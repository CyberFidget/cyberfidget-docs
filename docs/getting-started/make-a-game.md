<!-- check-examples: cumulative -->
# Make a game, step by step

By the end of this page you will have built a small game called Catcher. Dots fly across the screen, you slide a paddle up and down to catch them, and the game keeps score, flashes the lights, beeps, and ends when you run out of lives.

<video src="../../assets/media/emulator-catcher.webm" poster="../../assets/media/emulator-catcher.png" autoplay loop muted playsinline width="300"></video>

*What you'll make: Catcher running in the emulator. The slider moves the paddle on the right; the score and lives are at the top.*

You build it in eight small steps. Each step adds a few lines and you run the game after each one, so you always know which change did what.

!!! note "One app, built up step by step"
    This page builds **one** app across all its steps. Every step adds to the code from the steps before it, so do them in order and do not skip any. (The [Make apps](../concepts/index.md) pages work differently: each of their examples stands alone and goes into a fresh blank template.)

!!! note "What you need"
    - A computer with Chrome, Edge or Firefox, and an internet connection. A Cyber Fidget is optional: the emulator, a copy of the device that runs on the page, is enough.
    - About 30 minutes.
    - It helps to have done [Build your first app](first-app.md) first. This page assumes you know where **REBUILD** is.

---

## Start: a blank app called Catcher

