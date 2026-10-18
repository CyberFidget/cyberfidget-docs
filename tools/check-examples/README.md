<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Documentation example checker

This tool extracts C/C++ fenced examples from Markdown and checks them against the current firmware app headers. It invokes the firmware's `wasm/device_module/build_custom_device_app.sh` recipe directly; compiler flags and shim headers remain owned by that recipe. It validates compilation, not runtime behavior or hardware behavior.

## Prerequisites

- Python 3.9 or later; standard library only.
- Bash (Git Bash on Windows), available on PATH. Windows also checks `C:\Program Files\Git\bin\bash.exe`.
- An emsdk installation with Emscripten **3.1.51** activated. Put `emsdk` at the workspace root alongside the repositories, or set `EMSDK_ROOT` to its directory. The checker sources `emsdk_env.sh` in Bash, which configures the compiler, Node and Python environment. It uses the Python interpreter running the checker for the SDK launcher. An activated `em++` on PATH also works if no SDK directory is found.
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

Put the placement instruction on the **first line inside the fence**:

```cpp
// Paste inside update(). Draw a greeting.
display.drawString(0, 0, "Hello");
```

The supported method slots are `begin()`, `update()` and `end()`:

```cpp
// Paste inside begin()
setColorsOff();
```

```cpp
// Paste inside end()
setColorsOff();
```

For globals, constants, helpers or sprite data:

```cpp
// Paste at the top of the file: a constant.
static const int exampleValue = 42;
```

Placement instructions are case-insensitive and allow punctuation or explanatory words after the slot. Inside the starter, `display` and `buttonManager` are members of the app class, so fragments for `begin()`, `update()` and `end()` can use them directly. Code at the top of the file is outside the class: use `HAL::displayProxy()` and `HAL::buttonManager()` there.

One block can go to several places. Each later `// Paste ...` line starts a new section, so a button example can define its callback at the top of the file and register it inside `begin()`:

```cpp
// Paste at the top of the file
static bool lit = false;
static void onRightPressed(const ButtonEvent& e) {
    if (e.eventType == ButtonEvent_Pressed) lit = !lit;
}

// Paste inside begin()
HAL::buttonManager().registerCallback(button_RightIndex, onRightPressed);

// Paste inside update()
HAL::setRgbLed(pixel_Front_Middle, 0, 0, lit ? 255 : 0, 0);
```

Every block must compile on its own in the starter template. Blocks do not share state, declarations or imports with other blocks on the page, because a reader may copy just one.

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

An untagged fence that conservatively resembles C/C++ (for example `#include`, a `void` function, `HAL::`, or `display.clear();`) fails as `untagged`: tag it `cpp`, or `text` if it is not code. Explicit non-C/C++ language tags are ignored. A tagged example without a placement instruction or all three lifecycle methods fails as `no-placement`; the tool does not guess where to paste it.

## Replacing the starter

`starter/MyApp.h` and `starter/MyApp.cpp` are the studio's **Code from Blank Template** starter, exactly as the studio writes it for the default name `MyApp`. Fragments are checked against the same code a reader pastes into, so they carry no license header or slot markers. `starter/slots.json` specifies the class name, instance, source files, and each slot's target file, regex anchor and insertion position (`before` or `after`). Each anchor must match exactly once. The update slot is just above `display.display();`, so a fragment draws after the starter's own text and before the frame is shown. The begin slot is after the starter's own setup lines, the end slot is at the top of `end()`, and the file slot is just before the global app instance.

When a website checkout sits next to the docs checkout (or `--website PATH` points at one), the checker renders the studio's blank template with `node tools/check-examples/studio/render_starter.js` and fails if `starter/` no longer matches it, printing the command that regenerates it. Without a website checkout or Node, the summary says `Starter: not checked`.

If the starter's shape changes, regenerate the source files and update the anchors. No Python changes are needed. File names must match the configured app name for the firmware recipe. Markdown `#line` directives are added to generated copies so compiler diagnostics point to the page and source line.

## Output and exit codes

The table contains page path, first content line, kind (`complete`, `fragment:<slot>`, `skipped`, `untagged`, or `no-placement`) and result. Failures include their reason and up to 15 lines of compiler output. Totals include complete apps, fragments, skipped-with-marker, untagged, no-placement, passed and failed. Wall-clock seconds include setup and compilation. `--json PATH` writes the same records, full per-example compiler output, totals and elapsed seconds.

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
python tools/check-examples/check_examples.py --docs-dir tools/check-examples/tests/fixtures --page bad.md --keep
```

The first two commands must exit 0. The final command must exit 1 and identify `missingExampleSymbol` at `bad.md:6`. The classification fixture also contains deliberately failing examples and is intended for unit tests.

To retain the current documentation baseline:

```sh
python tools/check-examples/check_examples.py --keep --json tools/check-examples/.build/baseline.json > tools/check-examples/.build/baseline.txt 2>&1
```

Create `.build/` first if it does not exist, because the shell opens the output file before Python starts. Existing documentation may fail the authoring convention; a baseline records those failures without changing pages.
