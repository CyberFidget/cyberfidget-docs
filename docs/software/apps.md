# Apps

After this page you can choose a built-in app and add your own app from the studio.

Cyber Fidget ships with 29+ built-in apps spanning games, screensavers, tools, and code examples. All apps follow the same [begin/update/end lifecycle](../concepts/app-lifecycle.md). Built-in apps are registered in the firmware; the studio adds your own apps to the menu for you.

!!! tip "More apps in The Archives"
    Beyond the built-in apps, [The Archives](sharing-apps.md) has apps, screensavers and art made by other people. Try them in your browser and send the ones you like to your Fidget. Made something yourself? [Submit it to The Archives](submit-to-archives.md).

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
| **Ragdoll Fidgie** | Physics puppet that idles and breathes until you knock it over -- it tumbles with realistic physics, then picks itself back up | Slider: blend pose from crouch to stretch, any face button or a shake: go ragdoll |

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
| **Home Remote** | Controls lights, speakers, scenes and scripts through a Home Assistant server on your home network: favorites, rooms, brightness and colour, volume, play/pause and track skip. Set up over USB with the [`hr` commands](../reference/serial-commands.md#setting-up-home-remote) | Up/Down to choose; Enter opens a light or speaker, or runs a scene or script; hold Enter on a light, speaker, scene or script in a list to toggle the light, play or pause the speaker, or run the scene or script; Left/Right change the selected value; the slider sets brightness or volume; Back goes up a level and exits from the top list |
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
| **Image Demo 1-4** | Image loading and display techniques (4 variants) |
| **Button Counters** | Button press counting and event handling |
| **Time On Counter** | Elapsed time tracking |
| **Progress Bar** | Progress bar rendering |

---

## Adding your own app

Open **Code from Blank Template** in the [studio](../getting-started/first-app.md). It creates an app class with three methods: `begin()` sets up, `update()` draws about 50 times per second, and `end()` cleans up. A method is a function that belongs to a class.

Add this fragment into its `.cpp` file. Keep the starter's bottom-left exit button and its cleanup, including `setColorsOff()` in `begin()` and `end()`. The starter sets the font and alignment; this fragment clears its text and draws your greeting:

```cpp
// Insert inside update(), just above display.display();
display.clear();
display.drawString(64, 24, "Hello!");
```

Choose the Menu Category in the studio. You do not add an `APP_ENTRY` or edit `AppManifest.h` for a studio app. Built-in firmware registration is explained in [How an App Works](../concepts/app-lifecycle.md#the-app_entry-macro).

See [How an App Works](../concepts/app-lifecycle.md) for the full lifecycle pattern, and the [Concepts](../concepts/index.md) section for how to use buttons, display, audio, LEDs, slider, and accelerometer in your app.

!!! tip "Try it in the browser first"
    Use the [studio](https://cyberfidget.com/create/) to write and test apps in the browser emulator before installing them on your Cyber Fidget.
