<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Independent fragments

```cpp
// Paste inside update(), just above display.display();
// Draw a greeting.
display.drawString(0, 0, "Hello");
```

!!! tip
    ```C++
    // Paste inside begin(), below setColorsOff();
    // Initialize state.
    setColorsOff();
    ```

=== "Cleanup"
    ~~~arduino
    // Paste inside end(), above unregisterButtonCallbacks();
    setColorsOff();
    ~~~

```c
// Paste at the top of the file, below the #include lines
// A helper.
static int answer() { return 42; }
```

```cpp
// Paste at the top of the file, below the #include lines
static bool lit = false;

static void onRightPressed(const ButtonEvent& e) {
    if (e.eventType == ButtonEvent_Pressed) lit = !lit;
}

// Paste inside begin(), below setColorsOff();
HAL::buttonManager().registerCallback(button_RightIndex, onRightPressed);

// Paste inside update(), just above display.display();
HAL::setRgbLed(pixel_Front_Middle, 0, 0, lit ? 255 : 0, 0);
```
