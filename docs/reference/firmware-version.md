# Reading the firmware version

Every Cyber Fidget firmware build is uniquely identifiable. This page covers
how to read the version on a flashed device, how to write app code that
adapts to firmware version, and what the various build types mean.

## Why this matters

- **Verifying a flash succeeded.** "Did I actually flash what I think I
  flashed?" - connect serial, see the version, compare to what your build
  log printed. Match means you're running the right binary.
- **Filing actionable bug reports.** A reporter who sends their `info`
  output gives the exact commit hash, build type, and chip - reduces follow-up conversation.
- **Checking app compatibility.** Apps can declare a
  minimum firmware version; the App Builder UI reads the device's version
  and warns before flashing an incompatible app.

## On a device

### Boot banner

Every boot, the firmware prints a single line to USB serial (default at **921600
baud**) right after `Serial.begin()`:

```
[boot] fw=1.1.0+508ea44 type=release built=2026-04-29T18:42:11Z
```

If you connected your terminal after the device booted (so you missed the
banner), use the CLI commands below - same data, available any time.

### Serial CLI

Type a command + Enter. Make sure your terminal sends a newline (`\r\n` or
`\n`) when you press Enter; some terminals don't by default - check the
terminal's "send line ending" or "transmit CR+LF" setting. PlatformIO's
`pio device monitor -b 921600` works out of the box with the line ending dropdown set to `CRLF`

| Command   | Output                                                          |
|-----------|-----------------------------------------------------------------|
| `version` | One line: `[cmd] version=1.1.0+508ea44`                         |
| `info`    | Multi-line system state (firmware, type, hash, chip, MAC, uptime) |
| `help`    | Lists available commands                                        |

Commands are case-insensitive. Unknown commands return `[err] unknown
command: <input>`. Lines longer than 31 characters return `[err] line too
long` and the buffer resets.

Sample `info` output:

```
[cmd] info.fw=1.1.0+508ea44
[cmd] info.type=release
[cmd] info.built=2026-04-29T18:42:11Z
[cmd] info.git=508ea44
[cmd] info.dirty=0
[cmd] info.chip=ESP32-PICO-V3-02 rev 301
[cmd] info.mac=0C:05:A3:12:4B:00
[cmd] info.uptime_ms=4802
```

## Format

A version string looks like:

```
1.1.0+508ea44
1.1.0+508ea44-dirty
1.4.2+a1b2c3d
```

Anatomy:

- **`1.1.0`** - semantic version (`MAJOR.MINOR.PATCH`).
- **`+508ea44`** - short git commit hash of the source the firmware was
  built from. Always 7 hex characters. Use this to check out the exact
  source: `git checkout 508ea44`.
- **`-dirty`** *(when present)* - the build tree had uncommitted source
  changes. The binary is **not** reproducible from the public commit alone;
  ask the reporter for `git diff` against the hash if you're trying to
  reproduce a bug.

## Build types

`type=` tells you what kind of build produced this binary.

| Type         | Meaning                                                         |
|--------------|-----------------------------------------------------------------|
| `release`    | Built in CI from a published `vX.Y.Z` tag                       |
| `prerelease` | Built in CI from an `vX.Y.Z-rc1` / `-alpha` / `-beta` tag       |
| `ci-dev`     | CI build of a PR or non-tagged push                             |
| `dev`        | Local clean build                                               |
| `dirty`      | Local build with uncommitted source changes                     |
| `wasm`       | Browser emulator build                                          |
| `user-build` | App Builder per-user build (core firmware + your selected apps) |
| `unknown`    | Built without git access - no source-provenance audit trail     |
| anything else | A custom CI label set via `CYBERFIDGET_BUILD_TYPE_OVERRIDE`     |

If you see `type=unknown` on a release artifact, that's a bug - it means
the build environment didn't have git available and the commit hash
couldn't be embedded. File an issue.

## Comparing versions in your app

The firmware exposes preprocessor macros so user-app code can adapt to
different firmware versions at compile time:

```c
#include "version.h"

#if FW_VERSION >= VERSION_ENCODE(1, 4, 2)
    hal::newAudioApi(...);          // available since 1.4.2
#else
    hal::oldAudioApi(...);          // legacy fallback
#endif
```

`VERSION_ENCODE(major, minor, patch)` packs a semver triple into a single
`uint32_t` with bit layout `(major << 16) | (minor << 8) | patch`, so
ordinary integer comparison gives you semver ordering. `FW_VERSION` is the
encoded current version; `FW_VERSION_STRING` is the dotted string;
`FW_VERSION_FULL_STRING` adds the `+hash[-dirty]` suffix.

At runtime, the same values are available via `HAL`:

```cpp
#include "HAL.h"

uint32_t v = HAL::getFirmwareVersion();          // encoded
const char* s = HAL::getFirmwareVersionString(); // "1.1.0+508ea44"
const char* t = HAL::getFirmwareBuildType();     // "release", "dev", ...
```

## In the WASM emulator

The browser emulator exposes the same surface as JS-callable exports:

```js
// After loading the WASM module:
const version    = Module.ccall('cyberfidget_version_string', 'string', [], []);
const encoded    = Module.ccall('cyberfidget_version_encoded', 'number', [], []);
const buildType  = Module.ccall('cyberfidget_build_type', 'string', [], []);

console.log(`Emulator running firmware ${version} (${buildType})`);
```

