# Buttons & Events

After this page you can make a button press change your app.

Buttons on the Cyber Fidget can *ring your functions* when something happens. You register a callback, and the framework calls it when the user presses, releases, or holds a button.

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
| **Pressed** | Button transitions from not pressed -> pressed |
| **Released** | Button transitions from pressed -> not pressed |
| **Held** | Button has been held down longer than the hold threshold (default 1500 ms). You get one Held event per press. |

You choose which events to handle. Many apps use **Pressed** for "do the thing" and **Released** for "back". A release event also follows a hold; it does not distinguish a tap from a long press by itself.

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
| 5 | `button_BottomRightIndex` / `button_EnterIndex` | Enter / confirm |

!!! important "Back button convention"
    **BottomLeft** (`button_BottomLeftIndex`) is the standard "back" or "exit" button. Users expect it to return to the menu or previous screen. The [studio starter](../getting-started/first-app.md) already registers and cleans up this callback. Keep it: it calls the app's `end()` and `MenuManager::instance().returnToMenu()`.

---

## Code example: callback registration

Paste these sections into the starter's `.cpp` file. The bottom-right button adds one to the score. The bottom-left button keeps its exit action. A free `static` function at the top of the file needs no declaration in the app's `.h` file.

Inside app methods, use `buttonManager`. In helpers outside the class, use `HAL::buttonManager()`. For continuous input you can also read `buttonManager.isPressed(button_RightIndex)` in `update()`.

```cpp
// Paste at the top of the file, below the #include lines
#include <stdio.h>
static int score = 0;
static void onActionPressed(const ButtonEvent& e) {
    if (e.eventType == ButtonEvent_Pressed) ++score;
}

// Paste inside begin(), below setColorsOff();
score = 0;
buttonManager.registerCallback(button_BottomRightIndex, onActionPressed);

// Paste inside update(), just above display.display();
display.clear();
display.setFont(ArialMT_Plain_16);
display.setTextAlignment(TEXT_ALIGN_CENTER);
char text[24];
snprintf(text, sizeof(text), "Score: %d", score);
display.drawString(64, 24, text);

// Paste inside end(), above unregisterButtonCallbacks();
buttonManager.unregisterCallback(button_BottomRightIndex);
```

A `ButtonEvent` groups information about one button action:

- `buttonIndex` -- Which button (0-5)
- `eventType` -- `ButtonEvent_Pressed`, `ButtonEvent_Released`, or `ButtonEvent_Held`
- `duration` -- Time held on a hold or release event, in ms; zero on a press. Studio apps on the device estimate this from event delivery times.

---

## Framework detail: ButtonManager internals

??? info "Advanced: how the firmware handles button events"
    You do not need these details to build apps in the studio. They describe the firmware internals for readers writing an app by hand and building it into the firmware.

    ### Ring buffer for events

    Inside the firmware, `ButtonManager` stores up to 16 events in a ring buffer, a queue that reuses its space. When a press, release, or hold is detected, it pushes an event. The firmware drains the queue and delivers events to the active app. Studio apps run their registered callbacks before their next `update()`.

    ### Debouncing

    Physical buttons "bounce" -- the electrical signal can flicker for a few milliseconds. The `ButtonManager` uses a configurable debounce time (default 20 ms). A state change is only registered after the reading has been stable for that duration. This prevents spurious double-presses.

    ### Hold threshold

    The hold threshold (default 1500 ms) determines when a **Held** event is generated. You get one Held event per press; it fires after the button has been down for that long.

## Functions on this page

--8<-- "includes/reference/buttons.md"
