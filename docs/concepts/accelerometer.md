# Motion Sensing

The Cyber Fidget has an accelerometer that measures tilt and acceleration. Use it for tilt-controlled games, gesture detection, or any app that reacts to how the device is held.

---

## What is this?

An **accelerometer** measures acceleration (including gravity) along three axes. When the device is still, it mostly senses which way is "down" — so you can infer tilt.

!!! tip "Like the tilt sensor in your phone"
    When you rotate your phone and the screen flips, that's the accelerometer. The Cyber Fidget uses the same idea: tilt the device and read X, Y, Z values to control your app.

---

## Three axes

| Axis | Direction | Typical use |
|------|-----------|-------------|
| **X** | Left–right tilt | Paddle movement, horizontal control |
| **Y** | Forward–backward tilt | Depth, forward/back |
| **Z** | Up–down | Vertical, "is it flat?" |

When the device is flat (screen up), Z is near 1g (≈1000) and X, Y are near 0. Tilting changes the distribution. Values are in raw units (roughly ±1000–±1100 for 1g).

---

## Global variables

The HAL updates these every 50 ms:

| Variable | Type | Description |
|----------|------|-------------|
| `accelX` | float | Left–right acceleration |
| `accelY` | float | Forward–backward acceleration |
| `accelZ` | float | Up–down acceleration |

Include `HAL.h` (or `globals.h` which includes it) to use them.

---

## Code example: tilt-controlled paddle

```cpp
#include "HAL.h"
#include "globals.h"

float paddleX = 64.0f;  // Center of screen
const float paddleSpeed = 2.0f;

void update() {
    // Move paddle based on X tilt (negative factor for natural feel)
    paddleX += accelX * paddleSpeed * -0.01f;

    // Clamp to screen edges
    if (paddleX < 0) paddleX = 0;
    if (paddleX > 128) paddleX = 128;

    display.clear();
    display.fillRect((int)paddleX - 20, 56, 40, 4);  // Draw paddle
    display.display();
}
```

!!! note "Sign and scale"
    The sign of `accelX`/`accelY` depends on orientation. Multiply by a small factor (e.g. 0.01) and tweak until movement feels right. You may need to negate for intuitive control.

---

## Code example: tilt-to-color

```cpp
// Map X, Y, Z to RGB for a simple visual
uint8_t r = map(accelX, -1030, 1030, 0, 255);
uint8_t g = map(accelY, -1030, 1030, 0, 255);
uint8_t b = map(accelZ, -1030, 1030, 0, 255);
HAL::setRgbLed(pixel_Front_Top, r, g, b, 0);
updateStrip();
```

---

## Framework details

### LIS2DH12

The accelerometer is an ST LIS2DH12, a 3-axis digital accelerometer. The firmware uses the SparkFun LIS2DH12 Arduino library for I2C communication.

### TASK_50MS update rate

The HAL reads the accelerometer every **50 ms** (20 Hz) in its `TASK_50MS` block. `accelX`, `accelY`, and `accelZ` are updated from `s_accel.getX()`, `getY()`, and `getZ()`. For most tilt-based apps, 20 Hz is sufficient; for fast gestures you may want higher-rate polling if the hardware supports it.

### Accessing the sensor directly

For advanced use, get the sensor reference:

```cpp
SPARKFUN_LIS2DH12& accel = HAL::accelerometer();
// Use accel for raw config, interrupts, etc.
```
