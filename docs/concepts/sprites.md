# Sprites & Animation

By the end of this page you will draw small pictures from your code, make them animate, move them with the buttons and the slider, and check when two of them touch.

---

## What is this?

A **sprite** is a small picture your app draws on the screen: a character, a ball, a coin, a spark. On the Cyber Fidget every sprite is a **1-bit bitmap**. A bitmap is a picture stored as a grid of pixels, and 1-bit means each pixel is either on (lit) or off. There are no colors or grays, which matches the screen.

!!! tip "Like a rubber stamp"
    You make the stamp once. Then you can press it anywhere on the page, as often as you like. An animation is a stack of stamps you swap quickly, like a flip book.

The words on this page:

| Word | Meaning |
|------|---------|
| **Sprite** | One small 1-bit picture, plus its size and its pivot. |
| **Bitmap** | A picture stored as a grid of on/off pixels. |
| **XBM** | The way the bytes of a bitmap are laid out (see [Drawing a sprite](#drawing-a-sprite)). |
| **Pivot** | The point on a sprite that lands on the screen position you give. |
| **Frame** | One picture in an animation. |
| **Animation** | A named list of frames, how long each one shows, and what happens at the end. |
| **Sprite sheet** | A named group of animations that belong to one character or object. |
| **Actor** | A thing on the screen: a position plus an animation that is playing. |
| **Collision** | Two sprites touching, meaning a lit pixel of one sits on a lit pixel of the other. |

Every example on this page goes into a fresh [blank template](../getting-started/first-app.md) and works on its own. Paste each part where its first line says. Each example defines its own tiny sprite in code, so you can try it without drawing anything first.

---

## Getting art into your code

There are three ways to get a sprite into an app.

**1. Draw it in the Studio.** Open the **2D** tab of your project. Under **Project Files**, choose **New sprite**, give it a **Sprite name** such as `Ball`, and press **Create**. Draw it, and add frames and animations if you like (see [Animations and frames](../studio/animations-and-frames.md)). When you build the app, the Studio turns every sprite in the project into code and adds it to your app for you. There is nothing to export. See [Sprites travel with your app](../studio/your-sprite-library.md#sprites-travel-with-your-app).

Give sprites simple names: lowercase English letters and digits, starting with a letter, like `ball` or `hero2`. The Studio makes the name lowercase, turns each run of other characters (spaces, punctuation, accented letters) into one `_`, and trims `_` from both ends. A name starting with a digit gets `_` in front, and a second sprite with the same name gets `_2` on the end. For example, `Big Ball` becomes `big_ball`, `1UP` becomes `_1up`, and a second `Ball` becomes `ball_2`. A name with no usable letters or digits becomes `sprite`. Your code uses that name:

| Name in code | What it is |
|--------------|------------|
| `cf::gfx::ball::sheet` | The sprite sheet: all of the sprite's animations. |
| `cf::gfx::ball::anim_run` | The animation called `run`, if the sprite has one. |
| `cf::gfx::ball::cel_0` | The first frame as a single sprite (`cel_1` is the second, and so on). |

A sprite with no animations gets one called `idle`, which loops through all its frames. Animations drawn in the Studio loop. Each frame is trimmed to its lit pixels, and its pivot is the middle of the bottom edge of the canvas. **New sprite** starts with a canvas the size of the screen (128 x 64), so for those sprites, a pivot placed at (64, 64) puts the drawing exactly where you drew it on the canvas.

<!-- check-examples: skip - needs a sprite named Ball in the project's art -->
```cpp
// Insert at the top of the file, below the #include lines
#include "cf_gfx.h"
static cf::gfx::Actor ball;

// Insert inside begin(), below setColorsOff();
ball.setSheet(&cf::gfx::ball::sheet);
ball.setPos(64, 64);
ball.play("idle", millis());

// Insert inside update(), just above display.display();
ball.update(millis());
ball.draw(display);
```

**Press REBUILD.** You see the `idle` animation of a sprite named `Ball`, exactly where it was drawn. [Actors](#actors) explains each line.

**2. Copy a Starter Sprite.** In the 2D tab's library, **Starter Sprites** has free sprites anyone may reuse. **Copy as C++** puts one on your clipboard as code: an array of bytes named after the sprite, its width and height, and a credit line. See [Your Sprite Library](../studio/your-sprite-library.md#starter-sprites). Paste it at the top of your file, then wrap it in a `Sprite` (explained in [Drawing a sprite](#drawing-a-sprite)) to use the functions on this page:

```cpp
// Insert at the top of the file, below the #include lines
#include "cf_gfx.h"
using namespace cf::gfx;
// Code in the shape Copy as C++ gives you, for a made-up 4 x 4 sprite called dot.
const unsigned char dot_bmp[] PROGMEM = {
  0x06, 0x0f, 0x0f, 0x06
};
const int dot_w = 4;
const int dot_h = 4;
// Wrap it in a Sprite: bytes, width, height, pivot x, pivot y, bit order.
static const Sprite dot = {dot_bmp, dot_w, dot_h, 0, 0, BO_LSB_FIRST};

// Insert inside update(), just above display.display();
drawSprite(display, dot, 62, 50);
```

**Press REBUILD.** You see a small dot near the bottom of the screen.

`PROGMEM` marks constant picture data for storage in program memory on embedded boards. Keep it when copying sprite code; the Studio build supplies its definition.

**3. Write the bytes yourself.** For a tiny sprite this is quick, and it is what the examples on this page do.

!!! note "Short names for the sprite functions"
    The sprite functions live in `cf_gfx.h`, and their full names start with `cf::gfx::`, as in `cf::gfx::drawSprite`. That is how the [function reference](../reference/functions.md#sprites-and-animation) lists them.

    Studio apps already have `cf_gfx.h` and their generated project art available. You do not need to add those #include lines. The examples include `cf_gfx.h` explicitly so they also suit apps built into the firmware by hand; those apps also need their generated asset header if they use project art.

    The examples on this page write `using namespace cf::gfx;` once at the top of the file, which lets them use the short names (`drawSprite`, `Sprite`, `Actor`). Do the same when your project has no sprites of its own in **Project Files**. In that case the Studio stops any build whose code writes out a `cf::gfx::` name, with the message "The generated art couldn't be used, and the app's code depends on it - so this app won't build. Try generating again." Once the project has a sprite, the full names build too.

---

## Drawing a sprite

A `Sprite` holds six things: the bytes of the picture, its width and height in pixels, its pivot (x and y), and the bit order, which is always `BO_LSB_FIRST`. `drawSprite()` draws it with its top-left corner at the x, y you give.

```cpp
// Insert at the top of the file, below the #include lines
#include "cf_gfx.h"
using namespace cf::gfx;
// An 8 x 8 smiley face. Each byte is one row, top to bottom.
static const uint8_t smileBits[] = {
    0x3c, 0x42, 0xa5, 0x81, 0xa5, 0x99, 0x42, 0x3c
};
// bytes, width, height, pivot x, pivot y, bit order
static const Sprite smile = {smileBits, 8, 8, 0, 0, BO_LSB_FIRST};

// Insert inside update(), just above display.display();
display.clear();
drawSprite(display, smile, 60, 28);
```

**Press REBUILD.** You see an 8 x 8 smiley face in the middle of the screen.

The bytes are in **XBM** order. Each row of the picture uses one byte for every 8 pixels of width. Inside a byte, the lowest bit is the leftmost pixel. Take the first row, `0x3c`: in binary that is `00111100`. Read it from right to left and you get off, off, on, on, on, on, off, off: the top of the face. A sprite 10 pixels wide needs 2 bytes per row, and the unused bits are ignored.

`drawSprite()` uses the same drawing as `display.drawXbm()` (see [Bitmaps](display.md#bitmaps-drawxbm)). The difference is that a `Sprite` keeps its size and pivot with its bytes, so the other functions on this page can use it.

---

## Pivots

The **pivot** is the point on a sprite that lands on the screen position you give. With the pivot at the middle of the bottom edge, a character "stands" on the y you give, wherever its feet are. `drawSpritePivoted()` uses the pivot; `drawSprite()` ignores it.

```cpp
// Insert at the top of the file, below the #include lines
#include "cf_gfx.h"
using namespace cf::gfx;
static const uint8_t smileBits[] = {
    0x3c, 0x42, 0xa5, 0x81, 0xa5, 0x99, 0x42, 0x3c
};
// The pivot is (4, 8): the middle of the bottom edge.
static const Sprite smile = {smileBits, 8, 8, 4, 8, BO_LSB_FIRST};

// Insert inside update(), just above display.display();
display.clear();
display.drawHorizontalLine(16, 40, 96);
// The pivot lands on (40, 40), so the face sits on the line.
drawSpritePivoted(display, smile, 40, 40);
// drawSprite ignores the pivot: the top-left corner lands on (80, 40).
drawSprite(display, smile, 80, 40);
```

**Press REBUILD.** You see two faces and a horizontal line. The left face sits on the line. The right face hangs below it. Pivots can also sit outside the picture, and they can be negative.

---

## Animations and sprite sheets

An **animation** is a list of **frames** (sprites) and how long each one shows, in milliseconds (thousandths of a second). A **sprite sheet** groups the animations of one character, so you can pick one by name.

An `Animation` holds: its name, its frames, a list of times for each frame (or `nullptr` when every frame shows for the same time), that same time in milliseconds, the number of frames, and its [loop mode](#loop-modes). A `SpriteSheet` holds: its name, its animations, how many there are, and a kind (`"sprite"` is fine; the device does not use it).

An `AnimationPlayer` works out which frame to show. Start it with `play()`, call `update()` every frame with the time, and draw whatever `sprite()` returns.

```cpp
// Insert at the top of the file, below the #include lines
#include "cf_gfx.h"
using namespace cf::gfx;
static const uint8_t openBits[] = {0x3c, 0x42, 0xa5, 0xa5, 0x81, 0xbd, 0x42, 0x3c};
static const uint8_t shutBits[] = {0x3c, 0x42, 0x81, 0xa5, 0x81, 0xbd, 0x42, 0x3c};
static const Sprite eyesOpen = {openBits, 8, 8, 4, 8, BO_LSB_FIRST};
static const Sprite eyesShut = {shutBits, 8, 8, 4, 8, BO_LSB_FIRST};
// "blink": eyes open for 1.5 seconds, then shut for 0.15 seconds.
static const Sprite* const blinkFrames[] = {&eyesOpen, &eyesShut};
static const uint16_t blinkTimes[] = {1500, 150};
// "stare": one frame. A time of 0 holds the frame forever.
static const Sprite* const stareFrames[] = {&eyesOpen};
// name, frames, frame times, time for every frame, frame count, loop mode
static const Animation faceAnimations[] = {
    {"blink", blinkFrames, blinkTimes, 0, 2, LOOP_LOOP},
    {"stare", stareFrames, nullptr, 0, 1, LOOP_LOOP},
};
static const SpriteSheet face = {"face", faceAnimations, 2, "sprite"};
static AnimationPlayer blinker;

// Insert inside begin(), below setColorsOff();
blinker.play(findAnimation(face, "blink"), millis());

// Insert inside update(), just above display.display();
display.clear();
blinker.update(millis());
// sprite() is nullptr when there is nothing to draw.
if (blinker.sprite()) drawSpritePivoted(display, *blinker.sprite(), 64, 40);
```

`&eyesOpen` means "the address of `eyesOpen`": where that sprite is stored in memory. `blinkFrames` and `stareFrames` are arrays (lists) of pointers, values that hold those addresses. They refer to the sprites without copying their picture data. `const Sprite* const` keeps both the pictures and the addresses in the list unchanged.


**Press REBUILD.** You see a face that blinks every 1.65 seconds.

`findAnimation()` looks up an animation in a sheet by name. It returns `nullptr` when there is no animation with that name, and `play(nullptr, ...)` stops the player, so a typo shows nothing at all. Change `"blink"` to `"stare"` to see the other animation.

`play()` always starts again from the first frame. `setIfChanged()` starts only when you pass a different animation, so it is safe to call every frame. `frameIndex()` tells you which frame is showing, starting at 0, and `stop()` clears the player.

---

## Actors

An **actor** is a sprite sheet, an animation player and a screen position in one object. Most game characters are actors. Its position is where its pivot lands.

```cpp
// Insert at the top of the file, below the #include lines
#include "cf_gfx.h"
using namespace cf::gfx;
static const uint8_t openBits[] = {0x3c, 0x42, 0xa5, 0xa5, 0x81, 0xbd, 0x42, 0x3c};
static const uint8_t shutBits[] = {0x3c, 0x42, 0x81, 0xa5, 0x81, 0xbd, 0x42, 0x3c};
static const Sprite eyesOpen = {openBits, 8, 8, 4, 8, BO_LSB_FIRST};
static const Sprite eyesShut = {shutBits, 8, 8, 4, 8, BO_LSB_FIRST};
static const Sprite* const blinkFrames[] = {&eyesOpen, &eyesShut};
static const uint16_t blinkTimes[] = {1500, 150};
static const Animation faceAnimations[] = {
    {"blink", blinkFrames, blinkTimes, 0, 2, LOOP_LOOP},
};
static const SpriteSheet face = {"face", faceAnimations, 1, "sprite"};
static Actor hero;

// Insert inside begin(), below setColorsOff();
hero.setSheet(&face);
hero.setPos(64, 40);
hero.play("blink", millis());

// Insert inside update(), just above display.display();
display.clear();
hero.update(millis());
hero.draw(display);
```

**Press REBUILD.** You see a blinking face standing at (64, 40). `&face` passes the address of the sprite sheet to the actor.

- `setSheet()` gives the actor its sprite sheet, so `play()` can find animations by name. `play()` returns `false` and changes nothing when the name is not in the sheet.
- `play()` on an actor does not restart an animation that is already playing, so you can call it every frame, for example `hero.play(moving ? "run" : "idle", millis())`. You can also pass an animation itself instead of a name: `hero.play(&faceAnimations[0], millis())`.
- `update()` moves the animation on. `draw()` draws the current frame with its pivot at the actor's position.
- `x()` and `y()` read the position. `sprite()`, `animation()` and `finished()` tell you what is showing.

### Moving an actor

Change the position each frame and the actor moves. `setPos()` takes whole pixels. For smooth slow movement, `setPosQ8()` takes fractions of a pixel: 256 units are one pixel, so adding 128 each frame moves half a pixel per frame. `xQ8()` and `yQ8()` read the position in the same units.

This example moves a face up and down with the slider and left and right with the middle buttons.

```cpp
// Insert at the top of the file, below the #include lines
#include "cf_gfx.h"
using namespace cf::gfx;
static const uint8_t smileBits[] = {
    0x3c, 0x42, 0xa5, 0x81, 0xa5, 0x99, 0x42, 0x3c
};
static const Sprite smile = {smileBits, 8, 8, 4, 8, BO_LSB_FIRST};
static const Sprite* const stillFrames[] = {&smile};
static const Animation still = {"still", stillFrames, nullptr, 0, 1, LOOP_LOOP};
static Actor hero;

// Insert inside begin(), below setColorsOff();
hero.setPos(64, 40);
hero.play(&still, millis());

// Insert inside update(), just above display.display();
// Slider at the top: face at the top.
int32_t y = map(sliderPosition_8Bits_Inverted_Filtered, 0, 255, 56, 16);
// Middle-left and middle-right buttons: half a pixel per frame.
int32_t x = hero.xQ8();
if (buttonManager.isPressed(button_MiddleLeftIndex)) x -= 128;
if (buttonManager.isPressed(button_MiddleRightIndex)) x += 128;
x = constrain(x, (int32_t)(12 * 256), (int32_t)(116 * 256));
hero.setPosQ8(x, y * 256);
hero.update(millis());
display.clear();
hero.draw(display);
```

**Press REBUILD.** The slider moves the face up and down. Hold a middle button to move it sideways.

`buttonManager.isPressed()` is true while a button is held down, which suits movement. For one action per press, use a callback instead (see [Buttons & Events](buttons.md)). `constrain()` keeps the face away from the screen edges.

---

## Loop modes

An animation's loop mode says what happens after its last frame.

| Loop mode | What happens after the last frame |
|-----------|-----------------------------------|
| `LOOP_LOOP` | Starts again from the first frame, forever. |
| `LOOP_PINGPONG` | Plays backward to the first frame, then forward again, forever. |
| `LOOP_ONCE_HOLD` | Stops and keeps showing the last frame. `finished()` becomes true. |
| `LOOP_ONCE` | Stops and shows nothing: `sprite()` returns `nullptr`. `finished()` becomes true. |

A frame time of 0 holds that frame forever, whatever the loop mode.

This example grows a square once and holds it. Press the middle-right button to play it again. Change `LOOP_ONCE_HOLD` to each of the other modes and rebuild to compare them.

```cpp
// Insert at the top of the file, below the #include lines
#include "cf_gfx.h"
using namespace cf::gfx;
static const uint8_t smallBits[] = {0x00, 0x00, 0x00, 0x18, 0x18, 0x00, 0x00, 0x00};
static const uint8_t middleBits[] = {0x00, 0x00, 0x3c, 0x3c, 0x3c, 0x3c, 0x00, 0x00};
static const uint8_t bigBits[] = {0x00, 0x7e, 0x7e, 0x7e, 0x7e, 0x7e, 0x7e, 0x00};
// The pivot (4, 4) is the middle, so the square grows from its center.
static const Sprite growSmall = {smallBits, 8, 8, 4, 4, BO_LSB_FIRST};
static const Sprite growMiddle = {middleBits, 8, 8, 4, 4, BO_LSB_FIRST};
static const Sprite growBig = {bigBits, 8, 8, 4, 4, BO_LSB_FIRST};
static const Sprite* const growFrames[] = {&growSmall, &growMiddle, &growBig};
static const Animation grow = {"grow", growFrames, nullptr, 300, 3, LOOP_ONCE_HOLD};
static AnimationPlayer grower;
static void onReplay(const ButtonEvent& e) {
    if (e.eventType == ButtonEvent_Pressed) grower.play(&grow, millis());
}

// Insert inside begin(), below setColorsOff();
grower.play(&grow, millis());
buttonManager.registerCallback(button_MiddleRightIndex, onReplay);

// Insert inside update(), just above display.display();
grower.update(millis());
display.clear();
if (grower.sprite()) drawSpritePivoted(display, *grower.sprite(), 64, 28);
display.setFont(ArialMT_Plain_10);
display.drawString(64, 44, grower.finished() ? "Finished" : "Playing");

// Insert inside end(), above unregisterButtonCallbacks();
buttonManager.unregisterCallback(button_MiddleRightIndex);
```

**Press REBUILD.** A square grows, then stays large with "Finished" below it. Press the middle-right button to replay it.

---

## Collision

A **collision** is two sprites touching. `pixelCollides()` answers "do any lit pixels of these two sprites overlap?". Blank corners of a sprite do not count, so a round ball only hits what touches its round edge.

There are two forms:

- `pixelCollides(spriteA, ax, ay, spriteB, bx, by)` takes two sprites and the **top-left** corner of each, the same positions you give `drawSprite()`.
- `pixelCollides(actorA, actorB)` takes two actors and uses their positions and pivots for you.

Do not mix them: if you draw with pivots, give the sprite form top-left positions, or use the actor form.

```cpp
// Insert at the top of the file, below the #include lines
#include "cf_gfx.h"
using namespace cf::gfx;
static const uint8_t smileBits[] = {
    0x3c, 0x42, 0xa5, 0x81, 0xa5, 0x99, 0x42, 0x3c
};
static const Sprite smile = {smileBits, 8, 8, 0, 0, BO_LSB_FIRST};
// A small 3 x 2 block.
static const uint8_t blockBits[] = {0x07, 0x07};
static const Sprite block = {blockBits, 3, 2, 0, 0, BO_LSB_FIRST};

// Insert inside update(), just above display.display();
display.clear();
// The slider moves the block from left to right, across the top of the face.
int blockX = map(sliderPosition_8Bits_Inverted_Filtered, 0, 255, 40, 80);
drawSprite(display, smile, 60, 28);
drawSprite(display, block, blockX, 28);
if (pixelCollides(smile, 60, 28, block, blockX, 28)) {
    HAL::setRgbLed(pixel_Front_Middle, 255, 0, 0, 0);
    display.drawString(64, 44, "Touching");
} else {
    HAL::setRgbLed(pixel_Front_Middle, 0, 0, 0, 0);
}
```

**Press REBUILD.** You see a face and a small block. Slide slowly to move the block. The two sprites' boxes overlap a little before "Touching" appears, because the face's top corners are blank. The starter's `end()` turns the LED off when the app closes.

### Reading single pixels

`sampleSprite(sprite, x, y)` tells you whether one pixel of a sprite is lit. The x and y count from the sprite's own top-left corner, and anything outside the sprite reads as off. This example uses it to draw the face four times bigger.

```cpp
// Insert at the top of the file, below the #include lines
#include "cf_gfx.h"
using namespace cf::gfx;
static const uint8_t smileBits[] = {
    0x3c, 0x42, 0xa5, 0x81, 0xa5, 0x99, 0x42, 0x3c
};
static const Sprite smile = {smileBits, 8, 8, 0, 0, BO_LSB_FIRST};

// Insert inside update(), just above display.display();
display.clear();
for (int y = 0; y < 8; y++) {
    for (int x = 0; x < 8; x++) {
        if (sampleSprite(smile, x, y)) display.fillRect(48 + x * 4, 16 + y * 4, 4, 4);
    }
}
```

**Press REBUILD.** You see the smiley face enlarged to 32 x 32 pixels.

---

## Functions on this page

--8<-- "includes/reference/sprites.md"

## Where to go next

- [Make a game, step by step](../getting-started/make-a-game.md): a whole game built up in small steps.
- [Drawing to the Screen](display.md): text, shapes and `drawXbm()`.
- [The Update Loop](update-loop.md): timing with `millis()`.
- [Studio overview](../studio/overview.md): drawing sprites and animations in the 2D tab.
- [Function reference](../reference/functions.md#sprites-and-animation): every sprite and animation call.
