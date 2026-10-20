# Concepts

<div class="cf-hero" markdown>
<div class="cf-hero__media" markdown>

<video src="../assets/media/emulator-sprites.webm" poster="../assets/media/emulator-sprites.png" autoplay loop muted playsinline width="240" height="320"></video>

</div>
<div class="cf-hero__text" markdown>

<p class="cf-hero__lead"><strong>Draw on the screen, read the buttons and slider, play sounds and light the LEDs -- one guide for each part.</strong></p>

After this page you can choose a guide for the input or output your app needs.

These guides explain the core concepts behind Cyber Fidget apps. Whether you're just curious or ready to dive into code, each page has something for you.

*In the clip: a small face that the slider moves up and down and the middle buttons move sideways, from [Sprites & Animation](sprites.md).*

</div>
</div>

<div class="grid cards" markdown>

-   **New to apps? Start here**

    ---

    The begin, update and end pattern every app follows, and the loop that runs 50 times per second.

    [How an App Works](app-lifecycle.md) | [The Update Loop](update-loop.md)

-   **Look up a function**

    ---

    Every function your app can call, on one page, with its arguments and an example.

    [Function reference](../reference/functions.md)

-   **Pictures and motion**

    ---

    Show small pictures, animate them, move them around, or draw a spinning 3D shape.

    [Sprites & Animation](sprites.md) | [3D Models](3d-models.md)

-   **Write and test in the browser**

    ---

    Write or generate an app, build it, and try it in the emulator with no device needed.

    [App Builder](../software/ota-builder.md) | [Browser Emulator](../software/emulator.md)

</div>

Start with **Code from Blank Template** in the [studio](../getting-started/first-app.md). Each code block says where to add its sections in the `.cpp` file. "At the top of the file" means below the `#include` lines, above the line that creates the app object. Keep the starter's methods; add a section inside them instead of adding another `begin()`, `update()` or `end()`. Each block works on its own.

Each concept page is written in layers:

1. **What is this?** -- A brief intro for beginners
2. **Concepts** -- Deeper explanation with analogies for curious users
3. **Code examples** -- Annotated snippets for tinkerers
4. **Framework details** -- Visible Advanced notes for readers building apps into the firmware by hand

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
| [Sprites & Animation](sprites.md) | Pictures on the screen, animation, movement and collisions |
| [3D Models](3d-models.md) | Wireframe shapes you can spin, turn and resize |

---

## Where to go next

- **New to the device?** Start with [How an App Works](app-lifecycle.md) to understand the app structure.
- **Want to understand the loop?** Read [The Update Loop](update-loop.md) next.
- **Building something?** Pick the concepts you need -- buttons, display, audio, LEDs, slider, or accelerometer.
- **Digging into the firmware?** Read the Advanced section of each concept page. Studio apps do not need these internals; the studio and firmware handle app registration and the update loop for you.
