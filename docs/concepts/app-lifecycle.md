# How an App Works

After this page you can set up, update and clean up a Cyber Fidget app.

Every Cyber Fidget app follows the same lifecycle pattern: **begin** -> **update** (repeated) -> **end**. Understanding this pattern is the key to writing apps that feel at home on the device.

---

## What is this?

When you launch an app, the firmware does three things in order:

1. **begin()** -- Runs once when the app starts. Set up your state, register button handlers, load resources.
2. **update()** -- Runs over and over, about 50 times per second. This is where your app "lives": read inputs, update logic, draw to the screen.
3. **end()** -- Runs once when the user exits. Clean up: unregister buttons, free resources, save state if needed.

!!! tip "Think of it like a board game"
    - **begin()** = Setting up the board, dealing cards, placing pieces.
    - **update()** = Playing turns -- each call is like one turn.
    - **end()** = Putting everything back in the box when you're done.

---

## The lifecycle in practice

- **begin()** runs once at start -- use it for one-time setup.
- **update()** runs ~50 times per second -- use it for everything that happens during the app.
- **end()** runs once on exit -- use it to leave things tidy for the next app.

!!! note "Why ~50 times per second?"
    The firmware schedules app updates every 20 ms (`TASK_20MS`), which gives roughly 50 updates per second. See [The Update Loop](update-loop.md) for details.

---

## Code example: reset and draw a score

Start with **Code from Blank Template** in the [studio](../getting-started/first-app.md). Add each section into the `.cpp` file where its comment says. "At the top" means below the `#include` lines and above the app object, not inside a method. Keep the starter's button setup and cleanup, including `setColorsOff()` in `begin()` and `end()`; its bottom-left button returns to the menu.

```cpp
// Insert at the top of the file, below the #include lines
#include <stdio.h>
static int score = 0;

// Insert inside begin(), below setColorsOff();
score = 0;

// Insert inside update(), just above display.display();
display.clear();
display.setFont(ArialMT_Plain_16);
display.setTextAlignment(TEXT_ALIGN_CENTER);
char text[24];
snprintf(text, sizeof(text), "Score: %d", score);
display.drawString(64, 24, text);
```

`snprintf()` writes the score into a fixed-size `char` buffer, an array that holds the text. The screen draws that text. Change `score` in your app logic to change what appears. To make a button add to the score, see [Buttons & Events](buttons.md#code-example-callback-registration).

The studio adds your app to the menu using the Menu Category you choose. You do not edit a manifest for a studio app.

---

## Functions on this page

--8<-- "includes/reference/app-lifecycle.md"

## Framework details: how it all connects

!!! advanced "Advanced: how the firmware runs your app"
    You do not need these details to build apps in the studio. The studio and firmware handle app registration and scheduling for you; this section is for writing an app by hand and building it into the firmware.

    **Firmware-source excerpt:** built-in apps are registered in `AppManifest.h` with `APP_ENTRY`. This excerpt assumes the app class, global `myApp` instance and app identifier are defined in the firmware; it is not code to add into a studio app.

    <!-- check-examples: skip - firmware source excerpt, not a studio app -->
    ```cpp
    APP_ENTRY(APP_MY_APP, "My App", "Games",
        [](){ myApp.begin(); },
        [](){ myApp.end(); },
        [](){ myApp.update(); }
    )
    ```

    ### AppManager calls your functions

    Inside the firmware, `AppManager` owns the app lifecycle. A singleton is an object shared through one instance. When the user selects your app from the menu:

    1. It calls `appDefs[appActive].endFunc()` for the *previous* app.
    2. It sets `appActive` to your app.
    3. It calls `appDefs[appActive].beginFunc()` for your app.

    When the 20 ms update interval has elapsed, it calls `appDefs[appActive].runFunc()` -- which is your `update()`.

    ### The APP_ENTRY macro

    A macro is a named piece of code expanded by the C++ preprocessor before compilation. These details apply to built-in firmware apps.

    `APP_ENTRY` expands into an entry in the `appDefs[]` array. The macro takes:

    - **Enum name** -- e.g. `APP_MY_APP`
    - **Menu label** -- What appears in the app menu
    - **Category path** -- e.g. `"Games"` or `"Tools/WiFi"`
    - **beginFunc** -- Function to call when the app starts
    - **endFunc** -- Function to call when the app exits
    - **runFunc** -- Function to call every ~20 ms (your update loop)

    ### Static instance pattern

    Built-in apps commonly use a single global instance (e.g. `MyApp myApp`) and pass lambdas, short unnamed functions, that call its methods. This keeps the manifest clean and lets each app own its state.
