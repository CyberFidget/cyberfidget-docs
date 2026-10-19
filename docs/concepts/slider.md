# The Slider

After this page you can use the slider to control a light and show its position.

The Cyber Fidget has an analog slider -- a physical control you can move from one end to the other. Your app reads its position as a number and uses it to control anything: brightness, speed, or selection. Studio apps on the device or in the browser emulator cannot change speaker volume with `setVolume()`; that setting is controlled outside the app.

---

## What is this?

The slider is a potentiometer, a variable resistor that changes voltage as you move it. The ESP32's ADC (Analog-to-Digital Converter) reads that voltage and turns it into a number you can use in code.

!!! tip "Like a dimmer switch"
    Think of a light dimmer: twist it one way, lights get brighter; twist the other, they dim. The slider works the same way -- it reads a position from one end to the other.

---

## Global variables

The hardware abstraction layer (HAL) reads the slider about every 20 ms and makes these values available to your app. Use the ones that fit your needs:

| Variable | Range | Use case |
|----------|-------|----------|
| `sliderPosition_Percentage_Filtered` | 0-100 (float) | Intuitive 0-100% |
| `sliderPosition_Percentage_Inverted_Filtered` | 0-100 (float) | Same, but direction flipped |
| `sliderPosition_8Bits_Filtered` | 0-255 (int) | Good for RGB/brightness |
| `sliderPosition_8Bits_Inverted_Filtered` | 0-255 (int) | Same, inverted |
| `sliderPosition_12Bits_Filtered` | 0-4095 (float) | Full ADC resolution |
| `sliderPosition_12Bits_Inverted_Filtered` | 0-4095 (float) | Same, inverted |

On the device, variables with `_Inverted_` read low with the slider at the bottom and high at the top: about 0 to 100%, 0 to 255, or 0 to 4095. The plain variables run the other way: high at the bottom, low at the top. The brightness example uses inverted values so moving the slider up makes the light brighter.

The studio emulator follows the same direction: moving the slider up increases the inverted values.

!!! note "Filtered vs raw"
    The "Filtered" variants are smoothed to reduce jitter. Prefer these for UI and control logic. Unfiltered readings such as `sliderPosition_12Bits` belong to firmware internals and are not available to studio apps.

---

## Code example: slider-controlled brightness

The slider can control volume inside built-in firmware apps. In studio apps on the device or in the browser emulator, `HAL::audioManager().setVolume()` has no effect. This example uses the same slider input for LED brightness instead, and shows the percentage on screen. Add it into the [studio starter](../getting-started/first-app.md).

```cpp
// Insert at the top of the file, below the #include lines
#include <stdio.h>

// Insert inside update(), just above display.display();
int brightness = sliderPosition_8Bits_Inverted_Filtered;
HAL::setRgbLed(pixel_Front_Top, brightness, 0, 0, 0);
display.clear();
display.setFont(ArialMT_Plain_16);
display.setTextAlignment(TEXT_ALIGN_CENTER);
char text[24];
snprintf(text, sizeof(text), "Slider: %d%%",
    (int)sliderPosition_Percentage_Inverted_Filtered);
display.drawString(64, 24, text);
```

---

## Functions on this page

--8<-- "includes/reference/slider.md"

## Kalman filtering

!!! advanced "Advanced: how slider readings are smoothed"
    You do not need these details to build apps in the studio; use the filtered variables above.

    The raw ADC readings jump around due to electrical noise. The framework applies a **Kalman filter** plus an **Exponential Moving Average (EMA)** on the percentage to smooth the signal. You get stable, responsive values without coding the math yourself.

---

## Framework details

!!! advanced "Advanced: how the firmware reads the slider"
    You do not need these details to build apps in the studio. They describe the firmware internals for readers writing an app by hand and building it into the firmware.

    ### ADC reading

    The slider is connected to **GPIO 35** (ADC1_CH7). The ESP32's 12-bit ADC yields values 0-4095. The HAL reads this in `sliderPositionRead()` and updates all derived variables.

    ### Filtering pipeline

    1. **Raw read** -- `analogRead()` -> 0-4095
    2. **Kalman filter** -- Smooths 12-bit value
    3. **Derived values** -- 8-bit = (12-bit / 4095) x 255; percentage = (12-bit / 4095) x 100
    4. **EMA on percentage** -- Reduces jitter in the 0-100% output

    ### Inverted variants

    The `*_Inverted_Filtered` values reverse the range: inverted percentage is 100 minus the ordinary percentage, and inverted 8-bit position is 255 minus the ordinary 8-bit position. Inverted 12-bit position is 4095 minus the ordinary position. On the device, inverted values increase from bottom to top; ordinary values decrease. Use an ordinary value when moving the slider up should reduce your app's setting.