App Builder uses these calls to compare an app's declared minimum firmware
against the emulator and against connected hardware before flashing.

## Test harness protocol contract

This section is for people building automated test harnesses, recording rigs,
or anything else that parses the firmware's serial output. The goal is to keep these stable and reliable.

### Line-prefix framing

Every line emitted by the firmware's identification surface (and the future
device-control mode it grows into) carries a category prefix:

| Prefix   | Meaning                                                       |
|----------|---------------------------------------------------------------|
| `[boot]` | One-shot boot banner, printed once at power-on / reset        |
| `[cmd]`  | Response to a CLI command                                     |
| `[err]`  | CLI errors (overflow, unknown command, malformed input)       |
| `[evt]`  | Reserved for the future event stream (button presses, app lifecycle, log subscriptions). Not emitted by today's firmware - but a harness should be ready to ignore lines with this prefix until the device-control-mode ticket lands. |

ESP_LOG output keeps its own format (`I (<timestamp>) <tag>: <message>`) and
is grep-distinguishable from the framed lines above.

### Key=value naming inside `[cmd]`

Multi-line command output uses dotted, lowercase keys with optional
underscore-separated unit suffixes:

- `[cmd] info.fw=1.1.0+508ea44`
- `[cmd] info.uptime_ms=12345`     ← `_ms` denotes milliseconds
- `[cmd] info.dirty=1`             ← raw boolean, no unit
- `[cmd] info.mac=AA:BB:CC:DD:EE:FF`

Convention: when a key carries a value with natural units (time, distance,
voltage, etc.), append the unit as a `_<unit>` suffix. Keys without units
imply a unit-free value (string, boolean, identifier).

### Forward compatibility

- New CLI commands may be added (`ota`, `app`, `button`, etc.). A harness
  that only handles `version` / `info` / `help` keeps working - unknown
  commands return `[err]` lines, which the harness can ignore.
- New `info.<key>` entries may be added. Parsers should treat `info` output
  as a key=value map, not a positional list.
- Line-prefix categories above are stable; new categories may be reserved
  in the future but won't reuse `[boot]` / `[cmd]` / `[err]` / `[evt]`.
- The `[boot]` banner format (`fw=...  type=...  built=...`) is stable.

### Stability guarantees

These are stable APIs the harness can pin against:

- `version` → exactly `[cmd] version=<full string>` followed by newline.
- `info` → multi-line `[cmd] info.<key>=<value>` block, one key per line, terminated when the firmware moves on.
- `help` → exactly one line beginning `[cmd] help=` listing comma-separated commands.
- Banner format on boot is the same string the build summary printed during compilation - character-for-character match is the design contract.

These are *not* yet stable and may change before T-002 lands:

- The exact set of keys returned by `info`. New keys may be added; existing keys won't be renamed without notice in the changelog.

## FAQ

**Why does my banner say `type=unknown`?**
The firmware was built on a machine without `git` on PATH, or from a source
tarball with no `.git` directory. Functional, but the binary can't be
traced back to a specific commit. Install git (or clone the repo properly)
and rebuild to get a real hash.

**Why does my banner say `-dirty`?**
The source tree had uncommitted modifications when the build ran. Common
during development; problematic for release artifacts. Commit your changes
and rebuild for a reproducible binary.

**My terminal opened too late and missed the boot banner.**
Type `version` + Enter at any time after boot. The CLI is always live.

**My terminal sends "version" but the device doesn't respond.**
Your terminal isn't sending a line ending. Check the terminal's settings
for "Send CR+LF on Enter" / "Append LF" / "Newline mode" and enable it.
PlatformIO's `pio device monitor` handles this automatically.

**Two different binaries report the same version string.**
Compare the `+hash` portion. If hashes match and neither is `-dirty`, the
binaries should be functionally identical (modulo build-time entropy like
commit-vs-clock timestamps).

**For Arduino IDE users.**
Arduino IDE doesn't have a clean pre-build hook. As a workaround, run
`python scripts/generate_version.py --standalone --out generated/version.h`
once before opening the sketch. Re-run after committing changes so the
embedded hash stays current.

**For ESP-IDF users (raw `idf.py`, no PlatformIO).**
Add a CMake pre-build target that invokes
`python scripts/generate_version.py --standalone --out generated/version.h`,
then `target_include_directories(... PRIVATE generated)` so includes
resolve. The same `version.h` is consumed identically.

**For external CI (Jenkins, GitLab CI, custom rigs).**
Set `CYBERFIDGET_BUILD_TYPE_OVERRIDE` in the build environment to brand
your artifacts (`jenkins-hil`, `ci-nightly`, etc.). The pre-build script
picks it up automatically. The GitHub Actions tag-vs-`version.txt`
assertion is YAML-specific; the equivalent in any other CI is three lines
of shell - match the tag's `MAJOR.MINOR.PATCH` against `version.txt` and
fail the build if they diverge.

---

*Internal: full design rationale at
[`cyberfidget-planning/tickets/T-001.md`](https://github.com/CyberFidget/cyberfidget-planning/blob/main/tickets/T-001.md)
(maintainers only).*
