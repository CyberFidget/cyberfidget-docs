<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Media capture

Drives the studio in a headless browser and writes the documentation's screenshots and short looping clips into `docs/assets/media/`. Every capture is a named **scene** in `capture.mjs`, so when the studio changes you re-run one scene instead of redoing media by hand. It runs signed out and never submits anything to a device or an account.

## What it writes

| Scene | Files |
|-------|-------|
| `new-sprite` | `new-sprite.webm` + `.png` (clip and poster); `new-sprite-add-art-menu.png`, `new-sprite-dialog.png`, `new-sprite-drawn.png` |
| `free-starters-copy` | `free-starters-copy.webm` + `.png`; `free-starters-tab.png`, `free-starters-copy-as-cpp.png`, `free-starters-pasted.png` |
| `add-art-from-file` | `add-art-menu.png`, `add-art-all-files.png`, `add-art-upload-your-own.png`, `add-art-2d-no-art.png`, `add-art-sprite-file-menu.png` |
| `emulator-catcher` | `emulator-catcher.webm` + `.png`: the finished Make a game listing, played with the emulator's slider |
| `emulator-sprites` | `emulator-sprites.webm` + `.png`: the "Moving an actor" example from the Sprites page |
| `rebuild-and-run` | `rebuild-and-run.webm` + `.png`; `rebuild-and-run-done.png` |
| `3d-new-model` | `3d-new-model.webm` + `.png`: 3D tab, **Add art > Build a 3D model**, name, **Create**; `3d-add-art-menu.png`, `3d-new-model-dialog.png`, `3d-new-model-blank.png`, `3d-starter-models.png` |
| `3d-add-points-lines` | `3d-add-points-lines.webm` + `.png`: **Add point** with Mirror on, then **Connect**, then a turn of the view; `3d-add-points-lines-done.png` |
| `3d-move-rotate-view` | `3d-move-rotate-view.webm` + `.png`: the SHIP starter turned, zoomed, a point dragged (its twin follows), a line selected, Mirror off, Undo; `3d-move-rotate-view-mirror-off.png` |
| `3d-try-in-app` | `3d-try-in-app.webm` + `.png` (the click path) and `3d-try-in-app-emulator.webm` + `.png` (the viewer app spinning, zoomed with the slider); `3d-use-in-code.png`, `3d-try-in-app-running.png` |
| `2d-drawing-tools` | `2d-drawing-tools.webm` + `.png`: Draw, Line, Rectangle, Oval, Fill and Erase on a new sprite; `2d-tool-bar.png`, `2d-drawing-tools-done.png` |
| `2d-layers` | `2d-layers.webm` + `.png`: **New layer**, drawing on it, hiding and showing a layer, picking a layer, the layer's menu; `2d-layers-menu.png` |
| `2d-animation-frames` | `2d-animation-frames.webm` + `.png`: **+ Frame** and **Move** to make a ball roll, then the preview and **Speed**; `2d-animation-frames-preview.png` |

Clips are WebM (VP8), cropped to the relevant region and kept short. Each clip has a poster PNG with the same base name.

The `3d-` scenes need the studio's 3D tab, which only appears for visitors who have it turned on. The tool turns it on inside its own browser: it answers the studio's feature lookup (`/api/user-features.php`) with "3D on" for a signed-out visitor, the same way the website's own browser tests do. Nothing on the server changes and no account is used.

The two emulator clips take their code from the docs themselves: `emulator-catcher` uses the final listing on `getting-started/make-a-game.md` (the block after `check-examples: final`), and `emulator-sprites` assembles the "Moving an actor" fragments from `concepts/sprites.md` into the blank template. If those pages change, re-run the scene and the clip follows.

## Prerequisites

- Node.js 18 or later.
- Playwright, with its Chromium browser installed. Either:
  - run `npm install` and `npx playwright install chromium` in this folder; or
  - point at a folder that already has it: set `PLAYWRIGHT_DIR` to a directory whose `node_modules` contains `playwright` (for example another project checkout).
