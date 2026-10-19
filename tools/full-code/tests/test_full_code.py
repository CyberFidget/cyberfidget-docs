# SPDX-License-Identifier: GPL-3.0-or-later
"""Check generated solutions against the compiler's fragment materialization."""
import importlib.util
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('full_code', Path(__file__).resolve().parents[1] / 'full_code.py')
hook = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(hook)
checker = hook.checker
TOP = checker.CONFIG['slots']['file']['marker']
UPDATE = checker.CONFIG['slots']['update']['marker']


def fragment(code, fence='```cpp'):
    return fence + '\n' + code + '\n' + fence[:3] + '\n'


class FullCodeTests(unittest.TestCase):
    def solutions(self, text):
        return text.split('??? example "Full code for this step"')[1:]

    def test_independent_fragments_and_exact_compiled_tokens(self):
        markdown = fragment(TOP + '\nstatic int score = 7;\n' + UPDATE + '\ndisplay.clear();')
        markdown += '\n' + fragment(UPDATE + '\ndisplay.drawString(64, 24, "Hi");')
        output = hook.transform(markdown, 'concepts/test.md')
        boxes = self.solutions(output)
        self.assertEqual(len(boxes), 2)
        self.assertNotIn('static int score', boxes[1])
        for block, box in zip(checker.extract_text(markdown, 'concepts/test.md'), boxes):
            source = re.search(r'    ```cpp[^\n]*\n(.*?)    ```', box, re.S)[1]
            source = '\n'.join(line[4:] for line in source.splitlines())
            with tempfile.TemporaryDirectory() as directory:
                checker.materialize(block, checker.classify(block)[0], Path(directory))
                compiled = (Path(directory) / 'MyApp.cpp').read_text(encoding='utf-8')
            compiled = re.sub(r'^#line[^\n]*\n', '', compiled, flags=re.M)
            self.assertEqual(checker.cpp_tokens(source), checker.cpp_tokens(compiled))
            assembled, _, _ = checker.assemble(block.prior + [block], plain=True)
            self.assertEqual(source + '\n', assembled['MyApp.cpp'])
            marks = list(map(int, re.search(r'hl_lines="([\d ]+)"', box)[1].split()))
            highlighted = [source.splitlines()[n - 1] for n in marks]
            self.assertTrue(highlighted)
            self.assertTrue(all(line.strip() in block.code for line in highlighted))
        self.assertIn('App Name "My App"', output)
        self.assertIn('change `MyApp` and `myApp`', output)

    def test_cumulative_steps_and_only_latest_highlights(self):
        markdown = '<!-- check-examples: cumulative -->\n'
        markdown += fragment(TOP + '\nstatic int score = 7;')
        markdown += fragment(UPDATE + '\nscore += 1;')
        box = self.solutions(hook.transform(markdown, 'tutorial.md'))[1]
        self.assertIn('static int score = 7;', box)
        self.assertIn('score += 1;', box)
        block = checker.extract_text(markdown, 'tutorial.md')[1]
        marks = {}
        files, _, _ = checker.assemble(block.prior + [block], plain=True, highlights=marks)
        self.assertEqual([files['MyApp.cpp'].splitlines()[n-1] for n in marks['MyApp.cpp']], ['    score += 1;'])

    def test_final_listing_names_every_step_for_the_same_app(self):
        markdown = '<!-- check-examples: cumulative -->\n'
        markdown += fragment(UPDATE + '\ndisplay.clear();')
        markdown += '<!-- check-examples: final -->\n' + fragment('void Catcher::begin() {}')
        box = self.solutions(hook.transform(markdown, 'tutorial.md'))[0]
        self.assertIn('title="Catcher.cpp"', box)
        self.assertIn('Catcher catcher(HAL::buttonManager());', box)
        self.assertIn('code name `Catcher` (create it with App Name "Catcher")', box)
        self.assertIn('change `Catcher` and `catcher`', box)
        self.assertNotIn('MyApp', box)

    def test_slot_indentation_and_raw_string_contents(self):
        begin = checker.CONFIG['slots']['begin']['marker']
        end = checker.CONFIG['slots']['end']['marker']
        code = TOP + '\nstatic int score = 0;\n'
        code += begin + '\nscore = 1;\n'
        code += UPDATE + '\nif (score) {\n    score++;\n}\n'
        code += 'const char* text = R"tag(\n  exact spaces\n\n)tag";\n'
        code += end + '\nscore = 0;'
        block = checker.extract_text(fragment(code), 'test.md')[0]
        files, _, _ = checker.assemble([block], plain=True)
        source = files['MyApp.cpp']
        self.assertIn('\nstatic int score = 0;\n', source)
        self.assertIn('    setColorsOff();\n    score = 1;\n}', source)
        self.assertIn('    if (score) {\n        score++;\n    }', source)
        self.assertIn('    score = 0;\n    unregisterButtonCallbacks();', source)
        self.assertIn('R"tag(\n  exact spaces\n\n)tag"', source)
        self.assertNotIn('\n\n}', source)
        with tempfile.TemporaryDirectory() as directory:
            checker.materialize(block, checker.classify(block)[0], Path(directory))
            compiled = (Path(directory) / 'MyApp.cpp').read_text(encoding='utf-8')
        compiled = re.sub(r'^#line[^\n]*\n', '', compiled, flags=re.M)
        self.assertEqual(checker.cpp_tokens(source), checker.cpp_tokens(compiled))

    def test_skip_complete_invalid_and_final_are_unchanged(self):
        complete = (checker.TOOL / 'tests/fixtures/complete.md').read_text(encoding='utf-8')
        for markdown in (complete, '<!-- check-examples: skip - pseudocode -->\n' + fragment('void pretend();'),
                         fragment('// Insert somewhere\nint x;'), fragment('int x;')):
            with self.subTest(markdown=markdown):
                self.assertEqual(hook.transform(markdown, 'test.md'), markdown)
        cumulative = (checker.TOOL / 'tests/fixtures/cumulative.md').read_text(encoding='utf-8')
        expected = sum(checker.classify(b)[0].startswith('fragment:') for b in checker.extract_text(cumulative, 'test.md'))
        self.assertEqual(len(self.solutions(hook.transform(cumulative, 'test.md'))), expected)

    def test_indented_tilde_fence_preserves_context_and_following_text(self):
        markdown = '!!! note\n\n' + '\n'.join('    ' + line for line in fragment(UPDATE + '\ndisplay.clear();', '~~~C++').splitlines()) + '\n\nAfter.\n'
        output = hook.transform(markdown, 'test.md')
        self.assertIn('    ??? example', output)
        self.assertIn('        ```cpp title="MyApp.cpp"', output)
        self.assertTrue(output.endswith('\nAfter.\n'))

    def test_header_is_included_when_slot_touches_it(self):
        slots = {**checker.CONFIG['slots'], 'file': {'file': 'MyApp.h', 'anchor': '^#endif', 'position': 'before', 'marker': TOP}}
        with patch.dict(checker.CONFIG, slots=slots):
            output = hook.transform(fragment(TOP + '\nstatic int score;'), 'test.md')
        self.assertIn('title="MyApp.h"', output)
        self.assertIn('title="MyApp.cpp"', output)

    def test_embedded_marker_and_backticks_are_preserved(self):
        code = TOP + '\nconst char* text = R"tag(\n' + UPDATE + '\n````\n)tag";'
        output = hook.transform(fragment(code, '~~~cpp'), 'test.md')
        box = self.solutions(output)[0]
        self.assertIn('    `````cpp title="MyApp.cpp"', box)
        self.assertIn('    ' + UPDATE, box)

    def test_no_trailing_newline_and_adjacent_blocks(self):
        first = fragment(UPDATE + '\ndisplay.clear();')
        last = fragment(UPDATE + '\ndisplay.fillCircle(64, 32, 3);').rstrip('\n')
        output = hook.transform(first + last, 'test.md')
        self.assertEqual(len(self.solutions(output)), 2)
        self.assertIn('```\n\n??? example', output)
        self.assertEqual(output.count('In the starter, `nullptr`'), 1)

    def test_hook_works_in_isolated_repo_without_sdk_or_firmware(self):
        tool = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in ('full-code/full_code.py', 'check-examples/check_examples.py',
                             'check-examples/starter/MyApp.h', 'check-examples/starter/MyApp.cpp',
                             'check-examples/starter/slots.json'):
                destination = root / 'tools' / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(tool.parent / relative, destination)
            script = ('import runpy; '
                      'hook = runpy.run_path("tools/full-code/full_code.py"); '
                      'output = hook["transform"](' + repr(fragment(UPDATE + '\ndisplay.clear();')) + ', "page.md"); '
                      'assert "Full code for this step" in output; '
                      'assert "MyApp.cpp" in output')
            result = subprocess.run([sys.executable, '-I', '-c', script], cwd=root,
                                    capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
