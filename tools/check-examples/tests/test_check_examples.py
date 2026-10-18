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


class ExampleTests(unittest.TestCase):
    def blocks(self, name):
        return checker.extract(FIXTURES / name, FIXTURES)

    def test_fragment_slots_and_indentation(self):
        blocks = self.blocks("good.md")
        self.assertEqual([checker.classify(b)[0] for b in blocks],
                         ["fragment:update", "fragment:begin", "fragment:end", "fragment:file",
                      "fragment:file+begin+update"])
        self.assertEqual(blocks[0].line, 5)
        self.assertEqual(blocks[1].code.splitlines()[0], "// Paste inside BEGIN(): initialize state.")
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
                code = ('// Paste at the top of the file\n'
                        f'const char* text = u8R"{delimiter}(\n'
                        '// Paste inside begin()\n'
                        '/* a comment-looking string */\n'
                        f'){delimiter}";\n'
                        '// Paste inside update()\ndisplay.clear();\n')
                sections = checker.fragment_sections(code)
                self.assertEqual([slot for slot, _, _ in sections], ["file", "update"])
                self.assertIn('// Paste inside begin()', sections[0][2])
                self.assertEqual(''.join(part for _, _, part in sections), code)

    def test_markers_inside_block_comments_and_after_close(self):
        code = ('// Paste at the top of the file\n/*\n'
                '// Paste inside end()\nR"fake(\n*/\n'
                '// Paste inside begin()\nint value = 1;\n')
        sections = checker.fragment_sections(code)
        self.assertEqual([slot for slot, _, _ in sections], ["file", "begin"])
        self.assertEqual(sections[1][1], 5)
        self.assertEqual(''.join(part for _, _, part in sections), code)

    def test_comment_tokens_in_ordinary_strings(self):
        code = ('// Paste at the top of the file\n'
                'const char* text = "\\\"/* R\\\"tag(";\n'
                "const char quote = '\"'; // /*\n"
                '// Paste inside update()\ndisplay.clear();\n')
        self.assertEqual([slot for slot, _, _ in checker.fragment_sections(code)], ["file", "update"])

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