- A running copy of the studio site (the `--base` URL). Any PHP-served checkout of the website works, for example `php -S localhost:8481 -t .` from the website folder.
- Optional: ffmpeg with the libvpx encoder, for cropping and trimming clips. The tool uses the small ffmpeg that Playwright installs next to its browsers (`ms-playwright/ffmpeg-*`), or the one named by the `FFMPEG` environment variable. Without ffmpeg, clips are kept as recorded (whole page, untrimmed) and no poster is written.

## Run

From this folder:

```sh
node capture.mjs --list                      # list the scenes
node capture.mjs new-sprite                  # one scene
node capture.mjs emulator-catcher rebuild-and-run
node capture.mjs all --base http://localhost:8481
node capture.mjs all --out /some/other/folder
```

| Option | Meaning |
|--------|---------|
| `--base URL` | The studio site (default `http://localhost:8000`). The tool opens `<base>/create/`. |
| `--out DIR` | Output folder (default `docs/assets/media`). |
| `--headed` | Show the browser while it works. |

Running a scene overwrites its files. Review the new media (open the PNGs, play the clips) before committing.

## Add a scene

1. Add a function to the `scenes` table in `capture.mjs`: `scenes['my-scene'] = async (r) => { ... }`.
2. Do the setup first (new project, open a tab, make a sprite), then note `const start = rec.now()`. Only what happens after `start` ends up in the clip. Setup helpers take a last argument `show`; pass `false` to click instantly.
3. For stills, call `r.shot(page, 'file-name', clip)`. `clip` is optional: `{ x, y, width, height }` in page pixels (the page is 1280 x 800).
4. For a clip, `const rec = r.recorder('file-name'); const page = await rec.open();` (add `{ models: true }` for the 3D tab), do the steps, and finish with `await rec.finish({ from: start, to: rec.now(), region })`.
5. Use only labels that exist in the studio. Check them against `inc/studio-body.php`, `assets/js/builder.js`, `assets/js/studio.js` and the components of the website before writing selectors.
6. Add the scene and its files to the table above.

## Driving the emulator

Every scene follows the same pattern, and `capture.mjs` has a small helper for each part. Reuse them rather than writing new page code.

### Open the studio and start a project

| Helper | What it does |
|--------|--------------|
| `openStudio(page, base)` | Opens `<base>/create/` and waits for the landing page. |
| `newBlankApp(page, base, 'Hello')` | **Create an app > Code from Blank Template**, with that App Name: a project whose code is the blank template. |
| `newEmptyProject(page, base)` | **Create an app** only: a project with no app code yet (what **Try it in an app** needs to write its viewer app). |
| `openTab(page, 'pixel')` | Clicks a tab in the rail: `builder` (Generate), `ide` (Code), `pixel` (2D), `model` (3D), `settings`. |
| `newSprite(page, 'Ball')`, `newModel(page, 'Arrow')` | **Add art > Draw a new sprite** or **Build a 3D model**, type the name, **Create**. |
| `addStarterModel(page, 'ship')` | **All files > Free starters**, then a starter model (`ship`, `cube`, `pyramid`). |
| `dismissToast(page)` | Closes the "Added ..." note under the file strip, so it is not in the clip. |

### Put full code in the editor and build

- `setCode(page, code)` replaces the code in the visible editor. Take the code from the docs, so the clip follows the page: `finalListing('getting-started/make-a-game.md')` (the listing after `check-examples: final`), or `assembleFragments(await readEditorCode(page), docsBlock('concepts/sprites.md', 'some line'))` to put an "Insert ..." example into the blank template the way a reader does.
- `rebuildAndRun(page)` clicks **REBUILD & RUN** (the first build of a project; later builds use **REBUILD**) and waits until the emulator says it is running your app. `waitForApp(page)` only waits, for builds started some other way (**Try it in an app** starts one by itself).
- A build takes from a few seconds to about a minute. Don't keep the wait in a clip: cut one clip before it and one after (see "Cut, crop and time a clip").

