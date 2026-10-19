<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- check-examples: cumulative -->
# Cumulative steps

```cpp
// Insert at the top of the file, below the #include lines
static int taps = 0;

// Insert inside update(), just above display.display();
display.drawString(0, 0, "Taps");
```

```cpp
// Insert at the top of the file, below the #include lines
static void onTap(const ButtonEvent& e) {
    if (e.eventType == ButtonEvent_Pressed) taps++;
}

// Insert inside begin(), below setColorsOff();
buttonManager.registerCallback(button_MiddleRightIndex, onTap);

// Insert inside end(), above unregisterButtonCallbacks();
buttonManager.unregisterCallback(button_MiddleRightIndex);
```

<!-- check-examples: skip - skipped blocks do not accumulate -->
```cpp
// Insert inside update(), just above display.display();
this is not code;
```

```cpp
// Insert inside update(), just above display.display();
display.drawProgressBar(0, 20, 100, 8, taps % 101);
```

```cpp
class Alone {
public:
    void begin() {}
    void update() {}
    void end() {}
};
Alone alone;
```

<!-- check-examples: final -->
```cpp
#include "Tapper.h"
#include "globals.h"
#include "HAL.h"
#include "MenuManager.h"


static int taps = 0;

static void onTap(const ButtonEvent& e) {
    if (e.eventType == ButtonEvent_Pressed) taps++;
}

Tapper tapper(HAL::buttonManager());
Tapper* Tapper::instance = nullptr;

Tapper::Tapper(ButtonManager& btnMgr) :
    buttonManager(btnMgr), display(HAL::displayProxy()) { instance = this; }

// begin() runs once when your app opens from the menu.
// Set things up here: hook up the buttons and start with the lights off.
void Tapper::begin() {
    registerButtonCallbacks();
    setColorsOff();
buttonManager.registerCallback(button_MiddleRightIndex, onTap);


}

// update() runs about 50 times a second while your app is open.
// Clear the screen, draw what you want, then show it.
// The case hides about 8 pixels at each screen corner, so keep text and
// important pixels out of those corners.
void Tapper::update() {
    display.clear();
    display.setTextAlignment(TEXT_ALIGN_CENTER);
    display.setFont(ArialMT_Plain_16);
    display.drawString(64, 24, "Tapper");

display.drawString(0, 0, "Taps");
display.drawProgressBar(0, 20, 100, 8, taps % 101);
    display.display();
}

// end() runs when your app closes. Let go of the buttons and turn the
// lights off (if your app plays sounds, call stopTone() here too).
void Tapper::end() {

buttonManager.unregisterCallback(button_MiddleRightIndex);
    unregisterButtonCallbacks();
    setColorsOff();
}

// The bottom-left button closes your app and goes back to the menu.
void Tapper::onButtonBackPressed(const ButtonEvent& event) {
    if (event.eventType == ButtonEvent_Released) {
        instance->end();
        MenuManager::instance().returnToMenu();
    }
}

void Tapper::registerButtonCallbacks() {
    buttonManager.registerCallback(button_BottomLeftIndex, onButtonBackPressed);
}

void Tapper::unregisterButtonCallbacks() {
    buttonManager.unregisterCallback(button_BottomLeftIndex);
}
```