1. Go to [cyberfidget.com/create/](https://cyberfidget.com/create/) and press **+ Create an app**.
2. Press **Code from Blank Template**.
3. Type `Catcher` as the **App Name**. The **Code Name** fills in as `Catcher` too. Pick **Games** as the **Menu Category** if you like.
4. Press **Create**.

You are looking at the starter code in the `.cpp` file. Every step below is one or more blocks of code. The first line of each part says where it goes:

| First line of the part | Where it goes |
|------------------------|-------------------|
| `// Insert at the top of the file, below the #include lines` | Under the four `#include` lines at the top, above the line `Catcher catcher(HAL::buttonManager());`. |
| `// Insert inside begin(), below setColorsOff();` | Inside `begin()`, under the line `setColorsOff();`. |
| `// Insert inside update(), just above display.display();` | Inside `update()`, on the line above `display.display();`. |
| `// Insert inside end(), above unregisterButtonCallbacks();` | Inside `end()`, above the line `unregisterButtonCallbacks();`. |

When a step inserts into a place you have already used, put the new lines **below** the lines you added there before. Include the comment lines (the ones starting with `//`) too: they keep your file readable, and they match the finished listing at the end of this page. You don't need the placement line itself.

Never delete or change earlier lines. Every step only adds.

!!! tip "Keep this, make it your own"
    **Keep:** the starter's shape: `begin()`, `update()` and `end()`, the back-button code at the bottom, and `display.display();` as the last line of `update()`. That is the framework every app runs on (see [App lifecycle](../concepts/app-lifecycle.md)).

    **Make it your own:** the numbers, sizes, speeds, colors, sounds and words in each step. Boxes like this one along the way say what each number does, and what else changes when you change it.

---

## Step 1: a paddle that follows the slider

The paddle is a thin upright bar near the right edge of the screen. The slider moves it.

```cpp
// Insert at the top of the file, below the #include lines
// The paddle: a thin upright bar near the right edge.
static const int PADDLE_X = 116;
static const int PADDLE_H = 14;
static int paddleY = 25;
```

```cpp
// Insert inside update(), just above display.display();
// Wipe the template's title so the game has the whole screen.
display.clear();
// Slider at the top puts the paddle at the top of the screen.
paddleY = map(sliderPosition_8Bits_Inverted_Filtered, 0, 255, 64 - PADDLE_H, 0);
display.fillRect(PADDLE_X, paddleY, 3, PADDLE_H);
```

`int` is a whole number. `static` at the top of the file keeps a variable alive between calls to `update()`, so `paddleY` remembers its value from one frame to the next. `const` means the value never changes: the paddle's x position and height are fixed, so they are `const` and written in capitals as a reminder. `sliderPosition_8Bits_Inverted_Filtered` reads 0 with the slider at the bottom and 255 at the top. `map()` turns that 0-255 range into a screen position from 50 (low on the screen) to 0 (the top). The screen is 64 pixels tall and y counts down from the top, so `64 - PADDLE_H` is the lowest the paddle can go and still fit. `display.fillRect(x, y, width, height)` draws a filled rectangle 3 pixels wide.

**Press REBUILD & RUN** (the first build of a new app; from now on, use **REBUILD**). You see a short bar on the right. Drag the slider up and down: the bar follows it.

!!! tip "Make it your own"
    `PADDLE_H` is the paddle's height: make it smaller for a harder game. `PADDLE_X` moves the paddle sideways. Later steps use both names, so the catch check follows whatever you choose. Keep `PADDLE_X` below 125 so the paddle stays on the screen.

---

## Step 2: a dot that flies across

```cpp
// Insert at the top of the file, below the #include lines
// The dot starts at the left edge, at a random height.
static int dotX = 8;
static int dotY = 32;
// Pixels to move each frame. Zero pauses the dot.
static int dotSpeed = 1;
static void newDot() {
    dotX = 8;
    dotY = random(12, 54);
}
```

```cpp
// Insert inside begin(), below setColorsOff();
newDot();
dotSpeed = 1;
```

```cpp
// Insert inside update(), just above display.display();
// Move the dot at its current speed, then draw it.
dotX += dotSpeed;
display.fillCircle(dotX, dotY, 2);
```

`newDot()` is a small function of our own: calling it puts the dot back at the left edge. `void` in front of its name means it doesn't hand back a value. `dotX += dotSpeed` adds `dotSpeed` to `dotX`. `random(12, 54)` picks a whole number from 12 up to 53. The score in step 4 lights pixels down to y=9. The dot has a radius of 2, so its top pixel stays at y=10 or below, clear of the score. `dotSpeed` starts at 1 pixel per frame; step 8 will change it. `update()` runs about 50 times a second, so the dot moves about 50 pixels a second.

**Press REBUILD.** One dot crosses the screen and flies off the right edge. It does not come back yet: that is the next step. Press **<< RESTART** to watch it again.

!!! tip "Make it your own"
    The last number in `display.fillCircle(dotX, dotY, 2)` is the dot's radius. If you make the dot bigger, also change the small numbers in step 3's catch check (`- 2` and `+ 1`), which allow for a radius of 2, and raise the `12` in `random(12, 54)` so a big dot stays clear of the score.

---

## Step 3: catch or miss

When the dot reaches the paddle, the game checks whether the paddle is in its way.

```cpp
// Insert at the top of the file, below the #include lines
static int score = 0;
static int lives = 3;
// Set for one frame when the dot is caught or missed.
static bool caught = false;
static bool missed = false;
```

```cpp
// Insert inside begin(), below setColorsOff();
// Start every game fresh when the app opens.
score = 0;
lives = 3;
caught = false;
missed = false;
```

```cpp
// Insert inside update(), just above display.display();
caught = false;
missed = false;
if (lives > 0 && dotX >= PADDLE_X - 2) {
    if (dotY >= paddleY - 2 && dotY <= paddleY + PADDLE_H + 1) {
        caught = true;
        score++;
    } else {
        missed = true;
        lives--;
    }
    newDot();
}
```

A `bool` holds either `true` or `false`. In the `if`, `&&` means "and": the check runs only while you have lives left **and** the dot has reached the paddle. `score++` adds one to the score, and `lives--` takes one away.

The dot is a circle with a radius of 2 pixels, so it touches the paddle when its center is 2 pixels to the left of `PADDLE_X`. The `- 2` and `+ 1` count a catch when the edge of the dot touches the paddle's top or bottom pixel (the paddle's bottom pixel is at `paddleY + PADDLE_H - 1`). `caught` and `missed` are only true in the frame where it happens. The next steps use them to flash the lights and beep.

`begin()` sets the score and lives back to their starting values. Without that, closing the game and opening it again would carry on with the old score.

**Press REBUILD.** Dots keep coming: each time one reaches the paddle, a new one starts at the left. You cannot see the score yet, but the game is counting. After three misses the lives are used up, so the next dot flies off the edge and no new one comes.

!!! tip "Make it your own"
    To start with more lives, change the `3` in `lives = 3;`. It appears here twice (at the top of the file and in `begin()`) and once more in step 7, so change all three.

---

## Step 4: show the score

```cpp
// Insert at the top of the file, below the #include lines
#include <stdio.h>
```

```cpp
// Insert inside update(), just above display.display();
// Write the score and lives into a short piece of text, then draw it.
char text[24];
snprintf(text, sizeof(text), "Score %d  Lives %d", score, lives);
display.setFont(ArialMT_Plain_10);
display.setTextAlignment(TEXT_ALIGN_CENTER);
display.drawString(64, 0, text);
```

`char text[24]` is a buffer: room for 24 characters of text. `snprintf()` fills it, putting the numbers where the `%d` marks are. The `sizeof(text)` part stops it from writing more than the buffer holds. `#include <stdio.h>` makes `snprintf()` available.

The text is centered at the top middle of the screen. The case hides about 8 pixels at each corner, so keep text out of the corners.

