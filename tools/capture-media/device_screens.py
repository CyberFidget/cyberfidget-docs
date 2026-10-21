# SPDX-License-Identifier: GPL-3.0-or-later
"""Capture a real Cyber Fidget's screen over USB serial, for the docs.

Drives the device with its serial commands (`btn <index> tap` presses a
button, `screencap` returns the 128 x 64 screen) and writes each screen as a
PNG. Steps come from the command line, in order:

    python device_screens.py --port COM30 --out ../../docs/assets/media \
        shot:menu-home btn:1 wait:0.6 shot:menu-second cmd:menutree

    shot:<name>   capture the screen to <out>/<name>.png
    btn:<index>   tap a button (0 up, 1 down, 2 left, 3 right, 4 back, 5 enter)
    wait:<sec>    pause
    cmd:<text>    send any serial command and print what it answers

Opening the port follows the bench rules: reset dance, then poll `version`
until the command line answers. The device is kept awake for the session
(`awake set stay until`) and put back to normal at the end (`awake set off`).
Needs pyserial (PlatformIO's Python has it).
"""
import argparse
import base64
import os
import struct
import sys
import time
import zlib

import serial

BAUD = 921600
W, H = 128, 64


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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", required=True)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "..", "docs", "assets", "media"))
    ap.add_argument("--scale", type=int, default=4)
    ap.add_argument("steps", nargs="+")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    dev = Device(args.port)
    print("device firmware: " + dev.version)
    # Stay awake for the session where the build has the command (test
    # builds); on other builds the button taps keep it awake.
    stay = True
    try:
        dev.ask("awake set stay until", "[cmd] awake", timeout=2.0)
    except RuntimeError:
        stay = False
    try:
        for step in args.steps:
            kind, _, val = step.partition(":")
            if kind == "shot":
                path = os.path.join(args.out, val + ".png")
                write_png(path, dev.screen(), scale=args.scale)
                print("wrote " + path)
            elif kind == "btn":
                dev.ask("btn %s tap" % val, "[cmd] btn.tap")
                time.sleep(0.4)
            elif kind == "wait":
                time.sleep(float(val))
            elif kind == "cmd":
                dev.send(val)
                for line in dev.lines(2.0):
                    print("  " + line)
            else:
                sys.exit("unknown step " + step)
    finally:
        if stay:
            dev.ask("awake set off", "[cmd] awake")
        dev.s.close()


if __name__ == "__main__":
    main()
