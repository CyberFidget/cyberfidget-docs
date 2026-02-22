# The Update Loop

The Cyber Fidget firmware runs your app's `update()` function about 50 times per second. Understanding what happens in each "frame" and how timing works will help you build smooth, responsive apps.

---

## What is this?

The main loop runs continuously. Roughly every 20 milliseconds, the firmware:

1. Updates hardware (buttons, battery, slider, etc.)
2. Processes any button events
3. Calls your app's `update()` function

Each call to `update()` is like one frame of a movie — you draw a complete picture from scratch, then the next frame replaces it.

!!! tip "Like frames in a movie"
    Each frame is a complete picture drawn from scratch. The display doesn't "remember" the last frame — you redraw everything every time. That's why you always `clear()` before drawing.

---

## The clear → draw → display cycle

Every frame, your app typically does:

1. **clear()** — Erase the display buffer (or the parts you care about).
2. **draw** — Draw text, shapes, sprites, etc. into the buffer.
3. **display()** — Send the buffer to the physical OLED screen.

The OLED has an internal buffer. Your drawing commands write to that buffer; `display()` pushes it to the pixels. Until you call `display()`, the user sees the previous frame.

!!! note "Why redraw everything?"
    The OLED is a simple framebuffer display. There's no built-in compositing or layers — you own the whole 128×64 canvas each frame.

---

## millis()-based timing vs delay()

Use `millis()` (or equivalent) for timing, not `delay()`.

- **delay(100)** — Blocks the entire system for 100 ms. Buttons freeze, display freezes, nothing runs.
- **millis()** — Returns elapsed milliseconds since boot. Check it each frame and act when enough time has passed.

```cpp
// Good: non-blocking animation
unsigned long lastFrameTime = 0;
const unsigned long frameInterval = 100;  // 10 fps

void MyApp::update() {
    unsigned long now = millis();
    if (now - lastFrameTime >= frameInterval) {
        lastFrameTime = now;
        currentFrame = (currentFrame + 1) % numFrames;
    }
    display.clear();
    display.drawXbm(0, 0, 128, 64, frames[currentFrame]);
    display.display();
}
```

!!! warning "Avoid delay() in apps"
    `delay()` blocks the main loop. The device won't respond to buttons, and the system may appear frozen. Use `millis()`-based timing instead.

---

## Code example: frame-based animation

```cpp
void MatrixScreensaver::update() {
    unsigned long now = millis();
    // Only advance logic every frameInterval ms
    if (now - lastUpdateTime >= frameInterval) {
        lastUpdateTime = now;
        // Update column states, drop characters, etc.
        advanceLogic(now);
    }
    draw();  // Draw every time update() is called
}

void MatrixScreensaver::draw() {
    display.clear();           // 1. Erase buffer
    // 2. Draw all columns, characters, pixels
    for (int i = 0; i < NUM_COLUMNS; i++) {
        // ... draw each column ...
    }
    display.display();         // 3. Push to screen
}
```

You can update logic at a different rate than the draw rate. For example, update game state every 30 ms but still draw every 20 ms for smoother visuals.

---

## Framework detail: TASK_20MS and HAL::loopHardware()

The firmware uses a 20 ms task interval (`TASK_20MS = 20`):

```cpp
// In AppManager::loop()
HAL::loopHardware();  // Buttons, battery, slider, LEDs, etc.

if ((millis_NOW - millis_APP_TASK_20MS) >= TASK_20MS) {
    millis_APP_TASK_20MS = millis_NOW;
    runActiveApp();  // Your update() runs here
}
```

`HAL::loopHardware()` runs every main loop iteration and handles:

- Button state polling (`s_buttonManager.update()`)
- Slider reading (every 20 ms)
- Accelerometer (every 50 ms)
- Battery (every 200 ms)
- RGB strip updates

Your app's `update()` is only called when the 20 ms timer fires, so you get a steady ~50 Hz update rate regardless of how fast the main loop spins.
