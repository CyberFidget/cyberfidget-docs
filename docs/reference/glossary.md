# Glossary

Hover over terms in the docs to see short definitions. This page lists all acronyms, file types, and product names used in the documentation.

---

## Acronyms & abbreviations

| Term | Definition |
|------|------------|
| **A2DP** | Advanced Audio Distribution Profile — Bluetooth stereo audio streaming protocol. |
| **ADC** | Analog-to-Digital Converter — converts the slider's voltage to a number (e.g. 0–4095). |
| **API** | Application Programming Interface — how code talks to a library or service. |
| **BLE** | Bluetooth Low Energy — used for wireless features on the device. |
| **CI** | Continuous Integration — automated builds (e.g. GitHub Actions compiling WASM). |
| **CMake** | Cross-platform build system used to configure the WASM/Emscripten build. |
| **CORS** | Cross-Origin Resource Sharing — browser rules that block loading WASM from `file://` URLs. |
| **CSS** | Cascading Style Sheets — used to style the emulator (LEDs, layout). |
| **DOM** | Document Object Model — the browser's representation of the page (buttons, canvas). |
| **ESP32** | Espressif's 32-bit microcontroller — the main chip on Cyber Fidget hardware. |
| **FPS** | Frames Per Second — the emulator runs at 50 FPS like the real device. |
| **FreeRTOS** | Free Real-Time Operating System — the RTOS layer used by ESP-IDF under the hood. |
| **GPIO** | General-Purpose Input/Output — physical pins used for buttons, etc. |
| **HAL** | Hardware Abstraction Layer — the layer that swaps ESP32 drivers for browser equivalents in the emulator. |
| **I2C** | Inter-Integrated Circuit — serial bus used for the OLED, accelerometer, and fuel gauge. |
| **I2S** | Inter-IC Sound — digital audio bus used for the speaker amplifier and MEMS microphone. |
| **IDE** | Integrated Development Environment — e.g. the App Builder on the website. |
| **IndexedDB** | Browser storage used to cache compiled WASM so you don't recompile every time. |
| **JS** | JavaScript. |
| **LED** | Light-Emitting Diode. |
| **LiPo** | Lithium Polymer — rechargeable battery type used in Cyber Fidget (400 mAh). |
| **MEMS** | Micro-Electro-Mechanical Systems — miniaturized sensor technology used in the ICS-43434 microphone. |
| **NeoPixel** | Adafruit's addressable RGB(W) LED product line; firmware uses a shim that matches its API. |
| **OLED** | Organic Light-Emitting Diode — the 128×64 pixel display on Cyber Fidget. |
| **OTA** | Over-The-Air — firmware updates delivered wirelessly. |
| **PCB** | Printed Circuit Board. |
| **RGBW** | Red, Green, Blue, White — four-channel LED color. |
| **SD** | Secure Digital — the micro-SD card slot. |
| **SPI** | Serial Peripheral Interface — serial bus used for the SD card. |
| **SPP** | Serial Port Profile — Bluetooth serial data streaming protocol. |
| **SSD1306** | The display controller chip used in the Cyber Fidget OLED. |
| **USB** | Universal Serial Bus — used for charging and serial communication via USB-C. |
| **WASM** | WebAssembly — binary format that runs in the browser; the emulator runs C++ apps as WASM. |
| **WebAssembly** | Binary instruction format for the web; the emulator compiles C++ to WASM. |
| **Wi-Fi** | Wireless Fidelity — used for OTA and network features. |

---

## File types & artifacts

| Term | Meaning |
|------|--------|
| **.cpp** | C++ source file (implementation). |
| **.h** | C/C++ header file (declarations). |
| **.js** | JavaScript file — the Emscripten "loader" that loads and runs the WASM module. |
| **.wasm** | WebAssembly binary — the compiled app. |
| **.yml / .yaml** | YAML config — e.g. GitHub Actions workflow or MkDocs config. |

---

## Products & projects

| Term | Meaning |
|------|--------|
| **Adafruit** | Maker electronics company; NeoPixel and many Arduino libraries. |
| **AP2112K** | Diodes Inc. 3.3V LDO regulator — used for main logic, OLED, and LED power rails. |
| **CircuitPython** | Adafruit's Python runtime for microcontrollers. Hardware support designed-in but currently untested on Cyber Fidget. |
| **CP2102N** | Silicon Labs USB-to-UART bridge chip — provides the serial connection over USB-C. |
| **Cyber Fidget** | The physical device and ecosystem (hardware, firmware, website, docs). |
| **Emscripten** | Toolchain that compiles C/C++ to WebAssembly and JavaScript. |
| **GitHub Actions** | CI/CD platform used to compile WASM on your fork. |
| **ICS-43434** | InvenSense/TDK I2S MEMS microphone used in Cyber Fidget. |
| **LIS2DH12** | STMicroelectronics 3-axis digital accelerometer used in Cyber Fidget. |
| **MAX17048** | Analog Devices/Maxim fuel gauge IC for LiPo battery state-of-charge monitoring. |
| **MAX98357A** | Analog Devices/Maxim I2S Class-D amplifier driving the on-board speaker. |
| **MCP73831** | Microchip single-cell LiPo charge management controller. |
| **pioarduino** | Community-maintained PlatformIO platform fork for ESP32 (ESP-IDF 5.1.4 + Arduino ESP32 3.0.3). |
| **PlatformIO** | IDE and build system for embedded development; recommended for Cyber Fidget via the pioarduino fork. |
| **SK6812** | Individually addressable RGBW LED (NeoPixel-compatible) — four are used in Cyber Fidget. |
| **ThingPulse** | Source of the OLED font data used in the WASM shim. |

---

## Emulator-specific

| Term | Meaning |
|------|--------|
| **Bridge** | `wasm_bridge.js` — glue between the WASM module and the on-screen emulator. |
| **Shim** | A stub header (e.g. `Arduino.h`, `SSD1306Wire.h`) that replaces real hardware libraries so the same app code compiles for the browser. |
| **Serial Monitor** | The panel in the App Builder that shows `Serial.println()` output from the running app. |
