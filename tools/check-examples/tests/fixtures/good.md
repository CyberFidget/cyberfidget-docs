<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Independent fragments

```cpp
// Insert inside update(), just above display.display();
// Draw a greeting.
display.drawString(0, 0, "Hello");
```

!!! tip
    ```C++
    // Insert inside begin(), below setColorsOff();
    // Initialize state.
    setColorsOff();
    ```

=== "Cleanup"
    ~~~arduino
    // Insert inside end(), above unregisterButtonCallbacks();
    setColorsOff();
    ~~~

```c
// Insert at the top of the file, below the #include lines
// A helper.
static int answer() { return 42; }
```

```cpp
// Insert at the top of the file, below the #include lines
static bool lit = false;

static void onRightPressed(const ButtonEvent& e) {
    if (e.eventType == ButtonEvent_Pressed) lit = !lit;
}

// Insert inside begin(), below setColorsOff();
HAL::buttonManager().registerCallback(button_RightIndex, onRightPressed);

// Insert inside update(), just above display.display();
HAL::setRgbLed(pixel_Front_Middle, 0, 0, lit ? 255 : 0, 0);
```
