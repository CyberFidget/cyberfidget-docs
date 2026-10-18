<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Documentation example checker

This tool extracts C/C++ fenced examples from Markdown and checks them against the current firmware app headers. It invokes the firmware's `wasm/device_module/build_custom_device_app.sh` recipe directly; compiler flags and shim headers remain owned by that recipe. It validates compilation, not runtime behavior or hardware behavior.

## Prerequisites

- Python 3.9 or later; standard library only.
- Bash (Git Bash on Windows), available on PATH. Windows also checks `C:\Program Files\Git\bin\bash.exe`.
- An emsdk installation with Emscripten **3.1.51** activated. Put `emsdk` at the workspace root alongside the repositories, or set `EMSDK_ROOT` to its directory. The checker sources `emsdk_env.sh` in Bash, which configures the compiler, Node and Python environment. It uses the Python interpreter running the checker for the SDK launcher. An activated `em++` on PATH also works if no SDK directory is found.
- Node.js on PATH when a website checkout is present, to compare the starter with the studio. Missing Node.js is a setup error (exit 2). Only an absent website checkout reports the starter as not checked.
- A current firmware checkout containing the device-app recipe and its dependencies. The checker searches ancestors of the docs checkout for a sibling `cyberfidget-firmware` and `emsdk`, including checkouts inside `.worktrees/`. Use `--firmware` to select another checkout.

Run from the docs repository root:

```sh
python tools/check-examples/check_examples.py
python tools/check-examples/check_examples.py --page 'concepts/*.md' --jobs 4 --keep --json tools/check-examples/.build/results.json
python tools/check-examples/check_examples.py --firmware ../cyberfidget-firmware
```

