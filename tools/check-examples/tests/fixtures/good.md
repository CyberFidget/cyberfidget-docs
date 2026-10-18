<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Independent fragments

```cpp
// Paste inside update(). Draw a greeting.
d.drawString(0, 0, "Hello");
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
