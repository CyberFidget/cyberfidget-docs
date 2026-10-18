# Motion Sensing

After this page you can move a paddle and change a light by tilting the device.

The Cyber Fidget has an LIS2DH12 accelerometer that measures tilt and acceleration. Use it for tilt-controlled games, gesture detection, or any app that reacts to how the device is held.

---

## What is this?

An **accelerometer** measures acceleration (including gravity) along three axes. When the device is still, it mostly senses which way is "down" -- so you can infer tilt.

!!! tip "Like the tilt sensor in your phone"
    When you rotate your phone and the screen flips, that's the accelerometer. The Cyber Fidget uses the same idea: tilt the device and read X, Y, Z values to control your app.

---

## Three axes

| Axis | Direction | Typical use |
|------|-----------|-------------|
| **X** | Left-right tilt | Paddle movement, horizontal control |
| **Y** | Forward-backward tilt | Depth, forward/back |
| **Z** | Up-down | Vertical, "is it flat?" |

With the device still and flat, the Z reading has a magnitude near 1000 and X and Y are near zero. Values are in milli-g (mg): 1000 mg is one g, the acceleration due to gravity. The sign depends on orientation. A shake can produce larger readings.

---

## Global variables

The HAL updates these every 50 ms:

| Variable | Type | Description |
|----------|------|-------------|
| `accelX` | float | Left-right acceleration |
| `accelY` | float | Forward-backward acceleration |
| `accelZ` | float | Up-down acceleration |

The [studio starter](../getting-started/first-app.md) already includes `HAL.h` through its `.cpp` file. Paste the sections below where their comments say. In the emulator, use its tilt controls; test the feel on a device too.

---

## Code example: tilt-controlled paddle

```cpp
// Paste at the top of the file, below the #include lines
static float paddleX = 64.0f;

// Paste inside begin(), below setColorsOff();
paddleX = 64.0f;

// Paste inside update(), just above display.display();
paddleX += accelX * -0.002f;
// Keep the whole 40-pixel paddle on the screen.
if (paddleX < 20) paddleX = 20;
if (paddleX > 108) paddleX = 108;
display.clear();
display.fillRect((int)paddleX - 20, 56, 40, 4);
```

!!! note "Sign and scale"
    The readings are in milli-g: 1000 mg is one g. The example multiplies `accelX` by -0.002, so a reading of 1000 moves the paddle by -2 pixels per update. Adjust that factor to change the speed, or flip its sign to reverse the direction.

---

## Code example: tilt-to-color

```cpp
// Paste inside update(), just above display.display();
// Clamp first: a shake can exceed the range seen when tilting.
long x = constrain((long)accelX, -1000L, 1000L);
long y = constrain((long)accelY, -1000L, 1000L);
long z = constrain((long)accelZ, -1000L, 1000L);
uint8_t r = (uint8_t)map(x, -1000, 1000, 0, 255);
uint8_t g = (uint8_t)map(y, -1000, 1000, 0, 255);
uint8_t b = (uint8_t)map(z, -1000, 1000, 0, 255);
HAL::setRgbLed(pixel_Front_Top, r, g, b, 0);
```

---

## Code example: read the motion values

Show the readings on the screen to see how they change as you turn the device.

```cpp
// Paste at the top of the file, below the #include lines
#include <stdio.h>

// Paste inside update(), just above display.display();
display.clear();
display.setFont(ArialMT_Plain_10);
display.setTextAlignment(TEXT_ALIGN_LEFT);
char text[32];
snprintf(text, sizeof(text), "X %d  Y %d", (int)accelX, (int)accelY);
display.drawString(10, 16, text);
snprintf(text, sizeof(text), "Z %d mg", (int)accelZ);
display.drawString(10, 32, text);
```

---

## Framework details

??? info "Advanced: how the firmware reads motion"
    You do not need these details to build apps in the studio. They describe the firmware internals for readers writing an app by hand and building it into the firmware.

    ### LIS2DH12

    The accelerometer is an ST LIS2DH12, a 3-axis digital accelerometer. The firmware uses the SparkFun LIS2DH12 Arduino library for I2C communication.

    ### TASK_50MS update rate

    The HAL reads the accelerometer every **50 ms** (20 Hz) in its `TASK_50MS` block. `accelX`, `accelY`, and `accelZ` are updated from `s_accel.getX()`, `getY()`, and `getZ()`. For most tilt-based apps, 20 Hz is sufficient; studio apps read the supplied values rather than changing the sensor polling rate.

    ### Accessing the sensor directly

    Direct sensor access is part of firmware internals. Studio apps cannot call `HAL::accelerometer()` or configure sensor interrupts. Read `accelX`, `accelY` and `accelZ` instead.

## Functions on this page

--8<-- "includes/reference/accelerometer.md"
