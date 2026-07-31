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

## Generating apps with 3D models

Besides flat pixel art, the App Builder can generate wireframe models -- 3D shapes made of nodes and straight-line struts that spin on the display, drawn like a classic vector arcade game. See [3D Models](../studio/3d-models.md) for what a wireframe model is and how to build one by hand in Studio's 3D tab.

**What to ask for:** describe the shape as three-dimensional, rotating, or a wireframe, and the App Builder generates a model instead of flat art -- for example, "a spinning wireframe crystal" or "a 3D ship that flies across the screen." Ask for flat art (a character, an icon, a background) and you'll get a sprite instead.

**Spinning or facing a direction:** a generated model can turn in two ways. It can spin continuously in place, like a rotating trophy. Or its facing can follow your app's own logic -- for example, a ship that banks and turns to face the direction it's moving, the way a paper airplane leans into a turn, driven by whatever your app already tracks (steering input, velocity, and so on).

**Using a model you already built in Studio:** open the model in the [3D tab](../studio/3d-models.md#using-a-model-in-an-app) and choose **Try it in an app** -- it either starts you off with a small example app showing the model spinning, or, if your project already has app code, switches to Generate with a request already filled in to add that model to your app.

---

## See also

- [3D Models](../studio/3d-models.md) -- Build wireframe models in Studio's 3D tab
- [Browser Emulator](emulator.md) — Detailed emulator guide, controls, and troubleshooting
- [Apps](apps.md) — Built-in app catalog and how to add your own
- [Concepts](../concepts/index.md) — Framework reference for all hardware features
