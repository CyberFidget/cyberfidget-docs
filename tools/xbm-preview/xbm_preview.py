# SPDX-License-Identifier: GPL-3.0-or-later
"""Render XBM sprite bytes from the docs as small enlarged PNG pictures.

Each entry in images.json names an output file, a width, a height and the
bytes exactly as a page's code example writes them. Lit pixels are white,
unlit pixels dark grey, with a thin grid so single pixels are easy to count.
Standard library only.
"""
import argparse
import json
from pathlib import Path
import re
import struct
import sys
import zlib

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
LIT = (255, 255, 255)
UNLIT = (40, 40, 48)
GRID = (16, 16, 20)


def parse_bytes(text):
    """Read 0x.. values (or a list of ints) into a list of byte values."""
    if isinstance(text, list):
        return [int(v) for v in text]
    return [int(v, 16) for v in re.findall(r"0x([0-9a-fA-F]{1,2})", text)]


def pixels(data, w, h):
    """XBM order: rows top to bottom, (w + 7) // 8 bytes per row, lowest bit leftmost."""
    per_row = (w + 7) // 8
    if len(data) < per_row * h:
        raise ValueError(f"{w} x {h} needs {per_row * h} bytes, got {len(data)}")
    return [[bool(data[y * per_row + x // 8] >> (x % 8) & 1) for x in range(w)] for y in range(h)]


def png(rows_rgb, width, height):
    raw = b"".join(b"\x00" + bytes(row) for row in rows_rgb)

    def chunk(kind, payload):
        body = kind + payload
        return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def render(data, w, h, scale):
    grid = pixels(data, w, h)
    out_w = w * scale + 1
    out_h = h * scale + 1
    rows = []
    for py in range(out_h):
        row = []
        for px in range(out_w):
            if px % scale == 0 or py % scale == 0:
                colour = GRID
            elif grid[py // scale][px // scale]:
                colour = LIT
            else:
                colour = UNLIT
            row.extend(colour)
        rows.append(row)
    return png(rows, out_w, out_h)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", default=str(HERE / "images.json"), help="list of images to write (default: images.json here)")
    parser.add_argument("--check", action="store_true", help="exit 1 if any image is missing or out of date, without writing")
    args = parser.parse_args(argv)

    entries = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    stale = []
    for entry in entries:
        out = REPO / entry["out"]
        data = render(parse_bytes(entry["bytes"]), entry["w"], entry["h"], entry.get("scale", 10))
        if args.check:
            if not out.exists() or out.read_bytes() != data:
                stale.append(entry["out"])
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        print(f"wrote {entry['out']} ({entry['w']} x {entry['h']})")
    if stale:
        print("Out of date: " + ", ".join(stale) + "\nRun: python tools/xbm-preview/xbm_preview.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
