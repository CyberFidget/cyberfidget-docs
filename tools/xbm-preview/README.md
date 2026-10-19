<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# XBM sprite previews

Turns the sprite bytes in the docs' code examples into small enlarged PNG pictures, so every byte array on a page can show the picture it makes. Lit pixels are white, unlit pixels dark grey, with a thin grid so single pixels are easy to count.

The bytes are read in XBM order, the same order `drawSprite()` and `display.drawXbm()` use: rows from top to bottom, `(width + 7) / 8` bytes per row, and the lowest bit of each byte is the leftmost pixel.

## Run

Python 3.9 or later, standard library only. From the docs repository root:

```sh
python tools/xbm-preview/xbm_preview.py           # write every image in images.json
python tools/xbm-preview/xbm_preview.py --check   # exit 1 if any image is missing or out of date
```

`--manifest PATH` reads another list instead of `images.json`. No servers, ports or environment variables are used.

## Add a picture

Add an entry to `images.json`:

```json
{"out": "docs/assets/sprites/my-sprite.png", "w": 8, "h": 8, "bytes": "0x3c, 0x42, 0xa5, 0x81, 0xa5, 0x99, 0x42, 0x3c"}
```

- `out`: the PNG to write, relative to the repository root.
- `w`, `h`: the sprite's width and height in pixels.
- `bytes`: the bytes exactly as the page's example writes them (every `0x..` value is read, in order).
- `scale` (optional, default 10): screen pixels per sprite pixel.

Copy the bytes from the page, run the script, and embed the PNG next to the code block with alt text that describes the picture. When an example's bytes change, update its entry and run the script again; `--check` catches a picture that no longer matches.
