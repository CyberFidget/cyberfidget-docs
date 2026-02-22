# LEDs & Color

The Cyber Fidget has 4 RGBW NeoPixel LEDs. Each can display millions of colors plus a dedicated white channel for brighter, more natural whites.

---

## What is this?

**RGBW** means each LED has four channels:

- **R** — Red (0–255)
- **G** — Green (0–255)
- **B** — Blue (0–255)
- **W** — White (0–255)

The white channel is separate from RGB. Mixing R+G+B gives a tinted white; the W channel gives pure white and is more efficient for brightness.

!!! tip "Why RGBW?"
    For "warm white" or "cool white" lighting, the W channel is brighter and uses less power than maxing R, G, and B.

---

## The 4 LED positions

| Index | Constant | Location |
|-------|----------|----------|
| 0 | `pixel_Back` | Back of device |
| 1 | `pixel_Front_Top` | Front, top |
| 2 | `pixel_Front_Middle` | Front, middle |
| 3 | `pixel_Front_Bottom` | Front, bottom |

Use these constants when setting individual LEDs. The strip order is GRBW (see framework details).

---

## Setting colors

You can use helper functions or set pixels directly:

```cpp
#include "HAL.h"
#include "RGBController.h"

// Set all LEDs to one color
setDeterminedColorsAll(255, 0, 0, 0);   // Red
setDeterminedColorsFront(0, 255, 0, 0);  // Green (front 3 only)
setColorsOff();                          // All off

// Set a single LED via HAL
HAL::setRgbLed(pixel_Front_Top, 255, 128, 0, 0);  // Orange

// Or use the strip directly (include HAL.h for strip())
Adafruit_NeoPixel& strip = HAL::strip();
strip.setPixelColor(pixel_Front_Middle, strip.Color(0, 0, 255, 50));
```

After changing colors, call `updateStrip()` so changes appear on the hardware.

---

## Code example: color cycling and reactive LEDs

```cpp
#include "HAL.h"
#include "RGBController.h"

void update() {
    // Rainbow cycle based on time (mapToRainbow expects 0–4095)
    int input = (millis() / 20) % 4096;
    uint8_t r, g, b;
    mapToRainbow(input, 128, r, g, b);
    setDeterminedColorsAll(r, g, b, 0);

    // Make front-top LED react to slider
    int brightness = map(sliderPosition_Percentage_Inverted_Filtered, 0, 100, 0, 255);
    HAL::setRgbLed(pixel_Front_Top, brightness, 0, brightness, 0);

    updateStrip();  // Push changes to hardware
}
```

!!! note "Call updateStrip()"
    The framework throttles LED updates (~60 fps). Call `updateStrip()` after changing colors; it only sends data when dirty and the throttle interval has passed.

---

## Framework details

### RGBController and SK6812

The LEDs are SK6812-compatible (often called "NeoPixel"). The strip uses **GRBW** color order: the library sends Green, Red, Blue, White in that order. `strip.Color(r, g, b, w)` and `HAL::setRgbLed(index, r, g, b, w)` handle this internally.

### updateStrip throttling

`updateStrip()` does not call `strip.show()` every time. It:

1. Marks the strip as dirty when you change pixels
2. Only calls `strip.show()` when dirty **and** at least ~17 ms have passed since the last show
3. Clears the dirty flag after showing

This reduces blocking and avoids flicker while keeping updates smooth.

### Helper functions

| Function | Description |
|----------|-------------|
| `initRGB()` | Initialize strip (called at boot) |
| `updateStrip()` | Push buffered colors to LEDs (throttled) |
| `setDeterminedColorsAll(r,g,b,w)` | Set all 4 LEDs |
| `setDeterminedColorsFront(r,g,b,w)` | Set front 3 LEDs |
| `setColorsOff()` | Turn all off |
| `rainbow(int wait)` | Animated rainbow |
| `mapToRainbow(input, dim, &r, &g, &b)` | Map 0–4095 to HSV rainbow |
