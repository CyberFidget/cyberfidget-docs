# Product Overview

A machined-aluminum, pocket-sized gadget built for play, tinkering, and experimentation. Designed and assembled in Michigan.

---

## What is Cyber Fidget?

Cyber Fidget is two things at once:

1. **An electronic fidget toy** — beyond a spinner or clicker, something with a screen, buttons, LEDs, and sound that's fun to hold and play with
2. **An approachable dev board** — with everything already included: display, buttons, slider, speaker, mic, accelerometer, LEDs, SD card, Wi-Fi, and Bluetooth

It's meant to feel good in your hands, be easy to use without knowing how it works, and be fully hackable when you're ready to dig in.

---

## At a glance

| | |
|---|---|
| **Size** | 2.2 x 1.6 x 0.8 in (55.3 x 41.3 x 19.6 mm) |
| **Weight** | ~68 g (varies by backplate) |
| **MCU** | ESP32-PICO-MINI-02 (Wi-Fi + Bluetooth) |
| **Display** | 0.96" 128x64 monochrome OLED |
| **Controls** | 6 buttons + analog slider |
| **Audio** | Speaker + MEMS microphone |
| **LEDs** | 4x RGBW (3 front, 1 back) |
| **Storage** | microSD card |
| **Power** | 400 mAh LiPo, USB-C charging |
| **Body** | Precision-machined aluminum |

For the full component list with part numbers, see [Hardware Specs](../hardware/specs.md).

---

## What's in the kit

Cyber Fidget primarily ships as a self-assembly kit — no soldering, just screws. The kit includes:

- Machined aluminum chassis (front and back)
- Assembled PCB with all components pre-soldered
- Buttons, slider, and hardware
- Screws and fasteners
- Interchangeable screen color filters

Assembly takes about 15 minutes. See the [Assembly Guide](../getting-started/assembly/guide.md) for step-by-step instructions with photos.

---

## Made for tinkerers

Every screw and part is accessible. The enclosure is built to be opened, explored, and modified:

- **Re-color it** — swap screen colors (blue, red, teal, and more)
- **Redesign it** — 3D print your own backplate or case modifications
- **Hack it** — apps run off the SD card (soon) or integrate with the source code
- **Learn from it** — ideal for learning how to code, embedded systems, sensors, and human-machine interfaces

---

## Software

The firmware ships with 28+ built-in apps (games, screensavers, tools, examples). You can also write your own using the [App Builder](https://cyberfidget.com/build.html) in your browser or by cloning the [firmware repo](https://github.com/cyberfidget/cyberfidget-firmware).

Best experience with VS Code + PlatformIO (via pioarduino). CircuitPython hardware support is designed-in but currently untested.

See [Apps](../software/apps.md) for the full catalog.

---

## See also

- [Hardware Specs](../hardware/specs.md) — Full specifications with part numbers
- [Pinout](../hardware/pinout.md) — GPIO assignments
- [Accessories](accessories.md) — Color gels, backplates, and 3D printing
- [Assembly Guide](../getting-started/assembly/guide.md) — Build your device
- [First Flash](../getting-started/first-flash-arduino.md) — Flash firmware for the first time
- [Open Source](open-source.md) — Repos, licenses, and how to contribute
