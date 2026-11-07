# SPDX-License-Identifier: GPL-3.0-or-later
"""Capture a real Cyber Fidget's screen over USB serial, for the docs.

Drives the device with its serial commands (`btn <index> tap` presses a
button, `screencap` returns the 128 x 64 screen) and writes each screen as a
PNG. Steps come from the command line, in order:

    python device_screens.py --port COM30 --out ../../docs/assets/media \
        shot:menu-home btn:1 wait:0.6 shot:menu-second cmd:menutree

    shot:<name>   capture the screen to <out>/<name>.png
    enter:<name>  capture the screen, check it (see below), write it to
                  <out>/<name>.png, then press Enter (the bottom-right button)
    btn:<index>   tap a button (0 up, 1 down, 2 left, 3 right, 4 back);
                  Enter (5) is only pressed through enter:<name>
    wait:<sec>    pause
    cmd:<text>    send any serial command and print what it answers

Guards, so a missed press or a changed menu can't open the wrong thing:

- enter:<name> presses Enter only when the screen matches the reference
  frame <expect>/<name>.png (default <expect> is <out>), ignoring the top
  status row. With no reference frame it stops, unless --allow-unchecked-enter
  is given (for building a new walk; the checks below still apply).
- Enter is never pressed while the firmware update popup is on screen (its
  first choice is "Install now"), or while the running app (the `app`
  command's answer) is one that erases or resets something.
- Left and right change the saved preset on the Speaker EQ screen. The first
  time they are pressed there, the screen is remembered; at the end of the
  run, even after an error or Ctrl+C, the tool opens Speaker EQ again and
  steps until the screen matches it, so the preset is left as found.
- The awake setting is read at the start and set back at the end. If it was
  off, the run keeps the device awake (`awake set stay until`) meanwhile.

Opening the port follows the bench rules: reset dance, then poll `version`
until the command line answers. Needs pyserial (PlatformIO's Python has it).
"""
import argparse
import base64
import os
import re
import struct
import sys
import time
import zlib

import serial

BAUD = 921600
W, H = 128, 64
# Rows compared with a reference frame: below the menu's status row (clock,
# battery), which changes from run to run.
CHECK_ROWS = range(12, H)
# Differing pixels allowed in those rows when matching a reference frame.
MATCH_LIMIT = 40
# Apps whose screens erase or reset something: Enter is never pressed in them.
REFUSE_APPS = ("Reset to factory",)
EQ_APP = "Speaker EQ"
EQ_PRESETS = 3


