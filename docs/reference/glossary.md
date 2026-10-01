# Glossary

Hover over terms in the docs to see short definitions. This page lists terms, acronyms, file types, and product names used in the documentation.

---

## Acronyms & abbreviations

| Term | Definition |
|------|------------|
| **A2DP** | Advanced Audio Distribution Profile — Bluetooth stereo audio streaming protocol. |
| **ADC** | Analog-to-Digital Converter — converts the slider's voltage to a number (e.g. 0–4095). |
| **API** | Application Programming Interface — how code talks to a library or service. |
| **BLE** | Bluetooth Low Energy — used for wireless features on the device. |
| **CC0** | Creative Commons Zero - a public-domain dedication that allows reuse without the usual copyright restrictions. |
| **CI** | Continuous Integration — automated builds (e.g. GitHub Actions compiling WASM). |
| **CMake** | Cross-platform build system used to configure the WASM/Emscripten build. |
| **CORS** | Cross-Origin Resource Sharing — browser rules that block loading WASM from `file://` URLs. |
| **CSS** | Cascading Style Sheets — used to style the emulator (LEDs, layout). |
| **DOM** | Document Object Model — the browser's representation of the page (buttons, canvas). |
| **DNS** | Domain Name System - turns names like cyberfidget.com into network addresses. On its own WiFi network the Fidget answers every name lookup with its own address, which is how the portal's sign-in page opens by itself. |
| **EDNS** | Extension Mechanisms for DNS - extra options many phones and browsers add to a name lookup. The Fidget's portal answers lookups with or without them. |
| **DER** | Distinguished Encoding Rules - a compact binary layout; firmware update signatures use it before being written as base64 text. |
| **DIO** | Dual input/output - a flash mode accepted in release metadata. |
| **ECDSA** | Elliptic Curve Digital Signature Algorithm - the method used to sign firmware updates, so a Fidget can check that an update came from Cyber Fidget. |
| **ESP32** | Espressif's 32-bit microcontroller — the main chip on Cyber Fidget hardware. |
| **FPS** | Frames Per Second — the emulator runs at 50 FPS like the real device. |
| **FreeRTOS** | Free Real-Time Operating System — the RTOS layer used by ESP-IDF under the hood. |
| **GPIO** | General-Purpose Input/Output — physical pins used for buttons, etc. |
| **HAL** | Hardware Abstraction Layer — the layer that swaps ESP32 drivers for browser equivalents in the emulator. |
| **I2C** | Inter-Integrated Circuit — serial bus used for the OLED, accelerometer, and fuel gauge. |
| **I2S** | Inter-IC Sound — digital audio bus used for the speaker amplifier and MEMS microphone. |
| **IDE** | Integrated Development Environment — e.g. the App Builder on the website. |
| **GPU** | Graphics Processing Unit — when the phone's browser exposes it, the companion transcribes speech much faster. |
| **IPv4 / IPv6** | Internet Protocol version 4 / version 6 - the two kinds of network address. IPv4 is the familiar four-number form, like `192.168.4.1`; IPv6 is the newer, longer form. |
| **IndexedDB** | Browser storage used to cache compiled WASM and the phone companion's one-time transcription download. |
| **JS** | JavaScript. |
| **JSON** | JavaScript Object Notation - a structured text format for storing data. |
| **LED** | Light-Emitting Diode. |
| **LiPo** | Lithium Polymer — rechargeable battery type used in Cyber Fidget (400 mAh). |
| **Li-ion** | Lithium-ion — a family of rechargeable battery chemistries. |
| **MCU** | Microcontroller Unit — the processor that controls an embedded device. |
| **MEMS** | Micro-Electro-Mechanical Systems — miniaturized sensor technology used in the ICS-43434 microphone. |
| **ms** | Millisecond - one thousandth of a second. |
| **NeoPixel** | Adafruit's addressable RGB(W) LED product line; firmware uses a shim that matches its API. |
| **NVS** | Non-Volatile Storage - the small settings area in the ESP32's flash that keeps saved WiFi networks, the account link, and other settings across restarts. |
| **OLED** | Organic Light-Emitting Diode — the 128×64 pixel display on Cyber Fidget. |
| **OTA** | Over-the-air update - firmware delivered over a network instead of a cable. On the device and website, the action is called an "update." |
| **P-256** | A standard elliptic curve (also called prime256v1); the firmware update signing key must use it. |
| **PCB** | Printed Circuit Board. |
| **PEM** | Privacy-Enhanced Mail - a text format for storing keys, used for the release signing key. |
| **PCM** | Pulse-Code Modulation — uncompressed digital audio stored as raw samples. |
| **PNG** | Portable Network Graphics - a common lossless image file format. Aseprite exports its sprite sheets as PNG images. |
| **PSRAM** | Pseudo-Static RAM - extra memory on the ESP32 module, used to buffer audio while recording and to run apps sent to the Fidget (a little slower than the chip's internal memory). |
| **QIO** | Quad input/output - a flash mode accepted in release metadata. |
| **RC** | Release Candidate - a test version of the firmware, tagged like `v1.4.0-rc1`. On the device and website it is called a "test version." |
| **RGBW** | Red, Green, Blue, White — four-channel LED color. |
| **RS-232** | Recommended Standard 232 — a serial communication standard. |
| **SD** | Secure Digital — the micro-SD card slot. |
| **SHA-256** | Secure Hash Algorithm 256-bit - a digest used to check that downloaded bytes match the update manifest. |
| **SPI** | Serial Peripheral Interface — serial bus used for the SD card. |
| **SPP** | Serial Port Profile — Bluetooth serial data streaming protocol. |
| **SSD1306** | The display controller chip used in the Cyber Fidget OLED. |
| **USB** | Universal Serial Bus — used for charging and serial communication via USB-C. |
| **URL** | Uniform Resource Locator - an address for a web resource. |
| **USB-C** | USB Type-C — the reversible connector used for charging and serial communication. |
| **UVLO** | Under-voltage lockout - a protective shutdown that stops the device from draining its battery below a safe level. |
| **VU** | Volume Unit — a level meter showing how loud the microphone is hearing you (used by the Voice Notes recorder). |
| **WASM** | WebAssembly — binary format that runs in the browser; the emulator runs C++ apps as WASM. |
| **WAV** | Waveform Audio File — uncompressed audio format; plays on nearly any phone or computer with no special software. Voice Notes recordings are saved as WAV. |
| **WebAssembly** | Binary instruction format for the web; the emulator compiles C++ to WASM. |
| **WebSocket** | A persistent two-way connection between a browser page and a server — the phone companion's live caption link to the device. |
| **Wi-Fi** | Wireless Fidelity — used for OTA and network features. |
| **Web Serial** | A browser feature that lets a web page talk to a device over a USB serial connection. Available in desktop Chromium-based browsers such as Chrome and Edge. |
| **mDNS** | Multicast DNS — the local-network name service that makes `cyberfidget.local` resolve without any router configuration. |
| **microSD** | Compact removable Secure Digital memory-card format. |

---

## Studio terms

| Term | Meaning |
|------|---------|
| **Animation state** | A named sequence of sprite frames for one action, such as running or jumping. |
| **Asset** | A sprite or model that can be used in a Studio project. |
| **Built app** | The runnable copy produced when Studio builds an app. |
| **Capture** | An item stored in a Studio project's captures. |
| **Companion page** | The phone companion's web page, built into firmware and optionally overridden from the memory card. |
| **Internal storage** | Storage built into the Cyber Fidget where apps live. |
| **Project** | A person's Studio work, including its code, art, captures, and settings. |
| **Project file** | A `.cfapp.json` file containing a whole Studio project. |
| **Sprite** | An image or animation used by an app for a character, object, or effect. |
| **Wireframe model** | A 3D shape built from points (nodes) connected by straight lines (struts), with no solid surfaces -- drawn as spinning line art on the device. |
| **Node** | A point in a wireframe model's shape, positioned in 3D space. |
| **Strut** | A straight line connecting two nodes in a wireframe model. |

---

## Website terms

| Term | Meaning |
|------|---------|
| **The Archives** | The shared collection of apps, screensavers, and sprite packs at cyberfidget.com/explore. |
| **Share sheet** | The list of apps your phone offers when you send something on to someone else. |
| **Base64** | A way of writing binary data as plain text using letters, digits, `+` and `/`; update signatures are sent this way. |
| **Digital signature** | A short code that only the holder of a private key can make for one exact file. Anyone with the matching public key can check it, and changing even one byte of the file makes the check fail. Cyber Fidget uses signatures to confirm that an update is official. |
| **Manifest (update manifest)** | A small JSON document that identifies a firmware download, its size and Secure Hash Algorithm 256-bit (SHA-256) hash, and the hardware it supports. See the [firmware update manifest reference](firmware-update-manifest.md). |
| **Reset to factory** | The **Settings > Reset to factory** item on the Fidget. It erases sent apps, saved WiFi, settings, the account link and the battery record, and keeps the firmware and the memory card. See [Update or reset your Fidget](../software/updating.md). |
| **Erase everything and reinstall** | The website's clean-start install over USB: it erases the whole Fidget and installs a fresh copy of the chosen firmware version. See [Update or reset your Fidget](../software/updating.md#erase-everything-and-reinstall-on-the-website). |
| **Test version** | An early firmware build for trying new features before everyone gets them (a release candidate). Chosen with **Settings > Updates > Versions: Test** or from the **Test versions** group on the website update page. |
| **Check-in** | A linked Fidget contacting the website over its own WiFi to collect waiting app changes and look for firmware updates. See [Updates](../software/updates.md#when-it-checks). |
| **Sync session** | A run of USB serial commands from the website (or your own program) that copies apps and the menu to the Fidget. While one is active, the Fidget holds off its WiFi check-ins. See [Serial commands](serial-commands.md#sync-sessions-and-a-busy-fidget). |
| **Model (code generator)** | The service a provider (Anthropic, OpenAI, or Google) runs to write app code from your description in the App Builder. See [Choosing a model](../software/ota-builder.md#choosing-a-model). |
| **Pairing / linking** | Establishing an association between a Cyber Fidget and an account. On the device and website, the action is called "link your Fidget." |

---

## File types & artifacts

| Term | Meaning |
|------|--------|
| **.cfapp.json** | Studio whole-project file containing code, sprites, models, captures, and settings. |
| **.cfmesh.json** | Studio file containing one model. |
| **.cfsprite.json** | Studio file containing one sprite. |
| **.cpp** | C++ source file (implementation). |
| **.h** | C/C++ header file (declarations). |
| **.js** | JavaScript file — the Emscripten "loader" that loads and runs the WASM module. |
| **.wasm** | WebAssembly binary — the compiled app. |
| **.wav** | Waveform audio file — the uncompressed recordings made by the Voice Notes app. |
| **.yml / .yaml** | YAML config — e.g. GitHub Actions workflow or MkDocs config. |

---

## Products & projects

| Term | Meaning |
|------|--------|
| **Adafruit** | Maker electronics company; NeoPixel and many Arduino libraries. |
| **AP2112K** | Diodes Inc. 3.3V LDO regulator — used for main logic, OLED, and LED power rails. |
| **CircuitPython** | Adafruit's Python runtime for microcontrollers. Hardware support designed-in but currently untested on Cyber Fidget. |
| **CP2102N** | Silicon Labs USB-to-UART bridge chip — provides the serial connection over USB-C. |
| **CRC-32** | Cyclic Redundancy Check, 32-bit - a checksum used to detect damaged data. |
| **CF_TEST_CLI** | Firmware build option that includes extra device testing commands. |
| **baud** | Serial connection speed, measured in transmitted symbols per second. |
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
