<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Full-code solutions

MkDocs loads `full_code.py` through `hooks` in `mkdocs.yml`. It adds a collapsed
"Full code for this step" box immediately after each valid C++ fragment. Source
Markdown stays unchanged. Skipped blocks and complete apps get no box.

The hook imports extraction, classification and starter assembly from
`tools/check-examples/check_examples.py`. Ordinary pages use a fresh starter;
cumulative pages include all earlier steps. Only the current step is highlighted.
The complete source is shown, plus the header if an accumulated fragment changes it.
Compiler copies add diagnostic directives and placement comments; the solution uses
the same assembly with `plain=True`, without those annotations.

The build needs only Python and the checked-in starter, with no compiler, firmware
checkout, server, ports or environment variables. Run checks from the repo root:

```sh
python -m unittest discover -s tools/full-code/tests
python -m mkdocs build --strict --clean
```

For optional desktop and 390 px browser checks, use Node.js, Playwright, and an
installed Chrome. Pass the built site, an output directory for PNGs and the JSON
report, and a package.json in an existing project that has Playwright installed:

```sh
node tools/full-code/verify_render.cjs SITE OUTPUT /path/to/project/package.json
```

The script starts a local static server on an unused port and closes it when
finished. External requests are blocked. `CF_CHROMIUM_EXECUTABLE_PATH` selects
Chrome; the default is the Windows system installation under Program Files.
It checks that Advanced content is visible, solution boxes are collapsed and
highlighted when opened, signatures include types and examples, and the tested
pages fit both viewports without horizontal page scrolling.
