# SPDX-License-Identifier: GPL-3.0-or-later
"""MkDocs hook: show the checker's assembled source after each fragment."""
import importlib.util
from pathlib import Path
import re
import sys

CHECKER_PATH = Path(__file__).resolve().parents[1] / 'check-examples/check_examples.py'
SPEC = importlib.util.spec_from_file_location('docs_example_checker', CHECKER_PATH)
checker = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = checker
SPEC.loader.exec_module(checker)


def solution(block, explain=False):
    highlights = {}
    files, _, _ = checker.assemble(block.prior + [block], plain=True, highlights=highlights)
    lines = ['', '??? example "Full code for this step"', '',
             '    This full code is for code name `MyApp` (create it with App Name "My App"); '
             'if your app has another code name, change `MyApp` and `myApp` to yours.', '']
    if explain:
        lines += ['    In the starter, `nullptr` means a pointer has no object. '
                  '`*` in a declaration marks a pointer (an address), and before a pointer reads its object. '
                  '`&` in a type refers to an existing object; before a value it gives its address. '
                  '`const` means the code cannot change the value through that declaration.', '']
    touched = {checker.CONFIG['slots'][slot]['file']
               for step in block.prior + [block]
               for slot, _, _ in checker.fragment_sections(step.code)}
    for name, source in files.items():
        if not name.endswith('.cpp') and name not in touched:
            continue
        marks = ' '.join(map(str, highlights[name]))
        fence = '`' * max(3, max((len(m[0]) + 1 for m in re.finditer(r'`+', source)), default=0))
        lines += [f'    {fence}cpp title="{name}" hl_lines="{marks}"']
        lines += ['    ' + line for line in source.splitlines()]
        lines += ['    ' + fence, '']
    return '\n'.join(block.indent + line if line else '' for line in lines) + '\n'


def transform(markdown, page):
    lines = markdown.splitlines(keepends=True)
    blocks = [block for block in checker.extract_text(markdown, page)
              if checker.classify(block)[0].startswith('fragment:')]
    for block in reversed(blocks):
        if not lines[block.end_line - 1].endswith('\n'):
            lines[block.end_line - 1] += '\n'
        lines.insert(block.end_line, solution(block, explain=block is blocks[0]))
    return ''.join(lines)


def on_page_markdown(markdown, page, config, files):
    return transform(markdown, page.file.src_uri)
