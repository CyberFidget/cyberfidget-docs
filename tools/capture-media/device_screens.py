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
    record:on     start recording: the device streams its screen (20 a
                  second) while the next steps run, each screen timed as
                  it arrives
    record:off    stop, and write every change of screen as <out>/<ms>.png,
                  <ms> being its time from the first frame (enter: writes
                  no frame of its own while recording, and shot: is refused)

Guards, so a missed press or a changed menu can't open the wrong thing:

- enter:<name> presses Enter only when the screen matches the reference
  frame <expect>/<name>.png (default <expect> is <out>), ignoring the top
  status row. The reference is checked before anything is written; a refused
  screen goes to <out>/rejected/<name>.png, never over the reference. With no
  reference frame it stops, unless --allow-unchecked-enter is given (for
  building a new walk; the checks below still apply). A shot: and an enter:
  with the same name in one folder are refused, so a shot can't replace a
  reference.
- No button is pressed while the running app (the `app` command's answer)
  is one that erases or resets something, and only up and down are pressed
  while the firmware update popup is on screen (its first choice is
  "Install now"). The check is skipped only in apps the popup never
  opens over (NO_PROMPT_APPS); an unknown app name gets it. btn:5 and cmd:btn ... are
  refused: Enter goes through enter:<name>. cmd:launch of an erasing app is refused too.
- Left and right change the saved preset on the Speaker EQ screen. The first
  time they are pressed there, the screen is remembered; at the end of the
  run, even after an error or Ctrl+C, the tool opens Speaker EQ again and
  steps until the screen matches it, so the preset is left as found.
- The awake setting is read at the start, inside the same try/finally as
  the steps. If it was off, the run keeps the device awake (`awake set stay
  until`) and sets it back at the end, also after an error or Ctrl+C.

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
# Firmware 1.6.1 opens a popup (such as the update popup) only over the
# menu, Boot Animation, Link, Check for updates, Updates and Saved WiFi.
# The apps below (the rest of the `apps` command's list) draw their own
# lists with the same lit title bar and lit choice, so the popup check is
# skipped for them. Any other name, including an empty or unknown one, gets
# the check.
NO_PROMPT_APPS = (
    "Booper", "Flashlight", "Power Manager", "Matrix Screensaver", "Breakout",
    "Dino Run", "Clock", "Simon Says", "Particle Sim", "Font Face Demo",
    "Text Flow Demo", "Text Alignment Demo", "Rect Demo", "Circle Demo",
    "Image Demo 1", "Image Demo 2", "Image Demo 3", "Image Demo 4",
    "Battery Level", "Slider Status", "Accelerometer Demo", "Button Counters",
    "Time On Counter", "Progress Bar", "Reaction Time", "Serial Display",
    "Stratagem", "Graveyard", "Ghosts", "Eye", "CyberFidgie", "Splooty",
    "Spaceship", "Ragdoll Fidgie", "Music Player", "CyberFidget Portal",
    "Bewilder Your Brain", "Pixel Waterfall", "Dancing Gnomes", "Cronchybird",
    "Snake", "Voice Notes", "Starburst", "Timers", "Status",
    "Awake & dev mode", "Setup WiFi", "Speaker EQ", "Home Remote", "Counter",
)
EQ_APP = "Speaker EQ"
EQ_PRESETS = 3
# Screens per second asked of the device's screen stream while recording
# (the firmware's limit).
STREAM_FPS = 20


class Device:
    def __init__(self, port):
        self.s = serial.Serial(port, BAUD, timeout=0.25)
        self.buf = b""
        # While recording: (seconds since the start, base64 screen) for each
        # screen the device sends, timed when its line arrives.
        self.frames = None
        self.rec_t0 = 0.0
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
            # Take what has arrived, or wait (up to the port timeout) for one
            # byte, so each line is seen as soon as it is complete: that is
            # what times a recorded frame.
            self.buf += self.s.read(max(1, self.s.in_waiting))
            while b"\n" in self.buf:
                raw, self.buf = self.buf.split(b"\n", 1)
                line = raw.decode("utf-8", "replace").strip()
                if self.frames is not None and line.startswith("[cmd] screencap") and "b64=" in line:
                    self.frames.append((time.time() - self.rec_t0, line.split("b64=", 1)[1]))
                out.append(line)
        return out

    def pause(self, seconds):
        """Wait. While recording, keep reading, so every frame is timed."""
        if self.frames is None:
            time.sleep(seconds)
        else:
            self.lines(seconds)

    def record_start(self):
        self.s.timeout = 0.01
        self.frames = []
        self.rec_t0 = time.time()
        self.ask("screenstream on %d" % STREAM_FPS, "[cmd] screenstream=on")

    def record_stop(self):
        """Stop the screen stream and return the recorded frames."""
        frames, self.frames = self.frames, None
        self.send("screenstream off")
        # Let the frames still on their way arrive, without recording them.
        end = time.time() + 1.5
        while time.time() < end:
            if any("screenstream=off" in line for line in self.lines(0.2)):
                break
        self.s.timeout = 0.25
        return frames or []

    def ask(self, text, want, timeout=3.0):
        self.send(text)
        end = time.time() + timeout
        seen = []
        while time.time() < end:
            for line in self.lines(0.05):
                seen.append(line)
                if want in line:
                    return line, seen
        raise RuntimeError("no '%s' answer to '%s'; saw: %s" % (want, text, seen[-5:]))

    def screen(self):
        line, _ = self.ask("screencap", "[cmd] screencap", timeout=5.0)
        return decode_screen(line.split("b64=", 1)[1])

    def app(self):
        line, _ = self.ask("app", "[cmd] app.name=")
        return line.split("app.name=", 1)[1].strip()

    def tap(self, index, pause=0.4):
        self.ask("btn %d tap" % index, "[cmd] btn.tap")
        self.pause(pause)


def decode_screen(b64):
    data = base64.b64decode(b64)
    if len(data) != W * H // 8:
        raise RuntimeError("screencap returned %d bytes" % len(data))
    # Column pages, as the display stores them: byte i covers x = i % 128,
    # rows (i // 128) * 8 .. + 7, lowest bit at the top.
    return [[(data[(y // 8) * W + x] >> (y % 8)) & 1 for x in range(W)] for y in range(H)]


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


def write_recording(frames, out, scale=4):
    """Write each change of screen in a recording as <out>/<ms>.png.

    <ms> is the time the screen arrived, in milliseconds from the first
    frame (six digits, so the files sort in order). A screen shows until the
    next file's time, so a clip made from the files keeps the device's timing.
    """
    if not frames:
        raise Stop("the recording has no frames")
    t0 = frames[0][0]
    span = frames[-1][0] - t0
    kept = 0
    last = None
    for t, b64 in frames:
        if b64 == last:
            continue
        last = b64
        write_png(os.path.join(out, "%06d.png" % round((t - t0) * 1000)), decode_screen(b64), scale=scale)
        kept += 1
    rate = (len(frames) - 1) / span if span > 0 else 0.0
    print("recorded %d frames in %.2f s (%.1f per second); wrote the %d changes to %s"
          % (len(frames), span, rate, kept, out))
    return kept


class Stop(Exception):
    """A guard refused a step: nothing was pressed."""


def check_press(dev, index, pixels=None):
    """Refuse a button press that could confirm something dangerous.

    No button is pressed while an app that erases or resets is open (Reset
    to factory confirms by holding Enter, and its screens are not driven at
    all). On the update popup only up and down (0, 1) are allowed: the other
    buttons can choose "Install now". The check is skipped in the apps of
    NO_PROMPT_APPS, which the popup never opens over, so their own lists
    are not mistaken for it; any other app name, also an empty or unknown
    one, gets the check. Returns the running app's name.
    """
    running = dev.app()
    if running in REFUSE_APPS:
        raise Stop("'%s' is open; button %d not pressed" % (running, index))
    # Fail closed: the check is skipped only for an app known to take no
    # popups. A missing, empty or unknown name gets the check.
    if index not in (0, 1) and running not in NO_PROMPT_APPS:
        if pixels is None:
            pixels = dev.screen()
        if is_update_popup(pixels):
            raise Stop("the update popup is on screen; button %d not pressed" % index)
    return running


def check_enter(pixels, reference, ref, allow_unchecked):
    """Raise Stop unless the screen matches the reference frame for an Enter."""
    if reference is None:
        if not allow_unchecked:
            raise Stop("no reference frame %s; Enter not pressed "
                       "(check the screen, then add the frame or use --allow-unchecked-enter)" % ref)
        print("  no reference frame; pressing Enter unchecked")
        return
    diff = differing(pixels, reference)
    if diff > MATCH_LIMIT:
        raise Stop("the screen differs from %s in %d pixels; Enter not pressed" % (ref, diff))


def check_cmd(text):
    """Refuse serial commands that would get round the button guards."""
    words = text.strip().split()
    if not words:
        return
    verb = words[0].lower()
    if verb == "btn":
        raise Stop("'%s': press buttons with btn:<index> or enter:<name>, which check the screen first" % text)
    if verb == "launch" and " ".join(words[1:]).lower() in [a.lower() for a in REFUSE_APPS]:
        raise Stop("'%s': this tool does not open apps that erase or reset" % text)


def run(dev, steps, out, expect=None, allow_unchecked=False, scale=4):
    """Run the steps on dev. The finally undoes every state change made."""
    expect = expect or out
    enter_names = {s.partition(":")[2] for s in steps if s.startswith("enter:")}
    if os.path.abspath(out) == os.path.abspath(expect):
        shot_names = {s.partition(":")[2] for s in steps if s.startswith("shot:")}
        clash = sorted(enter_names & shot_names)
        if clash:
            raise Stop("shot: and enter: share a name (%s), so the shot would replace its reference" % ", ".join(clash))
    awake = None          # the awake setting read at the start
    awake_changed = False
    eq_start = None       # the Speaker EQ screen before the first left/right
    eq_touched = False
    recording = False
    try:
        # The awake setting is saved on the device: note it, keep the device
        # awake for the session, and put the noted setting back at the end.
        try:
            line, _ = dev.ask("awake", "[cmd] awake.mode=", timeout=2.0)
            m = re.search(r"awake\.mode=(\w+) stop=(\w+)", line)
            if m:
                awake = (m.group(1), m.group(2))
                print("awake setting at start: %s %s" % awake)
                if awake[0] == "off":
                    awake_changed = True
                    dev.ask("awake set stay until", "[cmd] awake.set", timeout=2.0)
        except RuntimeError:
            print("no awake command on this build; button taps keep the device awake")

        for step in steps:
            kind, _, val = step.partition(":")
            if kind == "record" and val in ("on", "off"):
                if (val == "on") == recording:
                    raise Stop("record:%s while recording is %s" % (val, "on" if recording else "off"))
                if val == "on":
                    # Marked first: if the start is interrupted or its answer
                    # never comes, the stream may still be on, and the
                    # finally must turn it off.
                    recording = True
                    dev.record_start()
                    print("recording")
                else:
                    recording = False
                    write_recording(dev.record_stop(), out, scale)
            elif kind == "shot" and recording:
                raise Stop("shot:%s while recording: the recording already keeps every screen" % val)
            elif kind in ("shot", "enter"):
                path = os.path.join(out, val + ".png")
                pixels = dev.screen()
                if kind == "shot":
                    write_png(path, pixels, scale=scale)
                    print("wrote " + path)
                    continue
                # Check against the reference first; the frame is written
                # in its place only after it passed.
                ref = os.path.join(expect, val + ".png")
                reference = read_png(ref) if os.path.exists(ref) else None
                try:
                    check_press(dev, 5, pixels)
                    check_enter(pixels, reference, ref, allow_unchecked)
                except Stop:
                    rejected = os.path.join(out, "rejected")
                    os.makedirs(rejected, exist_ok=True)
                    write_png(os.path.join(rejected, val + ".png"), pixels, scale=scale)
                    print("wrote the refused screen to " + os.path.join(rejected, val + ".png"))
                    raise
                if not recording:
                    write_png(path, pixels, scale=scale)
                    print("wrote " + path)
                dev.tap(5, pause=0.5)
            elif kind == "btn":
                index = int(val)
                if index == 5:
                    raise Stop("press Enter with enter:<name>, which checks the screen first")
                running = check_press(dev, index)
                if index in (2, 3) and running == EQ_APP:
                    if eq_start is None:
                        eq_start = dev.screen()
                    eq_touched = True
                dev.tap(index)
            elif kind == "wait":
                dev.pause(float(val))
            elif kind == "cmd":
                check_cmd(val)
                dev.send(val)
                for line in dev.lines(2.0):
                    if not line.startswith("[cmd] screencap"):
                        print("  " + line)
            else:
                raise Stop("unknown step " + step)
        if recording:
            raise Stop("record:on without record:off; nothing written")
    finally:
        try:
            try:
                if recording:
                    dev.record_stop()
            finally:
                if eq_touched:
                    restore_eq(dev, eq_start)
        finally:
            if awake and awake_changed:
                dev.ask("awake set off" + (" until" if awake[1] == "until" else ""), "[cmd] awake.set")
                print("awake setting restored: %s %s" % awake)


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
    try:
        sys.stdout.reconfigure(errors="replace")
    except AttributeError:
        pass

    dev = Device(args.port)
    print("device firmware: " + dev.version)
    try:
        run(dev, args.steps, args.out, args.expect, args.allow_unchecked_enter, args.scale)
    except Stop as stop:
        sys.exit("STOP: " + str(stop))
    finally:
        dev.s.close()


if __name__ == "__main__":
    main()