**Press REBUILD.** The score goes up when you catch a dot, and the lives go down when you miss one. At zero lives, the counting stops. Use **<< RESTART** to reset the game until step 7 adds the game over screen and a restart button.

---

## Step 5: flash the lights

```cpp
// Insert at the top of the file, below the #include lines
// When the lights came on, so they can go off again.
static bool lit = false;
static unsigned long litAt = 0;
```

```cpp
// Insert inside begin(), below setColorsOff();
lit = false;
litAt = 0;
```

```cpp
// Insert inside update(), just above display.display();
if (caught) {
    setDeterminedColorsAll(0, 255, 0, 0);
    lit = true;
    litAt = millis();
}
if (missed) {
    setDeterminedColorsAll(255, 0, 0, 0);
    lit = true;
    litAt = millis();
}
if (lit && millis() - litAt > 200) {
    setColorsOff();
    lit = false;
}
```

`setDeterminedColorsAll()` sets all four LEDs. Its numbers are red, green, blue and white, each from 0 (off) to 255 (full). `millis()` is the time in milliseconds (thousandths of a second), so the lights turn off just after 200 milliseconds. Subtracting unsigned times (`millis() - litAt`) also works when the clock wraps back to zero. The game keeps running in the meantime: there is no pause.

`unsigned long` is a whole number that is never negative and big enough for `millis()`. `lit && millis() - litAt > 200` means "the lights are on **and** more than 200 milliseconds have passed".

**Press REBUILD.** The LEDs on the emulator flash green when you catch a dot and red when you miss.

!!! tip "Make it your own"
    Change the four numbers in each `setDeterminedColorsAll()` to pick other colors: `(0, 0, 255, 0)` is blue. Change `200` to make the flash longer or shorter. Keep `setColorsOff()` and `lit = false` together, so the lights always go off.

---

## Step 6: add sound

```cpp
// Insert inside update(), just above display.display();
if (caught) {
    HAL::audioManager().playTone(1568, 60);
}
if (missed) {
    HAL::audioManager().playTone(900, 150);
}
```

```cpp
// Insert inside end(), above unregisterButtonCallbacks();
HAL::audioManager().stopTone();
```

