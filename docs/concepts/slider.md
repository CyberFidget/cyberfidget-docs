# The Slider

The Cyber Fidget has an analog slider — a physical control you can move from one end to the other. Your app reads its position as a number and uses it to control anything: volume, brightness, speed, or selection.

---

## What is this?

The slider is an analog potentiometer. As you move it, the voltage on a pin changes. The ESP32's ADC (Analog-to-Digital Converter) reads that voltage and turns it into a number you can use in code.

!!! tip "Like a dimmer switch"
    Think of a light dimmer: twist it one way, lights get brighter; twist the other, they dim. The slider works the same way — it reads a position from one end to the other.

---

## Global variables

The HAL updates these values every loop. Use the ones that fit your needs:

| Variable | Range | Use case |
|----------|-------|----------|
| `sliderPosition_Percentage_Filtered` | 0–100 (float) | Intuitive 0–100% |
| `sliderPosition_Percentage_Inverted_Filtered` | 0–100 (float) | Same, but direction flipped |
| `sliderPosition_8Bits_Filtered` | 0–255 (int) | Good for RGB/brightness |
| `sliderPosition_8Bits_Inverted_Filtered` | 0–255 (int) | Same, inverted |
| `sliderPosition_12Bits_Filtered` | 0–4095 (float) | Full ADC resolution |
| `sliderPosition_12Bits_Inverted_Filtered` | 0–4095 (float) | Same, inverted |

!!! note "Filtered vs raw"
    The "Filtered" variants are smoothed to reduce jitter. Prefer these for UI and control logic. Raw values (`sliderPosition_12Bits`, etc.) are also available if you need unfiltered readings.

---

## Kalman filtering

The raw ADC readings jump around due to electrical noise. The framework applies a **Kalman filter** plus an **Exponential Moving Average (EMA)** on the percentage to smooth the signal. You get stable, responsive values without coding the math yourself.

---

## Code example: slider-controlled volume

```cpp
#include "HAL.h"
#include "globals.h"

void update() {
    // Map slider 0–100% to volume 0.0–1.0
    float volume = sliderPosition_Percentage_Inverted_Filtered / 100.0f;
    HAL::audioManager().setVolume(volume);

    // Use 8-bit for LED brightness
    int brightness = sliderPosition_8Bits_Inverted_Filtered;
    HAL::setRgbLed(pixel_Front_Top, brightness, 0, 0, 0);
    updateStrip();

    // Display percentage on screen
    display.drawString(64, 20, "Slider: " + 
        String((int)sliderPosition_Percentage_Inverted_Filtered) + "%");
}
```

---

## Framework details

### ADC reading

The slider is connected to **GPIO 35** (ADC1_CH7). The ESP32's 12-bit ADC yields values 0–4095. The HAL reads this in `sliderPositionRead()` and updates all derived variables.

### Filtering pipeline

1. **Raw read** — `analogRead()` → 0–4095
2. **Kalman filter** — Smooths 12-bit value
3. **Derived values** — 8-bit = 12-bit >> 4; percentage = (12-bit / 4095) × 100
4. **EMA on percentage** — Reduces jitter in the 0–100% output

### Inverted variants

Some hardware builds wire the slider so "top" gives low voltage and "bottom" gives high (or vice versa). The `*_Inverted_Filtered` variables flip the range so 0% = one end and 100% = the other, regardless of wiring.
