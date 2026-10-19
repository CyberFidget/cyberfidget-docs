# LEDs & Color

After this page you can set each light and change its color with the slider.

Your app controls 4 SK6812 RGBW LEDs (NeoPixel-compatible), each with red, green, blue and white channels. The device also has a separate red-only LED under the front grill and a red charge indicator on the back. Studio apps cannot control the separate red LED, and the studio emulator does not show it. The emulator's colored glow under the grill shows the front-bottom RGBW LED (`pixel_Front_Bottom`).

---

## What is this?

**RGBW** means each LED has four channels:

- **R** -- Red (0-255)
- **G** -- Green (0-255)
- **B** -- Blue (0-255)
- **W** -- White (0-255)

The white channel is separate from red, green and blue. You can combine those three channels to make colors, or use the dedicated W channel for white light.

!!! tip "Why RGBW?"
    The W channel gives brighter white light and uses less power than maxing R, G and B. Mix it with red, green or blue to tint the result.

---

## The 4 LED positions

| Index | Constant | Location |
|-------|----------|----------|
| 0 | `pixel_Back` | Back of device |
| 1 | `pixel_Front_Top` | Front, top |
| 2 | `pixel_Front_Middle` | Front, middle |
| 3 | `pixel_Front_Bottom` | Front, bottom |

Use these constants when setting individual LEDs. The strip order is GRBW (see [firmware details](#framework-details)).

---

## Setting colors

Add each example into `update()` of the [studio starter](../getting-started/first-app.md), where its comment says. The starter calls `setColorsOff()` in `begin()` and `end()`, so every app starts and finishes with its lights off.

You can set all lights, the front three, or one pixel:

```cpp
// Insert inside update(), just above display.display();
// Arguments after the pixel index are red, green, blue, white (0-255).
setDeterminedColorsAll(255, 0, 0, 0);          // All four red.
setDeterminedColorsFront(0, 255, 0, 0);        // Front three green.
HAL::setRgbLed(pixel_Front_Top, 255, 128, 0, 0); // Top orange.
HAL::setRgbLed(pixel_Front_Middle, 0, 0, 255, 50); // Middle blue + white.
// Use setColorsOff() to turn all four off.
```

LED changes appear automatically. Studio apps do not need `updateStrip()`; that call does nothing in app code.

---

## Code example: color cycling and reactive LEDs

```cpp
// Insert inside update(), just above display.display();
// mapToRainbow takes a hue from 0 to 4095 and a brightness from 0 to 255.
int input = (millis() / 20) % 4096;
uint8_t r, g, b;
mapToRainbow(input, 128, r, g, b);
setDeterminedColorsAll(r, g, b, 0);

int brightness = sliderPosition_8Bits_Inverted_Filtered;
HAL::setRgbLed(pixel_Front_Top, brightness, 0, brightness, 0);
```

The inverted slider value is low at the bottom and high at the top of the device. Moving it up makes the top light brighter. See [The Slider](slider.md#global-variables) for both directions.

!!! note "Automatic light updates"
    Set the colors in `update()`. The firmware handles sending them to the LEDs. No extra call is needed.

---

## Functions on this page

--8<-- "includes/reference/leds.md"

## Framework details

!!! advanced "Advanced: how the firmware drives the LEDs"
    You do not need these details to build apps in the studio. They describe the firmware internals for readers writing an app by hand and building it into the firmware.

    ### RGBController and SK6812

    The LEDs are SK6812-compatible (often called "NeoPixel"). The strip uses **GRBW** color order: the library sends Green, Red, Blue, White in that order. `HAL::setRgbLed(index, r, g, b, w)` and the color helpers accept red, green, blue, white in that order. They handle the wiring order for you. Studio apps do not have access to `HAL::strip()` or `Adafruit_NeoPixel`.

    ### updateStrip throttling

    Inside the firmware, `updateStrip()` sends buffered colors to the lights. Color changes mark the buffer as dirty, meaning it needs sending. The firmware:

    1. Checks whether any color has changed
    2. Only calls `strip.show()` when dirty **and** at least 33 ms have passed since the last show (about 30 updates per second)
    3. Clears the dirty flag after showing

    This reduces blocking and avoids flicker while keeping updates smooth.

    ### Firmware-only helpers

    The LED functions your app can call are listed under [Functions on this page](#functions-on-this-page). These are used inside the firmware:

    | Function | Description |
    |----------|-------------|
    | `initRGB()` | Firmware only: initialize strip at boot |
    | `updateStrip()` | Does nothing in studio apps; firmware sends colors automatically |
    | `rainbow(int wait)` | Firmware only; studio apps can time colors with `millis()` |
