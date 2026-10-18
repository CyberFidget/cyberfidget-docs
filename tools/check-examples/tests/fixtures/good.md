<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Independent fragments

```cpp
// Paste inside update(). Draw a greeting.
display.drawString(0, 0, "Hello");
```

!!! tip
    ```C++
    // Paste inside BEGIN(): initialize state.
    setColorsOff();
    ```

=== "Cleanup"
    ~~~arduino
    // Paste inside end()
    setColorsOff();
    ~~~

```c
// Paste at the top of the file: a helper.
static int answer() { return 42; }
```

```cpp
// Paste at the top of the file
static bool lit = false;

static void onRightPressed(const ButtonEvent& e) {
    if (e.eventType == ButtonEvent_Pressed) lit = !lit;
}

// Paste inside begin()
HAL::buttonManager().registerCallback(button_RightIndex, onRightPressed);

// Paste inside update()
HAL::setRgbLed(pixel_Front_Middle, 0, 0, lit ? 255 : 0, 0);
```
