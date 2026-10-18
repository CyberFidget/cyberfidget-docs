# SPDX-License-Identifier: CC-BY-SA-4.0
"""Extractor and source-layout checks; no compiler needed."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()
