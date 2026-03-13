# Overview

Cyber Fidget ships as a high-quality kit — no soldering required, just screws. This section helps you go from unboxing to running your first app.

---

## What you'll need

- **USB-C cable** (data-capable, not charge-only)
- **Computer** with a USB port (Windows, macOS, or Linux)
- **Small Phillips screwdriver** (for assembly)
- **microSD card** (FAT32 formatted, optional but recommended)
- **Internet connection** (for downloading firmware and tools)

---

## Steps

### 1. Assemble your device

Follow the [Assembly Guide](assembly/guide.md) to put your Cyber Fidget together. Every screw and part is accessible — the enclosure is designed to be opened, explored, and modified.

### 2. Flash firmware

Connect via USB-C and flash the firmware using your preferred toolchain. See [First Flash](first-flash-arduino.md) for step-by-step instructions.

!!! tip "Recommended toolchain"
    **VS Code + PlatformIO** (via pioarduino) gives the best experience — automatic dependency management, built-in serial monitor, and one-click upload.

### 3. Explore apps

The firmware ships with 28+ built-in apps: games, screensavers, tools, and code examples. Use the buttons to navigate the on-device menu. See the [Apps](../software/apps.md) page for the full catalog.

### 4. Build your own

Write or generate apps using the [App Builder](https://cyberfidget.com/build) in your browser. Test in the emulator first, then flash to hardware.

---

## Development options

| Toolchain | Notes |
|-----------|-------|
| **VS Code + PlatformIO** | Recommended. Uses pioarduino (community-maintained ESP32 platform) |
| **pioarduino IDE** | Standalone PlatformIO-compatible IDE |
| **Arduino IDE** | Works, but requires manual library management |
| **CircuitPython** | Hardware support designed-in but currently untested |

---

## Where to go next

- **[Assembly Guide](assembly/guide.md)** — Build your device step by step
- **[First Flash](first-flash-arduino.md)** — Flash firmware for the first time
- **[Concepts](../concepts/index.md)** — Learn how apps use buttons, display, audio, LEDs, and more
- **[Hardware Specs](../hardware/specs.md)** — Full component list and dimensions
