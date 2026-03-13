# App Builder

The [App Builder](https://cyberfidget.com/build) is a browser-based tool for writing, generating, and testing Cyber Fidget apps — no local setup required.

---

## What it does

1. **Write or generate** a C++ app using the code editor or build assistant
2. **Compile to WASM** — builds your app to WebAssembly via GitHub Actions to support emulator
3. **Run in the emulator** — test with on-screen buttons, slider, OLED, and LEDs
4. **Flash to hardware** — compile for the ESP32 and flash OTA or via USB

---

## Getting started

1. Go to [cyberfidget.com/build](https://cyberfidget.com/build)
2. Sign in with your GitHub account (required for compilation)
3. Write or generate your app code in the editor
4. Click **Compile Emulator** to build for the browser, then **Emulator** to run it
5. When ready, compile for hardware and flash to your device

---

## Compile vs Emulator

| Action | What it does | Speed |
|--------|-------------|-------|
| **Compile Emulator** | Builds C++ to WASM via GitHub Actions | ~1–2 min (first time, cached after) |
| **Emulator** | Loads the compiled WASM and runs it in the browser | Instant |

These are intentionally separate steps. Compilation is slow (cloud build), but the emulator loads instantly from the cached WASM in IndexedDB.

---

## Emulator features

The browser emulator maps all hardware to browser APIs:

- **Display** — 128x64 canvas matching the OLED
- **Buttons** — Keyboard shortcuts (Q/E/A/D/Z/C) or click on-screen
- **Slider** — Draggable slider control
- **LEDs** — Rendered as colored circles
- **Audio** — Web Audio API for tones
- **Serial Monitor** — Shows `Serial.println()` output

For full details, see the [Browser Emulator](emulator.md) page.

---

## App lifecycle

Every app follows the same pattern:

```cpp
void begin();   // Runs once when app starts
void update();  // Runs 50 times per second
void end();     // Runs once when app exits
```

See [How an App Works](../concepts/app-lifecycle.md) for the full lifecycle and [Concepts](../concepts/index.md) for how to use buttons, display, audio, LEDs, slider, and accelerometer.

---

## See also

- [Browser Emulator](emulator.md) — Detailed emulator guide, controls, and troubleshooting
- [Apps](apps.md) — Built-in app catalog and how to add your own
- [Concepts](../concepts/index.md) — Framework reference for all hardware features
