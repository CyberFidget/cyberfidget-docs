# Overview

Cyber Fidget ships as a high-quality kit — no soldering required, just screws. By the end of this section you will have built your device and run your own app on it. The quickest route needs nothing installed: you write and test apps in your browser.

---

## What you'll need

- **USB-C cable** (data-capable, not charge-only)
- **Computer** with a USB port (Windows, macOS, or Linux). For the browser route, use Chrome, Edge or Firefox.
- **Small Phillips screwdriver** (for assembly)
- **microSD card** (FAT32 formatted, optional but recommended)
- **Internet connection** (for the browser tools, firmware and downloads)

---

## Steps

### 1. Assemble your device

Follow the [Assembly Guide](assembly/guide.md) to put your Cyber Fidget together. Every screw and part is accessible — the enclosure is designed to be opened, explored, and modified.

### 2. Build your first app in the browser

Write a small app, watch it run in the on-screen emulator, and send it to your device. Nothing to install. Follow [Build your first app in the browser](first-app.md). You can do most of it before your kit even arrives.

### 3. Explore built-in apps

The firmware ships with 28+ built-in apps: games, screensavers, tools, and code examples. Use the buttons to navigate the on-device menu. See the [Apps](../software/apps.md) page for the full catalog.

### 4. Go further

Build bigger apps with the [App Builder](https://cyberfidget.com/create/), or work on the firmware itself (see the advanced route below).

---

## Advanced: develop the firmware

Most people never need this. If you want to change the firmware itself, or build with your own toolchain, connect via USB-C and flash the firmware. See [Advanced: firmware with Arduino](first-flash-arduino.md) for step-by-step instructions.

!!! tip "Recommended toolchain"
    **VS Code + PlatformIO** (via pioarduino) gives the best experience — automatic dependency management, built-in serial monitor, and one-click upload.

### Development options

| Toolchain | Notes |
|-----------|-------|
| **VS Code + PlatformIO** | Recommended. Uses pioarduino (community-maintained ESP32 platform) |
| **pioarduino IDE** | Standalone PlatformIO-compatible IDE |
| **Arduino IDE** | Works, but requires manual library management |
| **CircuitPython** | Hardware support designed-in but currently untested |

---

## Where to go next

- **[Build your first app](first-app.md)** — Write and run an app in your browser
- **[Assembly Guide](assembly/guide.md)** — Build your device step by step
- **[Advanced: firmware with Arduino](first-flash-arduino.md)** — Flash firmware for the first time
- **[Concepts](../concepts/index.md)** — Learn how apps use buttons, display, audio, LEDs, and more
- **[Hardware Specs](../hardware/specs.md)** — Full component list and dimensions
