# Emulator Developer Guide

This document explains the WASM emulator architecture for contributors who want to fix bugs, add features, or understand how the pieces fit together. For user-facing how-to and troubleshooting, see [Browser Emulator](../software/emulator.md).

---

## Architecture Overview

The emulator compiles real Cyber Fidget C++ app code to WebAssembly using Emscripten. Instead of emulating the ESP32 CPU, it replaces the HAL with browser-native equivalents.

``` mermaid
flowchart TB
  subgraph Browser
    UI[emulator.js: Device mockup]
    Bridge[wasm_bridge.js: Glue]
    WASM[app.wasm + loader.js]
    UI <-->|events / framebuffer, LEDs| Bridge
    Bridge <-->|cwrap, callbacks| WASM
  end
  subgraph WASM_module
    App[App C++ code]
    HAL_WASM[HAL_WASM.cpp]
    Shims[Arduino.h, SSD1306Wire.h, NeoPixel, ...]
    App --> HAL_WASM
    HAL_WASM --> Shims
  end
```

### Data flow (one frame)

``` mermaid
sequenceDiagram
  participant User
  participant Emulator
  participant Bridge
  participant WASM

  User->>Emulator: Click button / move slider
  Emulator->>Bridge: onButtonEvent / onSliderChange
  Bridge->>WASM: wasm_button_press / wasm_set_slider
  Note over WASM: mainLoop: loopHardware, updateStrip, app.update()
  WASM->>Bridge: onFrameReady(framebuffer)
  WASM->>Bridge: onLedUpdate(index, r, g, b, w)
  WASM->>Bridge: onSerialOutput(text)
  Bridge->>Emulator: writeFramebuffer / setLED
  Bridge->>Emulator: Serial Monitor
```

1. **User input** → `emulator.js` fires `onButtonEvent` / `onSliderChange`
2. **Bridge** → `wasm_bridge.js` calls exported C functions (`wasm_button_press`, `wasm_set_slider`)
3. **App loop** → Emscripten's `emscripten_set_main_loop` calls `mainLoop()` at 50 FPS
4. **Display output** → `SSD1306Wire::display()` pushes framebuffer to JS via `EM_JS`
5. **LED output** → `HAL::loopHardware()` detects `needsShow` flag, calls `js_set_led()` via `EM_JS`
6. **Serial output** → `HardwareSerial::print()` routes to `js_serial_write()` via `EM_JS`

---

## Repository Layout

### Firmware Repo (`CyberFidget_Bundled_Demo_Platformio`)

```
wasm/
├── CMakeLists.txt          # Emscripten build config
├── main_wasm.cpp           # Entry point (main loop, exported C functions)
├── hal/
│   ├── HAL_WASM.cpp        # HAL namespace implementation for browser
│   ├── wasm_runtime.cpp    # NeoPixel ColorHSV, serial EM_JS bindings
│   ├── wasm_fonts.cpp      # Real OLED font data from ThingPulse
│   └── audio_wasm.cpp      # Web Audio tone generation
├── shims/
│   ├── Arduino.h           # millis, delay, String, Serial, PROGMEM, etc.
│   ├── SSD1306Wire.h       # OLED display with full drawing API
│   ├── Adafruit_NeoPixel.h # NeoPixel strip with WRGB Color() packing
│   ├── SparkFun_LIS2DH12.h # Accelerometer stub
│   └── ... (22 total shim headers)
└── app/                    # Generated at compile time for custom apps
    ├── app_include.h
    ├── MyApp.h
    └── MyApp.cpp
```

### Website Repo (`cyberfidget_website`)

```
assets/js/
├── emulator.js      # CyberFidgetEmulator class (DOM rendering)
├── wasm_bridge.js   # WasmBridge class (WASM ↔ emulator glue)
└── ai_builder.js    # App Builder integration (compile, cache, load)

build.html           # App Builder page with emulator panel
```

---

## Key Components

### `emulator.js` — Device Mockup

Renders an interactive device that mirrors the physical layout. Key methods:

- `writeFramebuffer(buffer)` — Accepts a flat `Uint8Array` (128×64 pixels, 1 byte per pixel) and renders to the OLED canvas
- `setLED(index, r, g, b, w)` — Updates LED indicator color with brightness boosting for dim values
- `setAllLEDsOff()` — Resets all LED indicators to the dim/off state
- `onButtonEvent` / `onSliderChange` — Callbacks wired by the bridge

**LED index mapping**: The firmware uses index 0 = back, 1 = front top, 2 = front middle, 3 = front bottom. The emulator maps these via `LED_INDEX_MAP = [3, 0, 1, 2]` to match the visual layout.

