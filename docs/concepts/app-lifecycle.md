# How an App Works

Every Cyber Fidget app follows the same lifecycle pattern: **begin** → **update** (repeated) → **end**. Understanding this pattern is the key to writing apps that feel at home on the device.

---

## What is this?

When you launch an app, the firmware does three things in order:

1. **begin()** — Runs once when the app starts. Set up your state, register button handlers, load resources.
2. **update()** — Runs over and over, about 50 times per second. This is where your app "lives": read inputs, update logic, draw to the screen.
3. **end()** — Runs once when the user exits. Clean up: unregister buttons, free resources, save state if needed.

!!! tip "Think of it like a board game"
    **begin()** = Setting up the board, dealing cards, placing pieces.  
    **update()** = Playing turns — each call is like one turn.  
    **end()** = Putting everything back in the box when you're done.

---

## The lifecycle in practice

- **begin()** runs once at start — use it for one-time setup.
- **update()** runs ~50 times per second — use it for everything that happens during the app.
- **end()** runs once on exit — use it to leave things tidy for the next app.

!!! note "Why ~50 times per second?"
    The firmware schedules app updates every 20 ms (`TASK_20MS`), which gives roughly 50 updates per second. See [The Update Loop](update-loop.md) for details.

---

## Code example: minimal app skeleton

```cpp
// MyApp.h
class MyApp {
public:
    void begin();
    void update();
    void end();
};

// MyApp.cpp
void MyApp::begin() {
    // Runs once when app launches
    score = 0;
    // Register button callbacks here
}

void MyApp::update() {
    // Runs ~50 times per second
    display.clear();
    display.drawString(0, 0, "Score: " + String(score));
    display.display();
}

void MyApp::end() {
    // Runs once when user exits
    // Unregister button callbacks here
}
```

To register your app with the system, add an entry to `AppManifest.h`:

```cpp
APP_ENTRY(APP_MY_APP, "My App", "Games",
    [](){ myApp.begin(); },
    [](){ myApp.end(); },
    [](){ myApp.update(); }
)
```

---

## Framework details: how it all connects

### AppManager calls your functions

The `AppManager` singleton owns the app lifecycle. When the user selects your app from the menu:

1. It calls `appDefs[appActive].endFunc()` for the *previous* app.
2. It sets `appActive` to your app.
3. It calls `appDefs[appActive].beginFunc()` for your app.

Every loop iteration (when `TASK_20MS` has elapsed), it calls `appDefs[appActive].runFunc()` — which is your `update()`.

### The APP_ENTRY macro

`APP_ENTRY` expands into an entry in the `appDefs[]` array. The macro takes:

- **Enum name** — e.g. `APP_MY_APP`
- **Menu label** — What appears in the app menu
- **Category path** — e.g. `"Games"` or `"Tools/WiFi"`
- **beginFunc** — Function to call when the app starts
- **endFunc** — Function to call when the app exits
- **runFunc** — Function to call every ~20 ms (your update loop)

### Static instance pattern

Most apps use a single global or static instance (e.g. `MyApp myApp`) and pass lambdas that call its methods. This keeps the manifest clean and lets each app own its state.
