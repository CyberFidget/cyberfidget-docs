# Apps

Cyber Fidget ships with 28+ built-in apps spanning games, screensavers, tools, and code examples. All apps follow the same [begin/update/end lifecycle](../concepts/app-lifecycle.md) and are registered via `APP_ENTRY` macros in `AppManifest.h`.

---

## Games

| App | Description | Key controls |
|-----|-------------|--------------|
| **Breakout** | Classic brick-breaking game with tilt-controlled paddle | Accelerometer for paddle, Back to exit |
| **Dino Run** | Endless runner with jumping and ducking | Middle-Left: jump, Middle-Right: duck, slider: speed |
| **Simon Says** | LED + button memory pattern game with escalating difficulty | 4 directional buttons to match pattern |
| **Reaction Time** | Test your reaction time, press when the screen changes | Bottom right button to react, Back to return |
| **Stratagem** | Pattern match sequence input game | D-pad buttons (U/D/L/R), timed scoring |
| **Particle Sim** | SPH fluid physics simulation with gravity control | Accelerometer for gravity, slider: particle count |
| **Booper** | Musical tone generator / synth toy | All 6 buttons for notes, slider: volume |

---

## Screensavers

| App | Description |
|-----|-------------|
| **Matrix Screensaver** | Falling matrix-style characters with column state transitions, programmatically generated |
| **Boot Animation** | Startup animation displayed on power-on |
| **Graveyard** | Animated graveyard scene (25 frames), built with Pixel Sandbox |
| **Ghosts** | Animated ghost graveyard scene (52 frames), built with Pixel Sandbox |
| **Eye** | Animated eye blink sequence (17 frames), built with Pixel Sandbox |

---

## Tools

| App | Description | Key controls |
|-----|-------------|--------------|
| **Flashlight** | Uses LEDs and display as a flashlight | Back to exit |
| **Battery Level** | Shows battery state via MAX17048 fuel gauge | Back to exit |
| **Slider Status** | Displays slider ADC position with NeoPixel color feedback | Slider + Back |
| **Clock** | Time display with WiFi/NTP sync (fallback to internal timer) | Back to exit |
| **Power Manager** | Manually shutdown Cyber Fidget | Double-tap Bottom-Left for deep sleep |
| **WiFi Manager** | WiFi connection and web portal | Bottom-Left/Right to navigate |
| **Serial Display** | Scrollable view of incoming serial data | Scroll buttons, toggle scroll mode |
| **Accelerometer Demo** | Real-time raw accelerometer data with LED color feedback | Tilt device, Back to exit |

---

## Examples

These apps demonstrate individual framework features and are useful as starting points for your own apps:

| App | What it demonstrates |
|-----|---------------------|
| **Font Face Demo** | Font rendering options |
| **Text Flow Demo** | Text wrapping and flow |
| **Text Alignment Demo** | Text alignment modes |
| **Rect Demo** | Rectangle drawing primitives |
| **Circle Demo** | Circle drawing primitives |
| **Image Demo 1–4** | Image loading and display techniques (4 variants) |
| **Button Counters** | Button press counting and event handling |
| **Time On Counter** | Elapsed time tracking |
| **Progress Bar** | Progress bar rendering |

---

## Adding your own app

Every app is a class with three methods:

```cpp
void begin();   // Setup — runs once when app starts
void update();  // Main loop — runs 50 times per second
void end();     // Cleanup — runs once when app exits
```

Register your app with `APP_ENTRY` in `AppManifest.h` and it appears in the device menu automatically.

See [How an App Works](../concepts/app-lifecycle.md) for the full lifecycle pattern, and the [Concepts](../concepts/index.md) section for how to use buttons, display, audio, LEDs, slider, and accelerometer in your app.

!!! tip "Try it in the browser first"
    Use the [App Builder](https://cyberfidget.com/build) to write and test apps in the browser emulator before flashing to hardware.