**Brightness floor**: LED values below brightness 50 are proportionally scaled up so they're visible on screen. Real NeoPixels emit visible light even at very low values; CSS backgrounds don't.

### `wasm_bridge.js` — WASM Glue

Two loading methods:

- `loadModule(url)` — Loads a pre-compiled `.js` loader from a URL (for demo/official apps)
- `loadFromBytes(jsText, wasmBinary)` — Loads from raw bytes (for custom-compiled apps)

Both methods:
1. Create a `<script>` tag to execute the Emscripten-generated JS loader
2. Call `CyberFidgetModule({...})` with callbacks for `onFrameReady`, `onLedUpdate`, `onSerialOutput`
3. Use `cwrap()` to bind exported C functions: `wasm_button_press`, `wasm_button_release`, `wasm_set_slider`, `wasm_set_accel`, `wasm_get_framebuffer`, `wasm_get_framebuffer_size`, `wasm_stop`
4. Wire emulator events to the WASM functions
5. Start the accelerometer feed (`_startAccelFeed()`): on devices with motion data, uses `DeviceMotionEvent`; otherwise uses mouse position vs window center as tilt and calls `wasm_set_accel`

The **volume slider and mute** in the emulator panel are output-only: they set `Module._emulatorMasterVolume` (0..1). The firmware’s `audio_wasm.cpp` multiplies the app’s tone volume by this value so users can mute or lower the browser output without changing the app’s idea of volume. The app’s own volume controls (e.g. in-app settings) are unchanged. `Module._audioPlaying` is set when a tone is playing so the UI can show a “sound active” indicator.

The `stop()` method calls `_wasm_stop()` (which internally calls `emscripten_cancel_main_loop`) and resets LEDs.

### `HAL_WASM.cpp` — Browser HAL

Implements the `HAL` namespace that all apps depend on:

- Uses `EM_JS` macros for JS interop (framebuffer push, LED updates, serial output)
- `loopHardware()` runs every frame: updates timing globals, processes button events, reads slider value from JS, pushes LED state when the strip's `needsShow` flag is set
- `updateStrip()` (from `RGBController.cpp`) must be called each frame to flush the dirty flag into `show()`
- **Accelerometer**: `getAccelerometerX/Y/Z()` return values set by the bridge via `wasm_set_accel(x, y, z)` (mouse position or `DeviceMotionEvent`)
- **Output volume**: The emulator panel sets `Module._emulatorMasterVolume` (0..1) in JS only; no WASM export. `audio_wasm.cpp` multiplies the app’s tone gain by this so users can mute or lower browser output. App volume (e.g. `AudioManager::setVolume()`) is unchanged.

### `Adafruit_NeoPixel.h` — NeoPixel Shim

**Critical detail**: The `Color()` function packs as WRGB to match the real Adafruit library:

```cpp
// Color(r=255, g=0, b=0, w=0) → 0x00FF0000
static uint32_t Color(uint8_t r, uint8_t g, uint8_t b, uint8_t w = 0) {
    return ((uint32_t)w << 24) | ((uint32_t)r << 16) | ((uint32_t)g << 8) | b;
}
```

`setPixelColor()` unpacks in the same WRGB order. `getLedRGBW()` returns the stored values directly.

### `main_wasm.cpp` — Entry Point

The main loop runs at 50 FPS via `emscripten_set_main_loop`:

```cpp
static void mainLoop() {
    HAL::loopHardware();  // timing, buttons, slider, LED push
    updateStrip();         // flush RGBController dirty flag → show()
    // ... button event dispatch ...
    APP_INSTANCE.update(); // the app's per-frame logic
}
```

Order matters: `loopHardware` pushes LED state set in the **previous** frame, `updateStrip` flushes the dirty flag for the **current** frame, and the app sets new state for the **next** frame.

---

## Custom App Compilation Flow

``` mermaid
flowchart LR
  A[User .h + .cpp] --> B[Base64 encode]
  B --> C[GitHub API: workflow_dispatch]
  C --> D[compile-wasm.yml]
  D --> E[Write wasm/app/, emcmake, build]
  E --> F[Upload artifacts]
  F --> G[Frontend: poll run, download ZIP]
  G --> H[JSZip: extract .js + .wasm]
  H --> I[IndexedDB cache]
  I --> J[loadFromBytes]
```

1. Frontend base64-encodes the `.h` and `.cpp` files
2. Triggers `workflow_dispatch` on the user's firmware fork via GitHub API
3. The `compile-wasm.yml` workflow:
   - Writes decoded files to `wasm/app/`
   - Generates `app_include.h`
   - Runs `emcmake cmake` with `-DWASM_APP=Custom -DCUSTOM_APP_NAME=...`
   - Uploads `cyberfidget.js` + `cyberfidget.wasm` as artifacts
