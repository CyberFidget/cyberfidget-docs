# The Update Loop

After this page you can animate your app with elapsed-time checks.

The Cyber Fidget firmware runs your app's `update()` function about 50 times per second. Understanding what happens in each "frame" and how timing works will help you build smooth, responsive apps.

---

## What is this?

The main loop runs continuously. Roughly every 20 milliseconds, the firmware:

1. Updates hardware (buttons, battery, slider, etc.)
2. Processes any button events
3. Calls your app's `update()` function

Each call to `update()` is like one frame of a movie -- you draw a complete picture from scratch, then the next frame replaces it.

!!! tip "Like frames in a movie"
    Each frame is a complete picture drawn from scratch. In this pattern, your code clears the last frame -- you redraw everything every time. That's why you always `clear()` before drawing.

---

## The clear -> draw -> display cycle

Every frame, your app typically does:

1. **clear()** -- Erase the display buffer (or the parts you care about).
2. **draw** -- Draw text, shapes, sprites, etc. into the buffer.
3. **display()** -- Send the buffer to the physical OLED screen.

The firmware keeps a drawing buffer, a working copy of the screen in memory. Your drawing commands write to it; `display()` pushes it to the pixels. Until you call `display()`, the user sees the previous frame.

!!! note "Why redraw everything?"
    The OLED is a simple framebuffer display. There's no built-in compositing or layers -- you own the whole 128 x 64 canvas each frame.

---

## millis()-based timing vs delay()

Use `millis()` for timing. Paste these examples into the [studio starter](../getting-started/first-app.md) where each comment says. The starter already calls `display.display()` at the end of `update()`.

- **delay(100)** - Does nothing in studio apps on the device or in the browser emulator. It does not create a pause. In built-in firmware code it can block the calling task.
- **millis()** -- Returns elapsed milliseconds since boot. Check it each frame and act when enough time has passed.

```cpp
// Paste at the top of the file, below the #include lines
static unsigned long lastFrameTime = 0;
static int currentFrame = 0;

// Paste inside begin(), below setColorsOff();
lastFrameTime = millis();
currentFrame = 0;

// Paste inside update(), just above display.display();
unsigned long frameTime = millis();
if (frameTime - lastFrameTime >= 100) {  // 10 animation steps per second
    lastFrameTime = frameTime;
    currentFrame = (currentFrame + 1) % 8;
}
display.clear();
display.fillCircle(15 + currentFrame * 14, 32, 5);
```

!!! warning "Avoid delay() in apps"
    Do not use `delay()` to schedule an app action. Compare `millis()` with a saved time, then return from `update()` so other work can run.

---

## Code example: frame-based animation

```cpp
// Paste at the top of the file, below the #include lines
static unsigned long lastStep = 0;
static int dropY = 8;

// Paste inside begin(), below setColorsOff();
lastStep = millis();
dropY = 8;

// Paste inside update(), just above display.display();
unsigned long frameTime = millis();
if (frameTime - lastStep >= 100) {
    lastStep = frameTime;
    dropY += 4;
    if (dropY > 56) dropY = 8;
}
// Draw on every update, even between movement steps.
display.clear();
for (int column = 0; column < 6; ++column) {
    display.fillRect(14 + column * 18, dropY, 3, 5);
}
```

You can update logic at a different rate than the draw rate. For example, change the `100` in the elapsed-time check to `30` to use a 30 ms movement threshold, while drawing on every update. Movement happens on the first update after that threshold, so its timing is approximate.

---

## Framework detail: TASK_20MS and HAL::loopHardware()

??? info "Advanced: how the firmware schedules updates"
    You do not need these details to build apps in the studio. They describe the firmware internals for readers writing an app by hand and building it into the firmware.

    Inside the firmware, the main loop uses a 20 ms task interval (`TASK_20MS = 20`). This firmware-source excerpt is not code for a studio app:

    <!-- check-examples: skip - firmware source excerpt, not a studio app -->
    ```cpp
    // In AppManager::loop(), with other firmware work between these lines:
    HAL::loopHardware();

    if ((millis_NOW - millis_APP_TASK_20MS) >= TASK_20MS) {
        millis_APP_TASK_20MS = millis_NOW;
        runActiveApp();
    }
    ```

    `HAL::loopHardware()` runs every main loop iteration and handles:

    - Button state polling (`s_buttonManager.update()`)
    - Slider reading (every 20 ms)
    - Accelerometer (every 50 ms)
    - Battery (every 200 ms)
    - RGB strip updates

    Your app's `update()` is only called when the 20 ms timer fires, so about 50 updates per second is the target. Slow work can make updates arrive later; keep each call short. Do not call `HAL::loopHardware()` from a studio app.

## Functions on this page

--8<-- "includes/reference/update-loop.md"
