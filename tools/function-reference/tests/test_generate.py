# SPDX-License-Identifier: GPL-3.0-or-later
"""Run with python -m unittest discover -s tools/function-reference/tests -v."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOL = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('function_reference', TOOL / 'generate.py')
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)


class ReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.firmware = gen.find_firmware()
        cls.sidecar = (TOOL / 'reference.toml').read_text(encoding='utf-8')

    def check_sidecar(self, content):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'reference.toml'
            path.write_text(content, encoding='utf-8')
            result = subprocess.run([sys.executable, str(TOOL / 'generate.py'),
                                     '--firmware', str(self.firmware), '--check',
                                     '--sidecar', str(path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        return result.stderr

    def test_bogus_symbol_is_rejected(self):
        content = self.sidecar + '\n[symbols."HAL::imaginaryCall"]\nsection = "Screen"\nuse = "HAL::imaginaryCall();"\ndoes = "Test only."\nsee = "../concepts/display.md#text"\n'
        error = self.check_sidecar(content)
        self.assertIn('HAL::imaginaryCall is not in BOTH targets', error)
        self.assertIn('Remove its description or correct its qualified name', error)
        print('Bogus symbol rejected:', error.strip())

    def test_missing_real_description_is_rejected(self):
        start = self.sidecar.index('[symbols."HAL::setRgbLed"]')
        end = self.sidecar.index('\n[symbols.', start + 1)
        error = self.check_sidecar(self.sidecar[:start] + self.sidecar[end:])
        self.assertIn('HAL::setRgbLed is undescribed', error)
        self.assertIn('explicit ignore reason', error)
        print('Missing description rejected:', error.strip())

    def test_output_drift_is_rejected_without_writing(self):
        # Redirect outputs to a disposable root; never modify the real outputs.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / 'docs/reference/functions.md'
            page.parent.mkdir(parents=True)
            page.write_text('drift', encoding='utf-8')
            with patch.object(gen, 'ROOT', root), patch.object(gen, 'build',
                    return_value=('expected', '{}\n', {}, {}, {})):
                error, output = io.StringIO(), io.StringIO()
                with contextlib.redirect_stderr(error), contextlib.redirect_stdout(output):
                    code = gen.main(['--check', '--firmware', str(self.firmware)])
            self.assertEqual(code, 1)
            self.assertIn('functions.md differs', error.getvalue())
            self.assertIn('Run python tools/function-reference/generate.py', error.getvalue())
            self.assertEqual(page.read_text(encoding='utf-8'), 'drift')

    def test_links_and_anchors_are_validated(self):
        gen.validate_link('../concepts/display.md#text')
        with self.assertRaisesRegex(ValueError, 'has no heading anchor'):
            gen.validate_link('../concepts/display.md#imaginary-heading')
        with self.assertRaisesRegex(ValueError, 'has no page'):
            gen.validate_link('../concepts/imaginary-page.md')

    def test_explicit_no_guide_renders_dash_and_stays_out_of_concept_tables(self):
        page, symbols, _, _, includes = gen.build(self.firmware, TOOL / 'reference.toml')
        rows = json.loads(symbols)['symbols']
        without_guides = [row for row in rows if row['see'] == 'none']
        self.assertTrue(without_guides)
        self.assertTrue(any(row['kind'] == 'method' for row in without_guides))
        self.assertTrue(any(row['section'] in gen.TABLES for row in without_guides))
        for row in without_guides:
            anchor = 'symbol-' + re.sub(r'[^a-z0-9-]', '-', row['name'].lower())
            line = next(line for line in page.splitlines() if f'id="{anchor}"' in line)
            self.assertTrue(line.endswith(' - |'), line)
            self.assertNotIn('[Guide]', line)
            self.assertNotIn('[More]', line)
            for table in includes.values():
                self.assertNotIn(f'functions.md#{anchor})', table)
        self.assertNotIn('](none)', page)

    def test_missing_blank_or_invalid_guide_is_rejected(self):
        for replacement in ('', 'see = ""', 'see = "   "', 'see = false'):
            with self.subTest(replacement=replacement):
                content = self.sidecar.replace('see = "none"', replacement, 1)
                error = self.check_sidecar(content)
                self.assertIn('cf::gfx::RigActor::RigActor: add nonempty see', error)

    def test_no_guide_marker_does_not_allow_broken_links(self):
        content = self.sidecar.replace('see = "none"',
            'see = "../concepts/3d-models.md#imaginary-heading"', 1)
        self.assertIn('has no heading anchor', self.check_sidecar(content))

    def test_parser_preserves_overloads_visibility_and_lines(self):
        header = '''// hidden() is not a declaration.
#ifdef HOST_TEST
void testOnly();
#else
namespace HAL {
void added(int value);
void added(const char* value);
void hook(void (*callback)());
}
class DisplayProxy {
public:
    void visible(int x) { if (x) { x++; } }
    enum class Mode { OFF, ON = 4, AUTO };
    static const int index = 2;
private:
    void hidden();
};
extern float sensor;
class String {
public:
    void member();
    friend String operator+(const char* a, const String& b) { return b; }
};
#endif
'''
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'HAL.h'
            path.write_text(header, encoding='utf-8')
            rows = gen.parse_header(path, root)
        names = [row['name'] for row in rows]
        self.assertEqual(names.count('HAL::added'), 2)
        self.assertIn('HAL::hook', names)
        self.assertNotIn('testOnly', names)
        self.assertNotIn('DisplayProxy::hidden', names)
        self.assertNotIn('member', names)
        self.assertIn('operator+', names)
        self.assertEqual(next(row for row in rows if row['name'] == 'HAL::added')['line'], 6)
        self.assertEqual(next(row for row in rows if row['name'] == 'DisplayProxy::Mode::AUTO')['value'], '5')

    def test_outputs_match_and_provenance_is_complete(self):
        page, symbols, counts, only, includes = gen.build(self.firmware, TOOL / 'reference.toml')
        self.assertEqual((gen.ROOT / 'docs/reference/functions.md').read_text(encoding='utf-8'), page)
        self.assertEqual((gen.ROOT / 'docs/assets/reference/app-functions.json').read_text(encoding='utf-8'), symbols)
        payload = json.loads(symbols)
        self.assertEqual(counts['described'], len(payload['symbols']))
        for symbol in payload['symbols']:
            self.assertEqual(symbol['targets'], ['device', 'emulator'])
            self.assertEqual({row['target'] for row in symbol['declarations']}, {'device', 'emulator'})
            for row in symbol['declarations']:
                source_line = (self.firmware / row['header']).read_text(encoding='utf-8').splitlines()[row['line'] - 1]
                self.assertTrue(source_line.strip())

    def test_signatures_examples_defaults_overloads_and_types(self):
        page, symbols, _, _, includes = gen.build(self.firmware, TOOL / 'reference.toml')
        rows = {row['name']: row for row in json.loads(symbols)['symbols']}
        self.assertIn('## Reading the signatures', page)
        for term in ('uint8_t', 'int16_t', 'uint16_t', 'uint32_t', 'float', 'bool',
                     'const char*', 'String', 'nullptr'):
            self.assertIn('`' + term + '`', page)
        for name, text in (
                ('HAL::setRgbLed', 'void HAL::setRgbLed(int index, uint8_t r, uint8_t g, uint8_t b, uint8_t w)'),
                ('DisplayProxy::drawString', 'uint16_t display.drawString(int16_t x, int16_t y, const String& text)'),
                ('sliderPosition_8Bits_Filtered', 'int sliderPosition_8Bits_Filtered')):
            self.assertIn(text, gen.readable_signatures(rows[name]))
            self.assertIn('`' + text + '`<br><small>*Example:* `' + rows[name]['use'], page)
        self.assertGreater(len(gen.readable_signatures(rows['random'])), 1)
        self.assertTrue(any('= 0' in sig for sig in gen.readable_signatures(rows['AudioManager::playNote'])))
        self.assertTrue(gen.readable_signatures(rows['WHITE'])[0].startswith('OLEDDISPLAY_COLOR WHITE'))
        for row in rows.values():
            self.assertTrue(row['signature'])
            self.assertTrue(row['use'])
            for signature in gen.readable_signatures(row):
                self.assertIn('`' + signature.replace('|', '&#124;') + '`', page)
        self.assertIn('## Time and math', page)
        self.assertNotRegex('\n'.join(row['use'] for row in rows.values()), r'\bauto\b')
        for name in ('delay', 'delayMicroseconds'):
            self.assertIn('Does nothing on the device', rows[name]['does'])
            self.assertIn('use millis() timing', rows[name]['does'])
        self.assertIn('uint16_t display.drawString(', includes['includes/reference/display.md'])
        self.assertIn('<small>*Example:*', includes['includes/reference/display.md'])

    def test_concept_tables_match_destinations_and_reference_anchors(self):
        page, symbols, _, _, includes = gen.build(self.firmware, TOOL / 'reference.toml')
        rows = json.loads(symbols)['symbols']
        self.assertEqual(set(includes), {f'includes/reference/{p}.md' for p in gen.CONCEPT_PAGES})
        for concept in gen.CONCEPT_PAGES:
            path = f'includes/reference/{concept}.md'
            table = includes[path]
            self.assertEqual((gen.ROOT / path).read_text(encoding='utf-8'), table)
            self.assertIn('| Call | What it does |', table)
            self.assertNotIn('Learn more', table)
            expected = [row for row in rows if row['see'].partition('#')[0] == f'../concepts/{concept}.md']
            self.assertTrue(expected, concept)
            self.assertEqual(len(re.findall(r'^\| \[', table, re.M)), len(expected))
            for row in expected:
                self.assertIn(row['use'].replace('|', '&#124;'), table)
            for anchor in re.findall(r'functions\.md#([^)]+)', table):
                self.assertIn(f'id="{anchor}"', page)

    def test_missing_or_stale_include_fails_check_without_writing(self):
        for initial in (None, 'stale table'):
            with self.subTest(initial=initial), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for filename, content in [('docs/reference/functions.md', 'expected'),
                                          ('docs/assets/reference/app-functions.json', '{}\n')]:
                    path = root / filename
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content, encoding='utf-8')
                include = root / 'includes/reference/audio.md'
                if initial is not None:
                    include.parent.mkdir(parents=True)
                    include.write_text(initial, encoding='utf-8')
                with patch.object(gen, 'ROOT', root), patch.object(gen, 'build',
                        return_value=('expected', '{}\n', {}, {}, {'includes/reference/audio.md': 'current'})):
                    error, output = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stderr(error), contextlib.redirect_stdout(output):
                        code = gen.main(['--check', '--firmware', str(self.firmware)])
                self.assertEqual(code, 1)
                self.assertIn('reference/audio.md differs', error.getvalue().replace('\\', '/'))
                self.assertEqual(include.read_text(encoding='utf-8') if include.exists() else None, initial)

    def test_orphan_include_and_missing_snippet_fail_check_without_writing(self):
        for defect in ('orphan', 'missing-snippet', 'missing-page', 'valid'):
            with self.subTest(defect=defect), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                files = {'docs/reference/functions.md': 'expected',
                         'docs/assets/reference/app-functions.json': '{}\n',
                         'includes/reference/audio.md': 'current'}
                if defect != 'missing-page':
                    files['docs/concepts/audio.md'] = ('# Audio\n' if defect == 'missing-snippet'
                        else '# Audio\n\n--8<-- "includes/reference/audio.md"\n')
                if defect == 'orphan':
                    files['includes/reference/unpaired.md'] = 'orphan table'
                for filename, content in files.items():
                    path = root / filename
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content, encoding='utf-8')
                with patch.object(gen, 'ROOT', root), patch.object(gen, 'build',
                        return_value=('expected', '{}\n', {}, {}, {'includes/reference/audio.md': 'current'})):
                    error, output = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stderr(error), contextlib.redirect_stdout(output):
                        code = gen.main(['--check', '--firmware', str(self.firmware)])
                self.assertEqual(code, 0 if defect == 'valid' else 1)
                if defect == 'orphan':
                    self.assertIn('orphan include', error.getvalue())
                elif defect == 'missing-snippet':
                    self.assertIn('is missing --8<--', error.getvalue())
                elif defect == 'missing-page':
                    self.assertIn('has no concept page', error.getvalue())
                for filename, content in files.items():
                    self.assertEqual((root / filename).read_text(encoding='utf-8'), content)


if __name__ == '__main__':
    unittest.main()
