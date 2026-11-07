# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline tests for device_screens.py's guards, with a stand-in device.

Run from this folder: python -m unittest test_device_screens
"""
import base64
import os
import shutil
import tempfile
import unittest

import device_screens as ds

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES = os.path.join(HERE, "frames", "speaker-eq")


def frame(name):
    return ds.read_png(os.path.join(FRAMES, name + ".png"))


def blank():
    return [[0] * ds.W for _ in range(ds.H)]


def popup():
    # A lit title bar and a lit first choice under it, like the update popup.
    p = blank()
    for y in list(range(0, 13)) + list(range(14, 26)):
        p[y] = [1] * ds.W
    return p


class FakeDevice:
    """Answers the serial commands the tool uses, and records what it sent."""

    def __init__(self, screens, app="menu", awake=("off", "idle"), interrupt_after=None):
        self.screens = list(screens)   # screen shown after each button tap
        self.current = self.screens.pop(0)
        self.app_name = app
        self.awake = awake
        self.sent = []
        self.taps = []
        self.interrupt_after = interrupt_after
        self.recorded = []             # frames record_stop returns
        self.start_error = None        # raised by record_start, after sending

    def _note(self, text):
        self.sent.append(text)
        if self.interrupt_after and text == self.interrupt_after:
            self.interrupt_after = None
            raise KeyboardInterrupt

    def ask(self, text, want, timeout=3.0):
        self._note(text)
        if text == "awake":
            return "[cmd] awake.mode=%s stop=%s listen=0" % self.awake, []
        if text.startswith("awake set"):
            return "[cmd] awake.set=x stop=y", []
        if text.startswith("launch "):
            self.app_name = text[len("launch "):]
            return "[cmd] launch.ok=1", []
        return want, []

    def send(self, text):
        self._note(text)

    def lines(self, timeout):
        return []

    def screen(self):
        return self.current

    def app(self):
        return self.app_name

    def tap(self, index, pause=0.4):
        self.taps.append(index)
        if self.screens:
            self.current = self.screens.pop(0)

    def pause(self, seconds):
        pass

    def record_start(self):
        self.sent.append("screenstream on")
        if self.start_error:
            raise self.start_error

    def record_stop(self):
        self.sent.append("screenstream off")
        return self.recorded


def b64(pixels):
    data = bytearray(ds.W * ds.H // 8)
    for y in range(ds.H):
        for x in range(ds.W):
            if pixels[y][x]:
                data[(y // 8) * ds.W + x] |= 1 << (y % 8)
    return base64.b64encode(bytes(data)).decode()


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.out = tempfile.mkdtemp()
        self.ref = tempfile.mkdtemp()
        shutil.copy(os.path.join(FRAMES, "06.png"), os.path.join(self.ref, "06.png"))

    def tearDown(self):
        shutil.rmtree(self.out)
        shutil.rmtree(self.ref)

    def test_enter_on_matching_screen(self):
        dev = FakeDevice([frame("06"), frame("07")])
        ds.run(dev, ["enter:06"], self.out, self.ref)
        self.assertEqual(dev.taps, [5])

    def test_enter_refused_on_other_screen_and_reference_kept(self):
        # Same folder for output and references: the refused screen must not
        # replace the reference.
        shutil.copy(os.path.join(FRAMES, "06.png"), os.path.join(self.out, "06.png"))
        before = open(os.path.join(self.out, "06.png"), "rb").read()
        dev = FakeDevice([frame("05")])
        with self.assertRaises(ds.Stop):
            ds.run(dev, ["enter:06"], self.out)
        self.assertEqual(dev.taps, [])
        self.assertEqual(open(os.path.join(self.out, "06.png"), "rb").read(), before)
        self.assertTrue(os.path.exists(os.path.join(self.out, "rejected", "06.png")))

    def test_enter_refused_without_reference(self):
        dev = FakeDevice([frame("06")])
        with self.assertRaises(ds.Stop):
            ds.run(dev, ["enter:13"], self.out, self.ref)
        self.assertEqual(dev.taps, [])

    def test_enter_refused_on_update_popup_even_unchecked(self):
        dev = FakeDevice([popup()])
        with self.assertRaises(ds.Stop):
            ds.run(dev, ["enter:new"], self.out, self.ref, allow_unchecked=True)
        self.assertEqual(dev.taps, [])

    def test_select_and_sideways_refused_on_popup(self):
        for index in (2, 3, 4):
            dev = FakeDevice([popup()])
            with self.assertRaises(ds.Stop):
                ds.run(dev, ["btn:%d" % index], self.out, self.ref)
            self.assertEqual(dev.taps, [])
        dev = FakeDevice([popup(), popup()])
        ds.run(dev, ["btn:1"], self.out, self.ref)
        self.assertEqual(dev.taps, [1])

    def test_popup_check_only_where_popups_open(self):
        # An app's own list (lit title bar, lit first row) looks like the
        # popup, but the firmware never opens the popup over that app.
        dev = FakeDevice([popup(), blank()], app="Music Player")
        ds.run(dev, ["enter:list"], self.out, self.ref, allow_unchecked=True)
        self.assertEqual(dev.taps, [5])
        dev = FakeDevice([popup(), blank()], app="Updates")
        with self.assertRaises(ds.Stop):
            ds.run(dev, ["enter:list"], self.out, self.ref, allow_unchecked=True)
        self.assertEqual(dev.taps, [])

    def test_popup_check_for_empty_or_unknown_app(self):
        # Fail closed: without a known app name the popup check runs.
        for name in ("", "Some New App"):
            dev = FakeDevice([popup(), blank()], app=name)
            with self.assertRaises(ds.Stop):
                ds.run(dev, ["enter:list"], self.out, self.ref, allow_unchecked=True)
            self.assertEqual(dev.taps, [])
            dev = FakeDevice([popup(), blank()], app=name)
            with self.assertRaises(ds.Stop):
                ds.run(dev, ["btn:4"], self.out, self.ref)
            self.assertEqual(dev.taps, [])

    def test_stream_stopped_when_start_fails(self):
        # The stream may already be on when the answer times out or Ctrl+C
        # lands: the run still turns it off.
        for error in (RuntimeError("no answer"), KeyboardInterrupt()):
            dev = FakeDevice([frame("06")])
            dev.start_error = error
            with self.assertRaises(type(error)):
                ds.run(dev, ["record:on", "wait:0", "record:off"], self.out, self.ref)
            self.assertEqual(dev.sent.count("screenstream off"), 1)
            self.assertEqual(dev.sent[-1], "awake set off")

    def test_recording_writes_each_change_with_its_time(self):
        a, b = frame("00"), frame("01")
        dev = FakeDevice([frame("06"), frame("07")])
        dev.recorded = [(1.00, b64(a)), (1.05, b64(a)), (1.10, b64(b)), (1.15, b64(b)), (1.30, b64(a))]
        ds.run(dev, ["record:on", "enter:06", "wait:0.5", "record:off"], self.out, self.ref)
        self.assertEqual(dev.taps, [5])
        self.assertEqual(sorted(os.listdir(self.out)), ["000000.png", "000100.png", "000300.png"])
        self.assertEqual(ds.read_png(os.path.join(self.out, "000100.png")), b)

    def test_recording_stopped_after_error(self):
        dev = FakeDevice([frame("05")])
        with self.assertRaises(ds.Stop):
            ds.run(dev, ["record:on", "enter:06"], self.out, self.ref)
        self.assertIn("screenstream off", dev.sent)
        self.assertEqual(dev.taps, [])
        dev = FakeDevice([frame("05")])
        with self.assertRaises(ds.Stop):
            ds.run(dev, ["record:on", "shot:x"], self.out, self.ref)
        self.assertIn("screenstream off", dev.sent)
        self.assertFalse(os.path.exists(os.path.join(self.out, "x.png")))
        dev = FakeDevice([frame("05")])
        with self.assertRaises(ds.Stop):
            ds.run(dev, ["record:on", "wait:0"], self.out, self.ref)
        self.assertIn("screenstream off", dev.sent)

    def test_no_button_in_reset_to_factory(self):
        for step in ("btn:0", "btn:4", "enter:06"):
            dev = FakeDevice([frame("06")], app="Reset to factory")
            with self.assertRaises(ds.Stop):
                ds.run(dev, [step], self.out, self.ref)
            self.assertEqual(dev.taps, [])

    def test_raw_enter_and_cmd_btn_refused(self):
        for step in ("btn:5", "cmd:btn 5 tap", "cmd:btn 4 tap", "cmd:BTN 0 tap", "cmd:launch Reset to factory"):
            dev = FakeDevice([frame("06")])
            with self.assertRaises(ds.Stop):
                ds.run(dev, [step], self.out, self.ref)
            self.assertEqual(dev.taps, [])
            self.assertFalse(any(s.lower().startswith(("btn", "launch reset")) for s in dev.sent), dev.sent)

    def test_shot_and_enter_with_one_name_refused(self):
        dev = FakeDevice([frame("06")])
        with self.assertRaises(ds.Stop):
            ds.run(dev, ["shot:06", "enter:06"], self.out)
        self.assertEqual(dev.sent, [])

    def test_awake_restored_after_interrupt(self):
        # Ctrl+C right after the tool turned stay-awake on.
        dev = FakeDevice([frame("06")], awake=("off", "idle"), interrupt_after="awake set stay until")
        with self.assertRaises(KeyboardInterrupt):
            ds.run(dev, ["wait:0"], self.out, self.ref)
        self.assertEqual(dev.sent[-1], "awake set off")

    def test_awake_left_alone_when_not_off(self):
        dev = FakeDevice([frame("06")], awake=("dev", "until"))
        ds.run(dev, ["wait:0"], self.out, self.ref)
        self.assertFalse(any(s.startswith("awake set") for s in dev.sent))

    def test_speaker_eq_put_back_after_error(self):
        # In Speaker EQ on Balanced (14), right shows Loud (15); then a step
        # fails. The finally reopens Speaker EQ (still Loud) and steps right,
        # through Off, until Balanced shows again.
        balanced, loud = frame("14"), frame("15")
        dev = FakeDevice([balanced, loud, blank(), balanced], app="Speaker EQ")
        with self.assertRaises(ds.Stop):
            ds.run(dev, ["btn:3", "enter:missing"], self.out, self.ref)
        self.assertEqual(dev.taps, [3, 3, 3])
        self.assertIn("launch Speaker EQ", dev.sent)
        self.assertEqual(dev.sent[-2:], ["launch menu", "awake set off"])


if __name__ == "__main__":
    unittest.main()