### Play the emulator with the mouse

- Blur the editor first (`page.evaluate(() => document.activeElement.blur())`), so key presses and clicks reach the emulator.
- **Slider:** `sliderGrab(page, 50)` presses the mouse on the slider at that value (0 = bottom, 100 = top) and keeps it held; `sliderTo(page, value, steps)` moves it while held; `page.mouse.up()` lets go.
- **Buttons:** `pressButton(page, 'MiddleRight', 300)` moves the mouse onto that emulator button and holds it for 300 ms. Names: `TopLeft`, `TopRight`, `MiddleLeft`, `MiddleRight`, `BottomLeft`, `BottomRight`. Keys work too (Q, E, A, D, Z, C).
- **Read the screen:** `const lit = await readScreen(page)` returns `lit(x, y)` for the 128 x 64 device pixels. Use it to react to the game, as `emulator-catcher` does: it finds the falling dot and the paddle every 30 ms and moves the slider to catch (or miss) the dot.

### Show the mouse

Headless video does not draw the mouse. Recorded pages get a yellow dot that follows it and shrinks on a click; `r.shot()` hides it in stills. Use `tap(page, locator)`, `clickAt(page, x, y)`, `drag(page, [p1, p2, ...])` and `glide(page, x, y)`: they move the dot smoothly, so a viewer sees where each click lands. Pass `{ cursor: false }` to `rec.open()` for clips of the device alone.

For the 2D canvas, `tool2d(page, 'Line')` finds a tool, and `pixelAt(page, x, y)` and `drawPixels(page, [[x, y], ...])` work in sprite pixels. For the 3D stage, `modelPoint`, `modelLineMiddle`, `stageSpotFor`, `orbitTo` and `zoomTo` work in model units and view angles, using the editor state the studio exposes for its own tests (`window.__cfModelEditor.debugState()`).

### Cut, crop and time a clip

- `rec.finish({ from, to, region, width, posterAt })` keeps `from` to `to` seconds of the recording, crops it to `region` and scales it to `width` pixels wide. The ready-made regions are `WORKSPACE`, `STUDIO_PANEL` (rail and 2D or 3D workspace), `WHOLE_STUDIO`, `DEVICE` and `EMU_COLUMN`.
- Pass an array to cut several clips from one recording; each extra one has its own `name`. `3d-try-in-app` does this to leave out the build: one clip up to the click, one of the running app.
- The poster PNG is the frame at `posterAt` seconds. Pick a frame that shows the result (often `end - start - 0.3`), or the starting state when the clip is about a click path.
- Aim for 4 to 15 seconds. Pause (`sleep`) 300 to 900 ms after each step so a viewer can follow. End close to where the clip started, so the loop doesn't jump.
- Keep each clip under about 1.5 MB: crop to the part that matters, scale wide regions down (`width: 700` to `900`), and keep it short. The encoder runs at 20 frames a second and 900 kbit/s.

## Use a clip in a page

MkDocs has `md_in_html` and `attr_list` enabled, so a page can embed a clip like this (the path is relative to the page):

```html
<video src="../assets/media/new-sprite.webm" poster="../assets/media/new-sprite.png" autoplay loop muted playsinline width="480"></video>
```

Raw HTML is not rewritten by MkDocs, so a clip's path is relative to the page's address: a page in `docs/studio/` is served at `/studio/<page>/`, so its clips are `../../assets/media/...`. Markdown images (`![...](...)`) are relative to the source file instead (`../assets/media/...`).

Write alt-style text next to the clip describing what it shows. For a single state, use the PNG instead.

## Limits

- The clips are only as stable as the studio's labels and layout. A failing scene prints the error and the line of `capture.mjs` it came from; fix the selector or the label and re-run it.
- Playwright's small ffmpeg can crop, scale and trim, but not join pieces of video, which is why a long wait is left out by cutting two clips.
- The emulator clips drive the emulator's slider and buttons through the page, not a real device.
- Clips are recorded in real time, so durations vary by a fraction of a second between runs.
