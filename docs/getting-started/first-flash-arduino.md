# First Flash

This guide walks you through flashing the Cyber Fidget firmware for the first time.

---

## Choose your toolchain

!!! tip "Recommended: VS Code + PlatformIO"
    The best development experience is with **VS Code + PlatformIO** using the **pioarduino** platform. Arduino IDE works too, but PlatformIO handles dependencies and board configuration automatically.

| Option | Pros | Setup effort |
|--------|------|-------------|
| **VS Code + PlatformIO** | Auto-deps, built-in serial monitor, debugging | Medium |
| **pioarduino IDE** | Standalone PlatformIO-compatible IDE | Medium |
| **Arduino IDE** | Familiar, simple | Easy (but manual library management) |

!!! note "Build system note"
    The original PlatformIO platform for ESP32 is no longer officially maintained. This project uses **pioarduino**, a community-maintained fork that provides continuity with ESP-IDF 5.1.4 + Arduino ESP32 3.0.3. A future migration to pure ESP-IDF is under consideration.

---

## Prerequisites

- **Assembled Cyber Fidget** — see the [Assembly Guide](assembly/guide.md) if you haven't built yours yet
- **USB-C cable** (data-capable, not charge-only)
- **Computer** with USB port (Windows, macOS, or Linux)
- **microSD card** (FAT32 formatted) — optional but recommended for app storage

---

## Option A: VS Code + PlatformIO (recommended)

### 1. Install VS Code and PlatformIO

1. Install [VS Code](https://code.visualstudio.com/)
2. Open VS Code, go to Extensions (`Ctrl+Shift+X`), search **PlatformIO IDE**, and install it
3. Restart VS Code when prompted

### 2. Clone the firmware

```bash
git clone https://github.com/cyberfidget/CyberFidget_Bundled_Demo_Platformio.git
cd CyberFidget_Bundled_Demo_Platformio
```

### 3. Open the project

Open the cloned folder in VS Code. PlatformIO will automatically detect `platformio.ini` and install the correct platform, board support, and libraries.

The board is configured as `adafruit_feather_esp32_v2` in `platformio.ini`.

### 4. Connect and flash

1. Plug in your Cyber Fidget via USB-C
2. The CP2102N USB bridge will appear as a serial/COM port
3. Click the **PlatformIO: Upload** button (right arrow icon in the bottom toolbar), or run:

```bash
pio run --target upload
```

### 5. Verify

Open the PlatformIO Serial Monitor (`Ctrl+Shift+M` or the plug icon) at **921600 baud**. You should see boot messages and the device menu on the OLED.

---

## Option B: Arduino IDE

### 1. Install Arduino IDE

Download and install [Arduino IDE](https://www.arduino.cc/en/software) (2.x recommended).

### 2. Add ESP32 board support

1. Go to **File → Preferences**
2. In "Additional Board Manager URLs", add:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Go to **Tools → Board → Boards Manager**, search "esp32", and install **esp32 by Espressif Systems**

### 3. Select board and port

- **Board:** `Adafruit Feather ESP32 V2` (under ESP32 Arduino)
- **Port:** Select the COM port that appears when you plug in the device (CP2102N bridge)
- **Upload Speed:** 921600

### 4. Install libraries

You'll need to manually install the libraries listed in `platformio.ini` via **Sketch → Include Library → Manage Libraries**. Key libraries include:

- Adafruit NeoPixel
- SparkFun LIS2DH12
- ESP32-audioI2S (or equivalent)

### 5. Upload

Click **Upload** (right arrow button). The firmware will compile and flash to the device.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| No COM port appears | Try a different USB-C cable (must be data-capable). Install [CP2102N drivers](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers) if needed. |
| Upload fails | Hold the **Boot** button (small button on the back) while clicking Upload, then release after upload starts. |
| Garbled serial output | Set baud rate to **921600** in your serial monitor. |
| PlatformIO can't find board | Let PlatformIO fully initialize the project — it downloads the platform on first open. |

---

## Next steps

- [Apps](../software/apps.md) — Explore the 28+ built-in apps
- [How an App Works](../concepts/app-lifecycle.md) — Understand the app lifecycle
- [App Builder](https://cyberfidget.com/build) — Write and test apps in your browser
