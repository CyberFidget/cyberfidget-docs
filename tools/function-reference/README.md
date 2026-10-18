<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# App function reference generator

Generates `docs/reference/functions.md`, a one-page app cheat sheet, `docs/assets/reference/app-functions.json`, a symbol list intended for editor autocomplete, and nine concept-page tables under `includes/reference/`. Requires Python 3.11+ and Git; uses only Python's standard library.

## Run

From the documentation repository root:

```sh
python tools/function-reference/generate.py
python tools/function-reference/generate.py --check
python tools/function-reference/generate.py --firmware ../cyberfidget-firmware
python tools/function-reference/generate.py --check --sidecar /path/to/reference.toml
python -m unittest discover -s tools/function-reference/tests -v
```

The default firmware search walks upward from this repository looking for a sibling `cyberfidget-firmware`, including when this checkout lives inside `.worktrees/`. No server, ports, environment variables, or third-party packages are needed. The firmware checkout is read-only; Git reads its HEAD with a process-local safe-directory override for that exact input checkout.

Exit 0 means generation or validation succeeded. Exit 1 means invalid descriptions, missing coverage, broken guide links/anchors, unreadable inputs, Git failure, or output drift during `--check`, including missing or stale concept includes. Argument errors exit 2. `--check` never writes output files. Compare against the checked-in outputs; regenerate and review all outputs before committing. The firmware revision is part of the JSON, so a changed HEAD requires regeneration even when its declarations are identical.

Each concept table contains the symbols whose `see` destination is that concept page, regardless of heading anchor, in sidecar order. Constants and readable globals are included once each. The two columns are Call and What it does; each call links to its symbol anchor in the full reference. Tables reuse the full reference's fixed layout and wrapping CSS for phone widths.

Concept pages embed their table with `--8<-- "includes/reference/audio.md"` (substitute the page name). `--check` rejects missing snippet lines, missing concept pages and orphan files in `includes/reference/`, as well as missing or stale outputs. The MkDocs snippets configuration uses `base_path: [!relative $config_dir]` to resolve paths from the repository root even when the command runs elsewhere. `check_paths: true` makes missing includes fail the build. The `includes/abbreviations.md` auto-append uses that same base path.

## Header scope

The device inputs are `wasm/device_module/shims/{HAL,DisplayProxy,ButtonManager,AudioManager,RGBController,globals,MenuManager,Arduino}.h`. Emulator resolution follows `wasm/shims/cf_custom_app.h` and `wasm/CMakeLists.txt`: same-named files in `wasm/shims` win, otherwise the corresponding `lib/` headers are used. Display enums and fonts come from the emulator's `SSD1306Wire.h` shim. Follow local includes from `lib/CFGraphics/include/cf_gfx.h` on both targets. Mesh and rig helpers are included because apps can draw wireframe models and connected-bone figures with them; icons are type aliases with no callable declarations.

A purpose-built brace walker extracts free functions (including friend operators), namespaces, public methods of DisplayProxy, ButtonManager, AudioManager, MenuManager, Actor, AnimationPlayer, MeshActor and RigActor, enums, constants, external globals and font handles. Inline implementation bodies and private methods are skipped structurally. `HOST_TEST` and `CF_TEST_CLI` branches are disabled. String/serial/driver class members, asset struct fields, macros, and standard-library APIs are outside this reference's extraction scope; `using std::min/max` are recorded because Arduino explicitly exposes them. This is not a general C++ parser; extend its tests and walker if the source adopts unsupported syntax.

Counts use qualified symbol names, with overloads grouped under one name. A description is permitted only for a name present in both targets. JSON `signature` contains the device declarations, joined with semicolons for overloads. `declarations` preserves each target's signatures with header, original line number and target, including differing argument names, return types and font representation. Constants retain source expressions; button aliases also resolve to their numeric index in the page. Header provenance lists all inspected headers. Target membership means a declaration exists, not that behavior is identical: the sidecar documents no-ops and target limits explicitly.

## Maintain descriptions

When `--check` names an undescribed symbol, inspect its declaration and implementation on both targets. Add an entry in reader order in `reference.toml`:

```toml
[symbols."HAL::setRgbLed"]
section = "LEDs"
use = "HAL::setRgbLed(pixel_Front_Middle, 0, 0, 255, 0);"
does = "Set one RGBW LED; channels each use 0-255."
see = "../concepts/leds.md#setting-colors"
```

Use one short call with the HAL accessors for display, buttons and audio. Explain units and target limits. Overloads share a description; their declarations are generated. Use an existing guide heading: every `see` page and heading anchor is checked, including during normal generation. The introductory first-app link is intentionally independent of sidecar validation because that guide can be authored separately.

For plumbing, add an explicit reason under `[ignore]`, for example `"ButtonManager::dispatch" = "Host event delivery; apps register callbacks instead."`. Each ignored name must exist in at least one input set, and reasons cannot be blank. Target-only declarations must also have explicit ignore entries. Do not silently hide a callable name in parser code. Described and ignored names cannot overlap. If a target-only name becomes shared, review its ignore reason and add a portable description when appropriate.

The tests use temporary sidecars to demonstrate rejection of a bogus symbol and a removed real description, plus output-drift rejection, anchor validation, parser visibility/overloads and provenance. They leave the real sidecar and generated outputs unchanged.
