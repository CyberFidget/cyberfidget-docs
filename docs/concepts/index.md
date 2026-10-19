# Concepts

After this page you can choose a guide for the input or output your app needs.

These guides explain the core concepts behind Cyber Fidget apps. Whether you're just curious or ready to dive into code, each page has something for you.

Start with **Code from Blank Template** in the [studio](../getting-started/first-app.md). Each code block says where to add its sections in the `.cpp` file. "At the top of the file" means below the `#include` lines, above the line that creates the app object. Keep the starter's methods; add a section inside them instead of adding another `begin()`, `update()` or `end()`. Each block works on its own.

Each concept page is written in layers:

1. **What is this?** -- A brief intro for beginners
2. **Concepts** -- Deeper explanation with analogies for curious users
3. **Code examples** -- Annotated snippets for tinkerers
4. **Framework details** -- Collapsed advanced notes for readers building apps into the firmware by hand

---

## Core concepts

| Concept | Description |
|---------|-------------|
| [How an App Works](app-lifecycle.md) | The begin -> update -> end lifecycle pattern |
| [The Update Loop](update-loop.md) | What runs 50 times per second and why |
| [Buttons & Events](buttons.md) | How button presses become actions via callbacks |
| [Drawing to the Screen](display.md) | The OLED display, coordinates, text, shapes, and bitmaps |
| [Sound & Music](audio.md) | Speaker tones, playback settings, and microphone input |
| [LEDs & Color](leds.md) | The 4 RGBW NeoPixels and color control |
| [The Slider](slider.md) | Analog slider input and filtered position values |
| [Motion Sensing](accelerometer.md) | Accelerometer axes and tilt-based control |

---

## Where to go next

- **New to the device?** Start with [How an App Works](app-lifecycle.md) to understand the app structure.
- **Want to understand the loop?** Read [The Update Loop](update-loop.md) next.
- **Building something?** Pick the concepts you need -- buttons, display, audio, LEDs, slider, or accelerometer.
- **Digging into the firmware?** Open the collapsed advanced notes under "Framework details" at the bottom of each concept page. Studio apps do not need these internals; the studio and firmware handle app registration and the update loop for you.