class Device:
    def __init__(self, port):
        self.s = serial.Serial(port, BAUD, timeout=0.25)
        self.buf = b""
        # Opening the port leaves DTR/RTS undefined, which can wedge the
        # command line: reset the board, then wait until it answers.
        self.s.dtr = False
        self.s.rts = True
        time.sleep(0.1)
        self.s.rts = False
        deadline = time.time() + 25
        while time.time() < deadline:
            time.sleep(1.0)
            self.s.reset_input_buffer()
            self.buf = b""
            self.send("version")
            for line in self.lines(1.5):
                if "version=" in line:
                    self.version = line.split("version=", 1)[1].split()[0]
                    return
        raise RuntimeError("the device never answered on " + port)

    def send(self, text):
        self.s.write((text + "\n").encode())
        self.s.flush()

    def lines(self, timeout):
        out = []
        end = time.time() + timeout
        while time.time() < end:
            self.buf += self.s.read(4096)
            while b"\n" in self.buf:
                raw, self.buf = self.buf.split(b"\n", 1)
                out.append(raw.decode("utf-8", "replace").strip())
        return out

    def ask(self, text, want, timeout=3.0):
        self.send(text)
        end = time.time() + timeout
        seen = []
        while time.time() < end:
            for line in self.lines(0.3):
                seen.append(line)
                if want in line:
                    return line, seen
        raise RuntimeError("no '%s' answer to '%s'; saw: %s" % (want, text, seen[-5:]))

    def screen(self):
        line, _ = self.ask("screencap", "[cmd] screencap", timeout=5.0)
        data = base64.b64decode(line.split("b64=", 1)[1])
        if len(data) != W * H // 8:
            raise RuntimeError("screencap returned %d bytes" % len(data))
        # Column pages, as the display stores them: byte i covers x = i % 128,
        # rows (i // 128) * 8 .. + 7, lowest bit at the top.
        return [[(data[(y // 8) * W + x] >> (y % 8)) & 1 for x in range(W)] for y in range(H)]

    def app(self):
        line, _ = self.ask("app", "[cmd] app.name=")
        return line.split("app.name=", 1)[1].strip()

    def tap(self, index, pause=0.4):
        self.ask("btn %d tap" % index, "[cmd] btn.tap")
        time.sleep(pause)


def is_update_popup(pixels):
    # The update popup has a lit title bar (dark text on a lit band) and,
    # right under it, its first choice, "Install now", highlighted the same
    # way. A menu draws its highlight as an outline, and a screen such as
    # Speaker EQ has a lit title bar but nothing lit under it.
    band = sum(pixels[y][x] for y in range(16, 24) for x in range(W)) / (8 * W)
    title = sum(pixels[y][x] for y in range(2, 10) for x in range(W)) / (8 * W)
    return band > 0.7 and title > 0.5


def differing(a, b, rows=CHECK_ROWS):
    return sum(1 for y in rows for x in range(W) if a[y][x] != b[y][x])


def write_png(path, pixels, scale=4, on=(220, 238, 255), off=(0, 0, 0)):
    rows = []
    for y in range(H):
        row = bytearray()
        for x in range(W):
            row += bytes(on if pixels[y][x] else off) * scale
        rows.extend([b"\x00" + bytes(row)] * scale)
    raw = b"".join(rows)

    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W * scale, H * scale, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def read_png(path):
    """Read back a PNG written by write_png (any scale) as device pixels."""
    with open(path, "rb") as f:
        data = f.read()
    pos, idat, width, height = 8, b"", 0, 0
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            width, height = struct.unpack(">II", body[:8])
        elif kind == b"IDAT":
            idat += body
        pos += 12 + length
    raw = zlib.decompress(idat)
    scale = width // W
    stride = 1 + width * 3
    if width != W * scale or height != H * scale:
        raise RuntimeError(path + " is not a device screen capture")
    return [[1 if raw[(y * scale) * stride + 1 + (x * scale) * 3] > 100 else 0 for x in range(W)] for y in range(H)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", required=True)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "..", "docs", "assets", "media"))
    ap.add_argument("--expect", help="folder of reference frames for enter:<name> (default: --out)")
    ap.add_argument("--allow-unchecked-enter", action="store_true",
                    help="press Enter on enter:<name> steps that have no reference frame")
    ap.add_argument("--scale", type=int, default=4)
    ap.add_argument("steps", nargs="+")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    expect = args.expect or args.out
    try:
        sys.stdout.reconfigure(errors="replace")
    except AttributeError:
        pass

    dev = Device(args.port)
    print("device firmware: " + dev.version)
    # The awake setting is saved on the device: note it, keep the device
    # awake for the session, and put the noted setting back at the end.
    awake = None
    try:
        line, _ = dev.ask("awake", "[cmd] awake.mode=", timeout=2.0)
        m = re.search(r"awake\.mode=(\w+) stop=(\w+)", line)
        if m:
            awake = (m.group(1), m.group(2))
            print("awake setting at start: %s %s" % awake)
            if awake[0] == "off":
                dev.ask("awake set stay until", "[cmd] awake.set", timeout=2.0)
    except RuntimeError:
        print("no awake command on this build; button taps keep the device awake")
    eq_start = None      # the Speaker EQ screen before the first left/right
    eq_touched = False
    try:
        for step in args.steps:
            kind, _, val = step.partition(":")
            if kind in ("shot", "enter"):
                path = os.path.join(args.out, val + ".png")
                pixels = dev.screen()
                if kind == "enter":
                    ref = os.path.join(expect, val + ".png")
                    # Read the reference before writing over it (--out and
                    # --expect are often the same folder).
                    reference = read_png(ref) if os.path.exists(ref) else None
                write_png(path, pixels, scale=args.scale)
                print("wrote " + path)
                if kind == "enter":
                    if is_update_popup(pixels):
                        sys.exit("STOP: the update popup is on screen; Enter not pressed")
                    running = dev.app()
                    if running in REFUSE_APPS:
                        sys.exit("STOP: '%s' is open; Enter not pressed" % running)
                    if reference is None:
                        if not args.allow_unchecked_enter:
                            sys.exit("STOP: no reference frame %s; Enter not pressed "
                                     "(check the screen, then add the frame or use --allow-unchecked-enter)" % ref)
                        print("  no reference frame; pressing Enter unchecked")
                    else:
                        diff = differing(pixels, reference)
                        if diff > MATCH_LIMIT:
                            sys.exit("STOP: the screen differs from %s in %d pixels; Enter not pressed" % (ref, diff))
                    dev.tap(5, pause=0.5)
            elif kind == "btn":
                index = int(val)
                if index == 5:
                    sys.exit("STOP: press Enter with enter:<name>, which checks the screen first")
                if index in (2, 3) and dev.app() == EQ_APP:
                    if eq_start is None:
                        eq_start = dev.screen()
                    eq_touched = True
                dev.tap(index)
            elif kind == "wait":
                time.sleep(float(val))
            elif kind == "cmd":
                dev.send(val)
                for line in dev.lines(2.0):
                    print("  " + line)
            else:
                sys.exit("unknown step " + step)
    finally:
        try:
            if eq_touched:
                restore_eq(dev, eq_start)
        finally:
            if awake:
                mode, stop = awake
                if mode == "off":
                    dev.ask("awake set off", "[cmd] awake.set")
                else:
                    dev.ask("awake set %s %s" % (mode, "until" if stop == "until" else "idle"), "[cmd] awake.set")
                print("awake setting restored: %s %s" % awake)
            dev.s.close()


def restore_eq(dev, eq_start):
    """Step Speaker EQ until its screen matches the one seen before the run changed it."""
    dev.ask("launch " + EQ_APP, "[cmd] launch", timeout=3.0)
    time.sleep(1.0)
    rows = range(14, 50)   # the preset name and its description
    for _ in range(EQ_PRESETS):
        if differing(dev.screen(), eq_start, rows) <= MATCH_LIMIT:
            print("Speaker EQ restored to its preset at the start")
            dev.ask("launch menu", "[cmd] launch", timeout=3.0)
            return
        dev.tap(3, pause=0.9)
    print("WARNING: could not put Speaker EQ back to its preset at the start; check it on the device")


if __name__ == "__main__":
    main()
