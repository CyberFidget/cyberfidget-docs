# Buttons & Events

Buttons on the Cyber Fidget don't get polled in your app — they *ring your functions* when something happens. You register a callback, and the framework calls it when the user presses, releases, or holds a button.

---

## What is this?

Instead of checking "is the button down?" every frame, you tell the system: *"When this button is pressed, call this function."* That function is a **callback**. When the event happens, your code runs.

!!! tip "Like a doorbell"
    You don't stand at the door asking "Is someone there?" You install a doorbell and go about your day. When someone presses it, your bell function rings. Same idea: register a callback, and it gets called when the event happens.

---

## Event types

The `ButtonManager` generates three event types:

| Event | When it fires |
|-------|----------------|
| **Pressed** | Button transitions from not pressed → pressed |
| **Released** | Button transitions from pressed → not pressed |
| **Held** | Button has been held down longer than the hold threshold (default 1500 ms) |

You choose which events to handle. Many apps use **Pressed** for "do the thing" and **Released** for "back" (so you don't exit on accidental holds).

---

## The 6 buttons: positions and names

The device has 6 physical buttons. You refer to them by index or semantic name:

| Index | Semantic name | Typical use |
|-------|---------------|--------------|
| 0 | `button_TopLeftIndex` / `button_UpIndex` | Up / primary action |
| 1 | `button_TopRightIndex` / `button_DownIndex` | Down |
| 2 | `button_MiddleLeftIndex` / `button_LeftIndex` | Left |
| 3 | `button_MiddleRightIndex` / `button_RightIndex` | Right |
| 4 | `button_BottomLeftIndex` / `button_SelectIndex` | **Back** (convention) |
| 5 | `button_BottomRightIndex` / `button_EnterIndex` | Select / Enter |

!!! important "Back button convention"
    **BottomLeft** (`button_BottomLeftIndex`) is the standard "back" or "exit" button. Users expect it to return to the menu or previous screen. Register a callback for it in `begin()` and unregister in `end()`.

---

## Code example: callback registration

```cpp
// In begin(): register your callbacks
void MyApp::begin() {
    buttonManager.registerCallback(button_BottomLeftIndex, onButtonBackPressed);
    buttonManager.registerCallback(button_BottomRightIndex, onButtonActionPressed);
}

// In end(): unregister so the next app gets clean state
void MyApp::end() {
    buttonManager.unregisterCallback(button_BottomLeftIndex);
    buttonManager.unregisterCallback(button_BottomRightIndex);
}

// Callback signature: void (const ButtonEvent&)
static void MyApp::onButtonBackPressed(const ButtonEvent& e) {
    if (e.eventType == ButtonEvent_Released) {
        AppManager::instance().switchToApp(APP_MENU);  // Exit to menu
    }
}

static void MyApp::onButtonActionPressed(const ButtonEvent& e) {
    if (e.eventType == ButtonEvent_Pressed) {
        score++;  // Do something on press
    }
}
```

The `ButtonEvent` struct includes:

- `buttonIndex` — Which button (0–5)
- `eventType` — `ButtonEvent_Pressed`, `ButtonEvent_Released`, or `ButtonEvent_Held`
- `duration` — How long the button was pressed (ms)

---

## Framework detail: ButtonManager internals

### Ring buffer for events

The `ButtonManager` stores events in a fixed-size ring buffer (`MAX_EVENTS = 16`). When a press, release, or hold is detected, it pushes an event. `AppManager::processButtonEvents()` drains the queue each loop and invokes the registered callback for each button that has one.

### Debouncing

Physical buttons "bounce" — the electrical signal can flicker for a few milliseconds. The `ButtonManager` uses a configurable debounce time (default 20 ms). A state change is only registered after the reading has been stable for that duration. This prevents spurious double-presses.

### Hold threshold

The hold threshold (default 1500 ms) determines when a **Held** event is generated. You get one Held event per press; it fires after the button has been down for that long.