`--page` matches a glob against page paths relative to the input directory. Quote globs so the shell does not expand them. `--docs-dir PATH` changes the input directory (default: this repository's `docs/`). Builds run in a thread pool; `--jobs N` defaults to the CPU count.

## Authoring examples

The checker considers fences tagged `cpp`, `c++`, `c`, `arduino` or `ino`, case-insensitively, including indented admonitions, lists and content tabs. Backtick and tilde fences are supported. Each example must state where to paste it, contain a complete app, or have an explicit skip reason.

### Fragments

Put the placement line on the **first line inside the fence**. It must be exactly one of these four lines (trailing spaces are allowed). Each one tells the reader where to paste, relative to a line that is already in the starter:

| Slot | Placement line |
|------|----------------|
| Top of the file | `// Paste at the top of the file, below the #include lines` |
| `begin()` | `// Paste inside begin(), below setColorsOff();` |
| `update()` | `// Paste inside update(), just above display.display();` |
| `end()` | `// Paste inside end(), above unregisterButtonCallbacks();` |

The exact text lives in `starter/slots.json` (each slot's `marker`). Put any extra explanation on its own comment line underneath:

```cpp
// Paste inside update(), just above display.display();
// Draw a greeting.
display.drawString(0, 0, "Hello");
```

Any other comment line that starts with `// Paste` where a placement line could go fails as `bad-marker`. The message quotes the exact text for the slot it seems to mean (or all four, when it cannot tell).

Top-of-file code holds globals, constants, helpers or sprite data. Inside the starter, `display` and `buttonManager` are members of the app class, so fragments for `begin()`, `update()` and `end()` can use them directly. Code at the top of the file is outside the class: use `HAL::displayProxy()` and `HAL::buttonManager()` there.

Placement-looking lines inside block comments or C++ raw strings stay part of their surrounding section. A real placement line after either closes starts a section.

One block can go to several places. Each later placement line outside a block comment or raw string starts a section, so a button example can define its callback at the top of the file and register it inside `begin()`:

```cpp
// Paste at the top of the file, below the #include lines
static bool lit = false;
static void onRightPressed(const ButtonEvent& e) {
    if (e.eventType == ButtonEvent_Pressed) lit = !lit;
}

// Paste inside begin(), below setColorsOff();
buttonManager.registerCallback(button_RightIndex, onRightPressed);

// Paste inside update(), just above display.display();
HAL::setRgbLed(pixel_Front_Middle, 0, 0, lit ? 255 : 0, 0);
```

On an ordinary page, every block must compile on its own in the starter template. Blocks do not share state, declarations or imports with other blocks on the page, because a reader may copy just one.

### Cumulative pages

A step-by-step tutorial builds one app across many blocks. Put this comment anywhere on the page:

```markdown
<!-- check-examples: cumulative -->
```

On that page, every fragment block applies on top of all earlier fragment blocks, in page order, in the same starter. Each step is compiled with everything before it, and a failing step is reported at its own page and line (compiler messages point at whichever step holds the bad line). Within a slot, a later step's code goes below the code earlier steps put there, so tell readers to paste each new part below what they added before. Skipped blocks do not accumulate. A complete-app block on a cumulative page is compiled on its own, as usual.

A cumulative page can end with the whole program. Put this comment immediately before its fence:

```markdown
<!-- check-examples: final -->
```

The checker rebuilds the starter plus every earlier step, as a reader's file would look (no placement lines), and compares it with the listing. Whitespace and blank lines are ignored, and the starter's class name, instance and include guard are renamed to the class the listing defines (from `ClassName::begin()`), so the listing can use the reader's app name. A listing with `// ClassName.h` and `// ClassName.cpp` parts is compared part by part; a listing without them is compared with the `.cpp` file. A difference fails with a diff. A matching listing is then compiled (with the renamed starter header when the listing has only the `.cpp`). A final marker on a page without the cumulative marker fails.

### Complete apps

A complete app has a class with `void begin()`, `void update()` and `void end()`, plus a defined global instance named by lowercasing the first letter of the class name (`Greeting greeting;`). An `extern` declaration alone is insufficient. The check reports missing instances because the copied app would not run.

A single-file block is written verbatim to `<ClassName>.h`, with a preceding diagnostic line directive, and an empty `<ClassName>.cpp`. The firmware glue includes the header exactly once, so out-of-class definitions and the global instance are not duplicated across translation units.

For separate header and source parts, use comment lines containing exactly `// ClassName.h` and `// ClassName.cpp`, in that order. The source part must include its header, and the header must declare the global instance for the glue:

```cpp
// Greeting.h
#pragma once
class Greeting {
public:
    void begin();
    void update();
    void end();
};
extern Greeting greeting;
// Greeting.cpp
#include "Greeting.h"
Greeting greeting;
void Greeting::begin() { setColorsOff(); }
void Greeting::update() { HAL::clearDisplay(); HAL::updateDisplay(); }
void Greeting::end() { setColorsOff(); }
```

### Explicit skips

Place this comment **immediately before** the opening fence, with a nonempty reason:

````markdown
<!-- check-examples: skip - pseudocode illustrating scheduling -->
```cpp
perform the next action;
```
````

Use skips for pseudocode, intentionally incorrect examples and firmware-source excerpts that are not standalone studio apps. Skipped blocks and their reasons appear in both output formats.

An untagged fence that conservatively resembles C/C++ (for example `#include`, a `void` function, `HAL::`, or `display.clear();`) fails as `untagged`: tag it `cpp`, or `text` if it is not code. Explicit non-C/C++ language tags are ignored. A tagged example without a placement line or all three lifecycle methods fails as `no-placement`; the tool does not guess where to paste it.

## Replacing the starter

`starter/MyApp.h` and `starter/MyApp.cpp` are the studio's **Code from Blank Template** starter, exactly as the studio writes it for the default name `MyApp`. Fragments are checked against the same code a reader pastes into, so they carry no license header or slot markers. `starter/slots.json` specifies the class name, instance, source files, and each slot's target file, regex anchor, insertion position (`before` or `after`) and canonical placement line (`marker`). Each anchor must match exactly once. The update slot is just above `display.display();`, so a fragment draws after the starter's own text and before the frame is shown. The begin slot is after the starter's own setup lines, the end slot is just above `unregisterButtonCallbacks();` at the top of `end()`, and the file slot is just before the global app instance (below the `#include` lines).

When a website checkout sits next to the docs checkout (or `--website PATH` points at one), the checker renders the studio's blank template with `node tools/check-examples/studio/render_starter.js` and reports a setup error (exit 2) if `starter/` differs, printing the command that regenerates it. A renderer failure prints its stderr and regeneration instructions. Missing Node.js is also a setup error. Only an absent website checkout produces `Starter: not checked`.

If the starter's shape changes, regenerate the source files and update the anchors. No Python changes are needed. File names must match the configured app name for the firmware recipe. Markdown `#line` directives are added to generated copies so compiler diagnostics point to the page and source line.

## Output and exit codes

The table contains page path, first content line, kind (`complete`, `fragment:<slot>`, `final`, `skipped`, `untagged`, `no-placement` or `bad-marker`) and result. Failures include their reason and up to 15 lines of compiler output. Totals include complete apps, fragments, skipped-with-marker, untagged, no-placement, bad-marker, final listings, passed and failed. Wall-clock seconds include setup and compilation. `--json PATH` writes the same records, full per-example compiler output, totals and elapsed seconds.

- Exit **0**: zero failures (skips are allowed).
- Exit **1**: compilation or example-convention failure.
- Exit **2**: setup failure, with instructions for fixing the environment.

Generated app sources, output modules and `compiler.txt` logs live in unique directories under `tools/check-examples/.build/`. These directories are removed after each compile unless `--keep` is supplied. The build directory is gitignored. Explicit JSON reports remain regardless of `--keep`.

## Verification

Extractor, classification and source-layout unit tests do not require a compiler:

```sh
python -m unittest discover -s tools/check-examples/tests -v
```

Fixtures remain outside `docs/`. To exercise the real compiler:

```sh
python tools/check-examples/check_examples.py --docs-dir tools/check-examples/tests/fixtures --page good.md --keep
python tools/check-examples/check_examples.py --docs-dir tools/check-examples/tests/fixtures --page complete.md --keep
python tools/check-examples/check_examples.py --docs-dir tools/check-examples/tests/fixtures --page cumulative.md --keep
python tools/check-examples/check_examples.py --docs-dir tools/check-examples/tests/fixtures --page bad.md --keep
```

The first three commands must exit 0; the third checks cumulative steps and a matching final listing. The final command must exit 1 and identify `missingExampleSymbol` at `bad.md:6`. The classification fixture also contains deliberately failing examples and is intended for unit tests.

To retain the current documentation baseline:

```sh
python tools/check-examples/check_examples.py --keep --json tools/check-examples/.build/baseline.json > tools/check-examples/.build/baseline.txt 2>&1
```

Create `.build/` first if it does not exist, because the shell opens the output file before Python starts. Existing documentation may fail the authoring convention; a baseline records those failures without changing pages.
