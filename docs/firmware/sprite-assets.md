# Sprite assets in built-in apps

After this page you can add a sprite to a built-in app, put it where the build expects it, and keep the generated code in step with the drawing.

This page is for firmware contributors. If you are making an app in the studio, the studio does all of this for you: see [Sprites & Animation](../concepts/sprites.md).

---

## What is this?

A built-in app draws its pictures from **generated headers**. A generated header is a C++ file that a tool writes for you from a sprite drawing, so you never type the bitmap bytes by hand.

Each sprite has two files:

| File | Folder | You edit it? |
|---|---|---|
| The sprite drawing, `<name>.cfsprite.json` | `lib/<App>/assets/` | Yes. This is the source. |
| The generated header, `<name>.h` | `lib/<App>/generated/` | No. The tool writes it, and both files are committed. |

The Dino game is a real example. `lib/DinoGame/assets/` holds `cactus.cfsprite.json`, `dino.cfsprite.json`, `ground.cfsprite.json` and `pterodactyl.cfsprite.json`. `lib/DinoGame/generated/` holds the matching `cactus.h`, `dino.h`, `ground.h` and `pterodactyl.h`.

The first lines of every generated header say so: "Generated from .cfsprite.json. Edit the source asset, not this header."

---

## Step 1: author the sprite

Draw the sprite in the studio's sprite editor and save it with **Save to file** in the **Sprite file** menu. The result is a `.cfsprite.json` file. See [Files and Versions](../studio/files-and-versions.md) for where the menu is.

A `.cfsprite.json` file records the sprite's size, its pivot (the point placed at the screen position), its frames and its named animations. The Dino cactus is a good small file to read: one 8 by 16 frame and one looping animation called `idle`.

---

## Step 2: put it in the app's assets folder

Save the file as `lib/<App>/assets/<name>.cfsprite.json`. The build finds sprites with the pattern `lib/*/assets/*.cfsprite.json`, so the folder name and the ending both matter.

For an app called `MyApp` and a sprite called `coin`:

```text
lib/MyApp/assets/coin.cfsprite.json     <- you add this
lib/MyApp/generated/coin.h              <- the tool writes this
```

The part of the file name before `.cfsprite.json` is the **symbol prefix**. It becomes the C++ namespace the header defines, so use a short lowercase name made of letters, digits and underscores. The cactus file gives `cf::gfx::cactus`.

If two sprites would write to the same `generated/` file, the build stops with an "Asset header collision" error.

---

## Step 3: regenerate the header

Run the `cfsprite-regen` target. A **PlatformIO target** is a named extra job you run with `-t`. This one rewrites every generated header from its drawing:

```bash
pio run -t cfsprite-regen
```

It prints one line per file, for example `Generated lib/DinoGame/generated/cactus.h`. Commit the new or changed `.h` next to the `.cfsprite.json`.

The target needs two things on your computer:

- **Node.js**, the JavaScript runtime that runs the tool. Without it the target stops with "Node.js is required".
- **The sprite compiler**, the program that turns the drawing into C++. It ships with the Cyber Fidget website source. The tool looks for it in a folder named `cyberfidget_website` next to the firmware folder (`assets/js/cfsprite_compile.mjs`). If yours is somewhere else, set the `CF_CFSPRITE_COMPILER` environment variable to its full path.

If the compiler cannot be found, regeneration fails on purpose rather than skipping.

---

## Step 4: use the sprite in your app

Include the header and point an actor at the sheet. The Dino game does this in `lib/DinoGame/DinoGame.h` with `#include "generated/dino.h"`, and in `lib/DinoGame/DinoGame.cpp` with:

```cpp
dinoActor.setSheet(&cf::gfx::dino::sheet);
dinoActor.play(cf::gfx::dino::anim_run, millis());
```

`sheet` is the whole set of animations. Each animation also gets a name of the form `anim_<animation name>`.

---

## The drift check

**Drift** means a generated header no longer matches the drawing it came from, usually because someone edited the drawing and forgot to regenerate. The **drift check** catches this.

It runs automatically at the start of every firmware build (`pio run`, including `pio run -e local`). For each sprite it asks the compiler to produce the header again and compares the result with the committed file. Line endings are ignored, so a Windows checkout does not cause false alarms.

If a header has drifted, the build stops with:

```text
Generated header drift: lib/DinoGame/generated/cactus.h
Regenerate target: pio run -t cfsprite-regen
```

Run the regenerate step above, then commit the updated header.

You can also run the check by hand for one sprite:

```bash
node tools/cfsprite_compile_cli.mjs --check-only --symbol-prefix cactus lib/DinoGame/assets/cactus.cfsprite.json lib/DinoGame/generated/cactus.h
```

!!! note "The check can be skipped"
    If Node.js or the sprite compiler is missing, the build prints `WARNING - asset drift check SKIPPED` and carries on, because the committed headers already compile. The automated build on GitHub does not have the compiler, so it skips the check. Run the build on your own computer, with the compiler present, before you commit sprite changes.

---

## Advanced

Studio apps do not need this section.

- The same build hook also handles 3D models: `.cfmesh.json` files in `lib/<App>/assets/` become headers in `lib/<App>/generated/`, regenerated with `pio run -t cfmesh-regen`. See [3D Models](../studio/3d-models.md).
- `tools/legacy_xbm_to_cfsprite.mjs` converts older hand-written XBM bitmap arrays (like those in `lib/DinoGame/DinoSprites.h`) into `.cfsprite.json` files.
- The hook is `scripts/cfsprite_assets.py`, listed under `extra_scripts` in `platformio.ini`. The command-line compiler wrapper is `tools/cfsprite_compile_cli.mjs`.

See also: [Firmware development](index.md) and [How an App Works](../concepts/app-lifecycle.md).