`playTone(1568, 60)` plays a short high beep: 1568 Hz (the note G6) for 60 milliseconds. A miss plays a lower, longer tone. `stopTone()` in `end()` makes sure no sound keeps playing after the game closes. (The starter's `end()` already turns the lights off.)

**Press REBUILD.** Catches beep. Misses buzz lower. Turn the sound up with the emulator's volume control if you cannot hear it.

!!! tip "Make it your own"
    The first number in `playTone()` is the pitch in Hz (higher is higher), and the second is how long it plays, in milliseconds. Keep `stopTone()` in `end()`: it makes sure your game never leaves a sound playing. [Sound & Music](../concepts/audio.md) has notes and melodies.

---

## Step 7: game over and play again

When the lives run out, the game shows a game over screen. The middle-right button starts a new game.

```cpp
// Insert at the top of the file, below the #include lines
// The middle-right button starts a new game after game over.
static void onRestart(const ButtonEvent& e) {
    if (e.eventType == ButtonEvent_Pressed && lives <= 0) {
        score = 0;
        lives = 3;
        caught = false;
        missed = false;
        lit = false;
        litAt = 0;
        setColorsOff();
        HAL::audioManager().stopTone();
        newDot();
        dotSpeed = 1;
    }
}
```

```cpp
// Insert inside begin(), below setColorsOff();
buttonManager.registerCallback(button_MiddleRightIndex, onRestart);
```

```cpp
// Insert inside update(), just above display.display();
if (lives <= 0) {
    // Pause movement and clear every effect.
    dotSpeed = 0;
    dotX = 8;
    setColorsOff();
    lit = false;
    HAL::audioManager().stopTone();
    display.clear();
    display.setFont(ArialMT_Plain_16);
    display.drawString(64, 10, "Game over");
    display.setFont(ArialMT_Plain_10);
    snprintf(text, sizeof(text), "Score %d", score);
    display.drawString(64, 30, text);
    display.drawString(64, 44, "Right: play again");
}
```

```cpp
// Insert inside end(), above unregisterButtonCallbacks();
buttonManager.unregisterCallback(button_MiddleRightIndex);
```

`onRestart` is a callback: a function the device calls for you when the button changes. It is registered in `begin()` and let go of in `end()`, so the button does nothing once the game closes. It only restarts when the game is over (`lives <= 0`: lives at or below zero), so a press during play does nothing.

`const ButtonEvent& e` is what the device hands the callback: the button event, with `e.eventType` saying whether the button was pressed or released. The `&` means the callback looks at the device's own event instead of a copy, and `const` means it only reads it. Write callbacks with this exact first line, changing only the name.

The game over code reuses the `text` buffer from step 4, because both are inside `update()`. At game over, the dot is parked at the left with speed 0. The catch check also requires lives above 0. The score and lives stay fixed, and the lights and sound turn off. Restarting clears the score, effects and catch flags, restores three lives and the starting speed, and picks another dot height. The text is still centered, because step 4 set the alignment earlier in the same frame.

**Press REBUILD.** Miss three dots on purpose. The game over screen shows your score. Press the middle-right button (**Middle Right - Right** in the emulator) to play again. The bottom-left button still closes the game.

---

## Step 8: speed up as you score

```cpp
// Insert inside update(), just above display.display();
// Set the next frame's speed only while playing.
if (lives > 0) {
    dotSpeed = min(3, 1 + score / 5);
}
```

Dividing whole numbers in C++ drops the remainder, so `score / 5` is 0 for scores 0 to 4, 1 for 5 to 9, and so on. `min(3, ...)` chooses the smaller number, so the speed stops growing at 3 pixels per frame. At about 50 frames per second, even the fastest dot takes about 0.7 seconds to reach the paddle. This leaves time to aim with the slider. The speed applies on the next frame and stays at 0 during game over.

**Press REBUILD.** After 5 catches the dots move twice as fast. After 10 they reach their top speed of 3 pixels per frame. Miss three dots, wait on the game over screen, then restart: the dots begin slowly again.

!!! tip "Make it your own"
    `5` is how many catches it takes to speed up, and `3` is the top speed in pixels per frame. A top speed much above 4 is very hard to catch with the slider. The `1` is the starting speed; if you change it, change `dotSpeed = 1;` in step 2 and step 7 to match.

---

## The whole game

This is the complete `Catcher.cpp` after all eight steps. If your game does not build, compare your file with it. The `Catcher.h` file is unchanged from the template.

<!-- check-examples: final -->
```cpp
#include "Catcher.h"
#include "globals.h"
#include "HAL.h"
#include "MenuManager.h"

// The paddle: a thin upright bar near the right edge.
static const int PADDLE_X = 116;
static const int PADDLE_H = 14;
static int paddleY = 25;
// The dot starts at the left edge, at a random height.
static int dotX = 8;
static int dotY = 32;
// Pixels to move each frame. Zero pauses the dot.
static int dotSpeed = 1;
static void newDot() {
    dotX = 8;
    dotY = random(12, 54);
}
static int score = 0;
static int lives = 3;
// Set for one frame when the dot is caught or missed.
static bool caught = false;
static bool missed = false;
#include <stdio.h>
// When the lights came on, so they can go off again.
static bool lit = false;
static unsigned long litAt = 0;
// The middle-right button starts a new game after game over.
static void onRestart(const ButtonEvent& e) {
    if (e.eventType == ButtonEvent_Pressed && lives <= 0) {
        score = 0;
        lives = 3;
        caught = false;
        missed = false;
        lit = false;
        litAt = 0;
        setColorsOff();
        HAL::audioManager().stopTone();
        newDot();
        dotSpeed = 1;
    }
}

Catcher catcher(HAL::buttonManager());
Catcher* Catcher::instance = nullptr;

Catcher::Catcher(ButtonManager& btnMgr) :
    buttonManager(btnMgr), display(HAL::displayProxy()) { instance = this; }

// begin() runs once when your app opens from the menu.
// Set things up here: hook up the buttons and start with the lights off.
void Catcher::begin() {
    registerButtonCallbacks();
    setColorsOff();
    newDot();
    dotSpeed = 1;
    // Start every game fresh when the app opens.
    score = 0;
    lives = 3;
    caught = false;
    missed = false;
    lit = false;
    litAt = 0;
    buttonManager.registerCallback(button_MiddleRightIndex, onRestart);
}

// update() runs about 50 times a second while your app is open.
// Clear the screen, draw what you want, then show it.
// The case hides about 8 pixels at each screen corner, so keep text and
// important pixels out of those corners.
void Catcher::update() {
    display.clear();
    display.setTextAlignment(TEXT_ALIGN_CENTER);
    display.setFont(ArialMT_Plain_16);
    display.drawString(64, 24, "Catcher");
    // Wipe the template's title so the game has the whole screen.
    display.clear();
    // Slider at the top puts the paddle at the top of the screen.
    paddleY = map(sliderPosition_8Bits_Inverted_Filtered, 0, 255, 64 - PADDLE_H, 0);
    display.fillRect(PADDLE_X, paddleY, 3, PADDLE_H);
    // Move the dot at its current speed, then draw it.
    dotX += dotSpeed;
    display.fillCircle(dotX, dotY, 2);
    caught = false;
    missed = false;
    if (lives > 0 && dotX >= PADDLE_X - 2) {
        if (dotY >= paddleY - 2 && dotY <= paddleY + PADDLE_H + 1) {
            caught = true;
            score++;
        } else {
            missed = true;
            lives--;
        }
        newDot();
    }
    // Write the score and lives into a short piece of text, then draw it.
    char text[24];
    snprintf(text, sizeof(text), "Score %d  Lives %d", score, lives);
    display.setFont(ArialMT_Plain_10);
    display.setTextAlignment(TEXT_ALIGN_CENTER);
    display.drawString(64, 0, text);
    if (caught) {
        setDeterminedColorsAll(0, 255, 0, 0);
        lit = true;
        litAt = millis();
    }
    if (missed) {
        setDeterminedColorsAll(255, 0, 0, 0);
        lit = true;
        litAt = millis();
    }
    if (lit && millis() - litAt > 200) {
        setColorsOff();
        lit = false;
    }
    if (caught) {
        HAL::audioManager().playTone(1568, 60);
    }
    if (missed) {
        HAL::audioManager().playTone(900, 150);
    }
    if (lives <= 0) {
        // Pause movement and clear every effect.
        dotSpeed = 0;
        dotX = 8;
        setColorsOff();
        lit = false;
        HAL::audioManager().stopTone();
        display.clear();
        display.setFont(ArialMT_Plain_16);
        display.drawString(64, 10, "Game over");
        display.setFont(ArialMT_Plain_10);
        snprintf(text, sizeof(text), "Score %d", score);
        display.drawString(64, 30, text);
        display.drawString(64, 44, "Right: play again");
    }
    // Set the next frame's speed only while playing.
    if (lives > 0) {
        dotSpeed = min(3, 1 + score / 5);
    }
    display.display();
}

// end() runs when your app closes. Let go of the buttons and turn the
// lights off (if your app plays sounds, call stopTone() here too).
void Catcher::end() {

    HAL::audioManager().stopTone();
    buttonManager.unregisterCallback(button_MiddleRightIndex);
    unregisterButtonCallbacks();
    setColorsOff();
}

// The bottom-left button closes your app and goes back to the menu.
void Catcher::onButtonBackPressed(const ButtonEvent& event) {
    if (event.eventType == ButtonEvent_Released) {
        instance->end();
        MenuManager::instance().returnToMenu();
    }
}

void Catcher::registerButtonCallbacks() {
    buttonManager.registerCallback(button_BottomLeftIndex, onButtonBackPressed);
}

void Catcher::unregisterButtonCallbacks() {
    buttonManager.unregisterCallback(button_BottomLeftIndex);
}
```

### The finished game

<video src="../../assets/media/emulator-catcher.webm" poster="../../assets/media/emulator-catcher.png" autoplay loop muted playsinline width="300"></video>

*The finished Catcher in the emulator: dots fly in from the left, the paddle catches them, and a miss costs a life.*

The game is yours: install it on your Cyber Fidget the same way as in [Build your first app](first-app.md#7-install-it-on-your-cyber-fidget).

!!! tip "Swap the dot for a sprite"
    To draw a picture instead of the dot, follow one of the three options in [Sprites & Animation](../concepts/sprites.md#part-1-your-first-sprite-on-the-screen), then draw your sprite at `dotX, dotY` in place of `display.fillCircle()`. If you use an actor, name it something like `dotActor`, not after your sprite.

---

## Ideas to try next

- **Play with the buttons instead of the slider.** Read `buttonManager.isPressed(button_TopLeftIndex)` in `update()` and move the paddle a pixel at a time. See [Buttons & Events](../concepts/buttons.md).
- **Swap the dot for a picture.** Draw a sprite in the Studio and draw it where the dot is. See [Sprites & Animation](../concepts/sprites.md).
- **A best score.** Keep a `static int best` and update it at game over. See [Drawing to the Screen](../concepts/display.md) for more about text.
- **A tune at game over.** Play a short melody when the lives run out. See [Sound & Music](../concepts/audio.md).
- **Rainbow lights.** Light the LEDs in a color that changes with the score. See [LEDs & Color](../concepts/leds.md).
- **Tilt to play.** Move the paddle by tilting the Cyber Fidget. See [Motion Sensing](../concepts/accelerometer.md) and [The Slider](../concepts/slider.md).
- **Look up anything else** in the [function reference](../reference/functions.md).
