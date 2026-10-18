# SPDX-License-Identifier: GPL-3.0-or-later
"""Extractor and source-layout checks; no compiler needed."""
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOL = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_examples", TOOL / "check_examples.py")
checker = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = checker
spec.loader.exec_module(checker)
FIXTURES = TOOL / "tests/fixtures"
TOP = "// Paste at the top of the file, below the #include lines\n"
BEGIN = "// Paste inside begin(), below setColorsOff();\n"
UPDATE = "// Paste inside update(), just above display.display();\n"
END = "// Paste inside end(), above unregisterButtonCallbacks();\n"


class ExampleTests(unittest.TestCase):
    def test_studio_incompatible_examples_fail_before_compilation(self):
        for code in (UPDATE + 'cf::gfx::drawSprite(display, sprite, 0, 0);',
                     TOP + '// cf::gfx::Actor is a full name',
                     TOP + 'const char* name = "cf::gfx::Actor";'):
            with self.subTest(code=code), patch.object(checker, 'materialize') as materialize:
                block = checker.Block('sprites.md', 3, code, 'cpp')
                result = checker.compile_block(block, None, None, False)
                self.assertEqual(result['kind'], 'studio-incompatible')
                self.assertEqual(result['result'], 'failed')
                self.assertIn('projects without art', result['message'])
                self.assertIn('using namespace cf::gfx;', result['message'])
                materialize.assert_not_called()

    def test_studio_rule_allows_short_names_and_explicit_skips(self):
        block = checker.Block('sprites.md', 3,
                              TOP + 'using namespace cf::gfx;\nActor player;', 'cpp')
        self.assertEqual(checker.classify(block), ('fragment:file', ''))
        block.code = 'cf::gfx::Actor player;'
        block.skip = 'requires project art'
        self.assertEqual(checker.classify(block), ('skipped', 'requires project art'))

    def test_untagged_studio_incompatible_example_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / 'sprites.md'
            page.write_text('```\ncf::gfx::Actor player;\n```\n', encoding='utf-8')
            blocks = checker.extract(page, root)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(checker.classify(blocks[0])[0], 'studio-incompatible')

    def blocks(self, name):
        return checker.extract(FIXTURES / name, FIXTURES)

    def test_fragment_slots_and_indentation(self):
        blocks = self.blocks("good.md")
        self.assertEqual([checker.classify(b)[0] for b in blocks],
                         ["fragment:update", "fragment:begin", "fragment:end", "fragment:file",
                      "fragment:file+begin+update"])
        self.assertEqual(blocks[0].line, 5)
        self.assertEqual(blocks[1].code.splitlines()[0], "// Paste inside begin(), below setColorsOff();")
        with tempfile.TemporaryDirectory() as folder:
            for block in blocks:
                checker.materialize(block, checker.classify(block)[0], Path(folder))
                cpp = (Path(folder) / "MyApp.cpp").read_text()
                sections = checker.fragment_sections(block.code)
                for _, _, code in sections:
                    self.assertIn(code, cpp)
                self.assertEqual(cpp.count("#line"), 2 * len(sections))

    def test_classification(self):
        blocks = self.blocks("classification.md")
        self.assertEqual([checker.classify(b)[0] for b in blocks],
                         ["skipped", "no-placement", "untagged", "no-placement", "no-placement",
                          "complete", "complete", "complete"])
        self.assertEqual(blocks[0].skip, "deliberate pseudocode")

    def test_complete_layouts_and_missing_instance(self):
        blocks = self.blocks("classification.md")
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            self.assertEqual(checker.materialize(blocks[-3], "complete", target), ("Example", "example"))
            self.assertEqual((target / "Example.cpp").read_text(), "")
            self.assertIn("Example example;", (target / "Example.h").read_text())
            self.assertEqual(checker.materialize(blocks[-2], "complete", target), ("SplitExample", "splitExample"))
            self.assertIn('#include "SplitExample.h"', (target / "SplitExample.cpp").read_text())
            self.assertNotIn("void SplitExample::begin", (target / "SplitExample.h").read_text())
            with self.assertRaisesRegex(ValueError, "global instance"):
                checker.materialize(blocks[-1], "complete", target)

    def test_conservative_untagged_heuristic(self):
        for text in ("Serial ready\n921600 baud", "root/\n  file.cpp", "+---+\n| d |\n+---+"):
            self.assertFalse(checker.looks_cpp(text))
        for text in ('#include "app.h"', "void draw() {}", "class App {", "d.clear();"):
            self.assertTrue(checker.looks_cpp(text))

    def test_markers_inside_raw_strings(self):
        for delimiter in ("", "tag", "long_tag"):
            with self.subTest(delimiter=delimiter):
                code = (TOP +
                        f'const char* text = u8R"{delimiter}(\n'
                        '// Paste inside begin()\n'
                        '/* a comment-looking string */\n'
                        f'){delimiter}";\n' +
                        UPDATE + 'display.clear();\n')
                sections = checker.fragment_sections(code)
                self.assertEqual([slot for slot, _, _ in sections], ["file", "update"])
                self.assertIn('// Paste inside begin()', sections[0][2])
                self.assertEqual(''.join(part for _, _, part in sections), code)
                self.assertEqual(checker.classify(self.block(code))[0], "fragment:file+update")

    def test_markers_inside_block_comments_and_after_close(self):
        code = (TOP + '/*\n'
                '// Paste inside end()\nR"fake(\n*/\n' +
                BEGIN + 'int value = 1;\n')
        sections = checker.fragment_sections(code)
        self.assertEqual([slot for slot, _, _ in sections], ["file", "begin"])
        self.assertEqual(sections[1][1], 5)
        self.assertEqual(''.join(part for _, _, part in sections), code)
        self.assertEqual(checker.classify(self.block(code))[0], "fragment:file+begin")

    def test_plain_assembly_preserves_embedded_canonical_markers(self):
        code = (TOP + 'const char* text = u8R"tag(\n' + BEGIN + ')tag";\n'
                '/*\n' + END + '*/\n' + UPDATE + 'display.clear();\n')
        files, _, _ = checker.assemble([self.block(code)], plain=True)
        cpp = files['MyApp.cpp']
        self.assertIn('u8R"tag(\n' + BEGIN + ')tag"', cpp)
        self.assertIn('/*\n' + END + '*/', cpp)
        self.assertNotIn(TOP, cpp)
        self.assertNotIn(UPDATE, cpp)

    def test_renaming_is_exact_and_does_not_cascade(self):
        original = ('MyApp myApp; MYAPP_H MyAppHelper myAppHelper MYAPP_HELPER '
                    '#include "MyApp.h" MyApp.cpp')
        for app in ('Catcher', 'UsemyApp', 'MyAppExtra'):
            with self.subTest(app=app):
                instance = app[0].lower() + app[1:]
                self.assertEqual(checker.renamed(original, app),
                    f'{app} {instance}; {app.upper()}_H MyAppHelper myAppHelper '
                    f'MYAPP_HELPER #include "{app}.h" {app}.cpp')
                files, _, actual_instance = checker.assemble([], app=app, plain=True)
                self.assertEqual(set(files), {app + '.h', app + '.cpp'})
                self.assertIn(f'#ifndef {app.upper()}_H', files[app + '.h'])
                self.assertIn(f'{app} {instance}(', files[app + '.cpp'])
                self.assertEqual(actual_instance, instance)

    def test_cpp_tokens_preserve_literals_and_operator_boundaries(self):
        tokens = checker.cpp_tokens
        self.assertEqual(tokens('x+=1; /* note */ y = 1e+2; // note\n'),
                         tokens('x += 1 ; y=1e+2;'))
        self.assertNotEqual(tokens('x += 1;'), tokens('x + = 1;'))
        self.assertNotEqual(tokens('float x = 1e+2;'), tokens('float x = 1e + 2;'))
        for literal in ('"Score %d  Lives %d"', "' '", 'u8R"tag(a  b\n// text)tag"'):
            with self.subTest(literal=literal):
                self.assertIn(literal, tokens('auto text = ' + literal + ';'))
        self.assertNotEqual(tokens('"/* keep */"'), tokens('"/*keep*/"'))

    def test_final_comparison_accepts_formatting_but_rejects_literal_changes(self):
        for original, changed in (('"Score %d  Lives %d"', '"Score %d Lives %d"'),
                                  ("' '", "'\\t'"),
                                  ('R"tag(a  b)tag"', 'R"tag(a b)tag"')):
            step = self.block(TOP + 'const auto text = ' + original + ';\n' +
                              UPDATE + 'int x = 0; x+=1;\n')
            files, _, _ = checker.assemble([step], app='Catcher', plain=True)
            listing = files['Catcher.cpp'].replace('x+=1', 'x += 1')
            block = checker.Block('page.md', 1, listing, 'cpp', final=True,
                                  cumulative=True, prior=[step])
            with self.subTest(literal=original), tempfile.TemporaryDirectory() as folder:
                checker.materialize_final(block, Path(folder))
                block.code = listing.replace(original, changed)
                with self.assertRaisesRegex(ValueError, 'final listing differs'):
                    checker.materialize_final(block, Path(folder))

    def test_comment_tokens_in_ordinary_strings(self):
        code = (TOP +
                'const char* text = "\\\"/* R\\\"tag(";\n'
                "const char quote = '\"'; // /*\n" +
                UPDATE + 'display.clear();\n')
        self.assertEqual([slot for slot, _, _ in checker.fragment_sections(code)], ["file", "update"])

    def block(self, code, line=10):
        return checker.Block("page.md", line, code, "cpp")

    def test_canonical_markers_come_from_slots(self):
        self.assertEqual(checker.MARKERS, {TOP.strip(): "file", BEGIN.strip(): "begin",
                                           UPDATE.strip(): "update", END.strip(): "end"})
        for marker, slot in checker.MARKERS.items():
            self.assertEqual(checker.classify(self.block(marker + "   \nint x = 1;\n")),
                             ("fragment:" + slot, ""))

    def test_bad_marker_names_the_canonical_text(self):
        for line, slot in (("// Paste inside update()", "update"),
                           ("// Paste inside begin(): set up.", "begin"),
                           ("// paste inside END()", "end"),
                           ("// Paste at the top of the file", "file"),
                           ("  // Paste inside update(), just above display.display();", "update")):
            with self.subTest(line=line):
                kind, message = checker.classify(self.block(line + "\nint x = 1;\n"))
                self.assertEqual(kind, "bad-marker")
                self.assertIn("line 10", message)
                self.assertIn('"' + checker.CONFIG["slots"][slot]["marker"] + '"', message)
        kind, message = checker.classify(self.block("// Paste this anywhere\nint x = 1;\n"))
        self.assertEqual(kind, "bad-marker")
        for marker in checker.MARKERS:
            self.assertIn(marker, message)

    def test_bad_marker_in_a_later_section(self):
        kind, message = checker.classify(self.block(TOP + "int x = 1;\n\n// Paste inside begin()\nx = 2;\n"))
        self.assertEqual(kind, "bad-marker")
        self.assertIn("line 13", message)
        self.assertIn(BEGIN.strip(), message)

    def test_cumulative_steps_apply_in_page_order(self):
        blocks = self.blocks("cumulative.md")
        kinds = [checker.classify(b)[0] for b in blocks]
        self.assertEqual(kinds, ["fragment:file+update", "fragment:file+begin+end", "skipped",
                                 "fragment:update", "complete", "final"])
        self.assertTrue(all(b.cumulative for b in blocks))
        self.assertEqual([len(b.prior) for b in blocks], [0, 1, 0, 2, 0, 3])
        self.assertEqual(blocks[3].prior, blocks[:2])
        with tempfile.TemporaryDirectory() as folder:
            checker.materialize(blocks[3], kinds[3], Path(folder))
            cpp = (Path(folder) / "MyApp.cpp").read_text()
        # Each step's code is in the file, later steps below earlier ones in the same slot.
        order = [cpp.index(text) for text in ("static int taps", "static void onTap",
                                              'drawString(0, 0, "Taps")', "drawProgressBar")]
        self.assertEqual(order, sorted(order))
        self.assertNotIn("this is not code", cpp)
        self.assertLess(cpp.index("registerCallback(button_MiddleRightIndex"), cpp.index("void MyApp::update"))
        self.assertLess(cpp.index("unregisterCallback(button_MiddleRightIndex"), cpp.index("    unregisterButtonCallbacks();"))
        # #line directives point each step at its own page line.
        self.assertIn('#line 6 "cumulative.md"', cpp)
        self.assertIn('#line 33 "cumulative.md"', cpp)

    def test_fragments_without_cumulative_marker_stand_alone(self):
        blocks = self.blocks("good.md")
        self.assertTrue(all(not b.cumulative and not b.prior for b in blocks))

    def test_final_listing_matches_starter_plus_steps(self):
        blocks = self.blocks("cumulative.md")
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(checker.materialize(blocks[-1], "final", Path(folder)), ("Tapper", "tapper"))
            self.assertIn("class Tapper", (Path(folder) / "Tapper.h").read_text())
            self.assertIn("#ifndef TAPPER_H", (Path(folder) / "Tapper.h").read_text())
            self.assertIn("drawProgressBar", (Path(folder) / "Tapper.cpp").read_text())

    def test_final_listing_drift_fails_with_a_diff(self):
        text = (FIXTURES / "cumulative.md").read_text(encoding="utf-8")
        listing = text[text.index("<!-- check-examples: final -->"):]
        with tempfile.TemporaryDirectory() as folder:
            page = Path(folder) / "drift.md"
            page.write_text(text.replace(listing, listing.replace("taps % 101", "taps % 50")), encoding="utf-8")
            block = checker.extract(page, Path(folder))[-1]
            self.assertEqual(checker.classify(block), ("final", ""))
            with self.assertRaises(ValueError) as caught:
                checker.materialize(block, "final", Path(folder))
        message = str(caught.exception)
        self.assertIn("final listing differs", message)
        self.assertIn("-101", message)
        self.assertIn("+50", message)

    def test_final_listing_needs_a_cumulative_page(self):
        block = checker.Block("page.md", 3, "void A::begin() {}\n", "cpp", final=True)
        kind, message = checker.classify(block)
        self.assertEqual(kind, "final")
        self.assertIn("cumulative", message)

    def test_starter_without_website_is_not_checked(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(checker.shutil, "which") as which:
            self.assertEqual(checker.check_studio_starter(Path(folder) / "absent"), "not checked (no website checkout)")
            which.assert_not_called()

    def test_starter_checkout_with_missing_generator_is_setup_error(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "website starter generator missing"):
                checker.check_studio_starter(Path(folder))

    def test_starter_renderer_missing_output_is_setup_error(self):
        with tempfile.TemporaryDirectory() as folder:
            website = Path(folder)
            generator = website / "assets/js/builder.js"
            generator.parent.mkdir(parents=True)
            generator.write_text("// generator fixture", encoding="utf-8")
            with patch.object(checker.shutil, "which", return_value="node"), \
                    patch.object(checker.subprocess, "run"):
                with self.assertRaisesRegex(ValueError, "renderer output missing.*MyApp.h"):
                    checker.check_studio_starter(website)

    def test_starter_setup_errors_exit_two(self):
        with tempfile.TemporaryDirectory() as folder:
            website = Path(folder)
            generator = website / "assets/js/builder.js"
            generator.parent.mkdir(parents=True)
            generator.write_text("// generator fixture", encoding="utf-8")
            for node, failure, message in (
                (None, None, "Node.js missing"),
                ("node", subprocess.CalledProcessError(1, ["node"], stderr="shape mismatch"), "shape mismatch"),
            ):
                with self.subTest(node=node), patch.object(checker.shutil, "which", return_value=node), \
                        patch.object(checker.subprocess, "run", side_effect=failure), \
                        patch.object(checker, "setup") as setup, \
                        patch.object(checker.sys, "stdout", io.StringIO()) as stdout, \
                        patch.object(checker.sys, "stderr", io.StringIO()) as stderr:
                    stdout.reconfigure = lambda **kwargs: None
                    stderr.reconfigure = lambda **kwargs: None
                    result = checker.main(["--website", str(website), "--docs-dir", str(website)])
                    self.assertEqual(result, 2)
                    self.assertIn("Setup error:", stderr.getvalue())
                    self.assertIn(message, stderr.getvalue())
                    if failure:
                        self.assertIn("regenerate it with: node tools/check-examples/studio/render_starter.js", stderr.getvalue())
                    setup.assert_not_called()


if __name__ == "__main__":
    unittest.main()
