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

Clips are WebM (VP8), cropped to the relevant region and kept short. Each clip has a poster PNG with the same base name.

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
2. Start from `newBlankApp(page, r.base, 'Hello')` (creates a blank-template app with that App Name).
3. For stills, call `r.shot(page, 'file-name', clip)`. `clip` is optional: `{ x, y, width, height }` in page pixels (the page is 1280 x 800).
4. For a clip, `const rec = r.recorder('file-name'); const page = await rec.open();`, do the steps, note `rec.now()` at the start and end, and finish with `await rec.finish({ from, to, region })`. The region crops the video; `WORKSPACE`, `DEVICE` and `EMU_COLUMN` are ready-made regions. A yellow dot follows the mouse in recorded pages, so click paths are visible.
5. Use only labels that exist in the studio. Check them against `inc/studio-body.php`, `assets/js/builder.js` and the components of the website before writing selectors, and add short pauses (`sleep`) so a viewer can follow.
6. Keep a loop in mind: the clip's last frame should flow back into its first.

## Use a clip in a page

MkDocs has `md_in_html` and `attr_list` enabled, so a page can embed a clip like this (the path is relative to the page):

```html
<video src="../assets/media/new-sprite.webm" poster="../assets/media/new-sprite.png" autoplay loop muted playsinline width="480"></video>
```

Write alt-style text next to the clip describing what it shows. For a single state, use the PNG instead.

## Limits

- The clips are only as stable as the studio's labels and layout. A failing scene prints the step that failed; fix the selector or the label and re-run it.
- The emulator clips drive the emulator's slider and buttons through the page, not a real device.
- Clips are recorded in real time, so durations vary by a fraction of a second between runs.