4. Frontend polls the workflow run, downloads the artifact ZIP
5. Extracts `.js` and `.wasm` files using JSZip
6. Stores in IndexedDB (keyed by code hash) and loads via `loadFromBytes()`

---

## Bugs & Pitfalls Found During Development

These are documented here so future contributors don't repeat the same mistakes.

### 1. `Color()` byte order must match real Adafruit library
The real `Adafruit_NeoPixel::Color(r, g, b, w)` packs as **WRGB**: `(w<<24)|(r<<16)|(g<<8)|b`. Our original shim packed as RGBW which swapped every color channel. Always match the real library's format.

### 2. `updateStrip()` must be called every frame
`RGBController` uses a dirty-flag pattern: `markDirty()` sets a flag, `updateStrip()` checks it and calls `strip.show()`. Without calling `updateStrip()` in the main loop, `show()` never fires and LEDs never update.

### 3. `emscripten_cancel_main_loop` can't be directly exported
Emscripten internal functions can't appear in `EXPORTED_FUNCTIONS`. Solution: wrap it in a user-defined `wasm_stop()` function and export that instead.

### 4. `HEAPU8` is no longer a valid `EXPORTED_RUNTIME_METHODS` entry
Newer Emscripten versions expose `HEAPU8` automatically. Listing it causes a build warning/error.

### 5. Globals.cpp filename is case-sensitive on Linux
GitHub Actions runs Ubuntu. The file is `globals.cpp` (lowercase) but CMakeLists had `Globals.cpp`. Windows doesn't care; Linux does.

### 6. Low LED brightness values are invisible on screen
A NeoPixel at brightness 3/255 emits visible photons. CSS `rgb(0, 3, 0)` on a dark background is invisible. The emulator applies a minimum brightness floor of 50 to make all "on" LEDs visible.

### 7. LED index 0 is NOT the front-top LED
Physical wiring: index 0 = back LED, 1 = front top, 2 = front middle, 3 = front bottom. The emulator must remap indices to match the visual layout.

### 8. IndexedDB cache ignores firmware changes
The cache is keyed by app code hash. If you update the firmware shims/HAL but not the app code, the cached WASM is stale. The Compile button always forces a fresh build to handle this.

### 9. RGBController's `red()` and `green()` have swapped arguments
The firmware's `red()` calls `Color(0, 25, 0, 0)` which by Adafruit convention is actually green (r=0, g=25). This is likely compensating for a hardware channel swap on the PCB. The emulator reproduces whatever the firmware produces.

### 10. LEDs persist across app switches
When stopping one app and loading another, the LED DOM elements retain their last CSS style. `bridge.stop()` must call `emulator.setAllLEDsOff()`.

---

## Adding a New Built-In App to the Emulator

1. Add the app's library directory to `include_directories()` in `wasm/CMakeLists.txt`
2. Add an `elseif(WASM_APP STREQUAL "YourApp")` block with the appropriate source files
3. Add an `#elif defined(WASM_APP_YOURAPP)` block in `wasm/main_wasm.cpp`
4. Test locally: `emcmake cmake -S wasm -B wasm/build -DWASM_APP=YourApp && cmake --build wasm/build`

### Adding a New Shim

If an app pulls in a new ESP32 library:

1. Create a stub header in `wasm/shims/` with the same filename as the real library
2. Implement enough of the API for compilation to succeed (no-ops are fine for hardware-specific features)
3. If the library has actual logic needed at runtime, implement it in a `.cpp` under `wasm/hal/`

---

## Local Development (No GitHub Actions)

``` mermaid
flowchart LR
  subgraph Local
    Code[Your app or built-in]
    emcc[emcmake + cmake]
    Out[cyberfidget.js + .wasm]
    Code --> emcc --> Out
  end
  subgraph Run
    Server[python -m http.server]
    Browser[Browser loads from localhost]
    Out --> Server --> Browser
  end
```

### Prerequisites

- [Emscripten SDK](https://emscripten.org/docs/getting_started/downloads.html) — `emsdk install 3.1.51 && emsdk activate 3.1.51`
- CMake 3.13+
- Ninja (or make)
- Python 3 with `http.server` for local testing

### Build

```bash
cd CyberFidget_Bundled_Demo_Platformio
source emsdk/emsdk_env.sh  # or emsdk_env.bat on Windows

emcmake cmake -S wasm -B wasm/build -G Ninja -DWASM_APP=DinoGame
cmake --build wasm/build
```

### Test

```bash
cd wasm/build
python -m http.server 8080
# Open http://localhost:8080 and load cyberfidget.js from your test page
```

!!! warning "WASM files must be served over HTTP"
    Browsers block WASM loading from `file://` URLs due to CORS. Always use a local HTTP server.
