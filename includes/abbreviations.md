*[A2DP]: Advanced Audio Distribution Profile; Bluetooth stereo audio
*[ADC]: Analog-to-Digital Converter
*[API]: Application Programming Interface
*[BLE]: Bluetooth Low Energy
*[CC0]: Creative Commons Zero; a public-domain dedication that allows reuse without the usual copyright restrictions
*[CI]: Continuous Integration
*[CMake]: Cross-platform Make; build system used for the WASM build
*[CORS]: Cross-Origin Resource Sharing
*[CP2102N]: Silicon Labs USB-to-UART bridge chip
*[CRC-32]: Cyclic Redundancy Check, 32-bit; a checksum used to detect damaged data
*[CF_TEST_CLI]: Firmware build option that includes extra device testing commands
*[baud]: Serial connection speed, measured in transmitted symbols per second
*[CSS]: Cascading Style Sheets
*[DNS]: Domain Name System; turns names like cyberfidget.com into network addresses
*[EDNS]: Extension Mechanisms for DNS; extra options many phones and browsers add to a name lookup
*[IPv4]: Internet Protocol version 4; the familiar four-number network address, like 192.168.4.1
*[IPv6]: Internet Protocol version 6; the newer, longer kind of network address
*[DOM]: Document Object Model
*[DER]: Distinguished Encoding Rules; a compact binary layout used here for a digital signature
*[ECDSA]: Elliptic Curve Digital Signature Algorithm; the signing method used for official firmware updates
*[DIO]: Dual input/output flash mode
*[ESP32]: Espressif Systems 32-bit microcontroller used in Cyber Fidget hardware
*[FPS]: Frames Per Second
*[FreeRTOS]: Free Real-Time Operating System; used by ESP-IDF
*[GPIO]: General-Purpose Input/Output
*[GPU]: Graphics Processing Unit; phones with browser GPU access transcribe faster
*[HAL]: Hardware Abstraction Layer
*[harmonics]: Quieter extra pitches at 2x, 3x, 4x... a note's frequency that are mixed into a sound; they make it richer and let a small speaker hint at low notes
*[Hz]: Hertz; vibrations per second, the unit of pitch (higher Hz = higher note)
*[kHz]: Kilohertz; 1000 Hz
*[I2C]: Inter-Integrated Circuit; serial bus used for OLED and some sensors
*[I2S]: Inter-IC Sound; digital audio interface
*[IDE]: Integrated Development Environment
*[IndexedDB]: Browser key-value database used to cache compiled WASM and the companion's transcription pack
*[JS]: JavaScript
*[JSON]: JavaScript Object Notation; a structured text format for storing data
*[LED]: Light-Emitting Diode
*[LiPo]: Lithium Polymer battery
*[Li-ion]: Lithium-ion rechargeable battery
*[MCU]: Microcontroller Unit; the main processor in an embedded device
*[MEMS]: Micro-Electro-Mechanical Systems
*[ms]: Millisecond; one thousandth of a second
*[NeoPixel]: Adafruit brand of addressable RGB(W) LEDs
*[OLED]: Organic Light-Emitting Diode; the 128×64 display on Cyber Fidget
*[OTA]: Over-the-air update; firmware delivered over a network instead of a cable. Product controls say "update".
*[P-256]: A standard elliptic curve (also called prime256v1) used by the firmware update signing key
*[PCB]: Printed Circuit Board
*[PEM]: Privacy-Enhanced Mail; a text format for storing keys, such as the release signing key
*[PCM]: Pulse-Code Modulation; uncompressed digital audio samples
*[PNG]: Portable Network Graphics; a common lossless image file format
*[PSRAM]: Pseudo-Static RAM; extra memory used to buffer audio while recording and to run apps sent to the Fidget
*[QIO]: Quad input/output flash mode
*[RC]: Release Candidate; a test version of the firmware, tagged like v1.4.0-rc1
*[RGBW]: Red, Green, Blue, White (four-channel LED)
*[RS-232]: Recommended Standard 232; a serial communication standard
*[SD]: Secure Digital (memory card)
*[SHA-256]: Secure Hash Algorithm 256-bit; a digest used to check that downloaded bytes match the manifest
*[SK6812]: Addressable RGBW LED (NeoPixel-compatible)
*[SPI]: Serial Peripheral Interface
*[SPP]: Serial Port Profile; Bluetooth serial data
*[SSD1306]: Display controller chip used in the Cyber Fidget OLED
*[USB]: Universal Serial Bus
*[URL]: Uniform Resource Locator; an address for a web resource
*[USB-C]: USB Type-C; reversible connector used for charging and serial communication
*[UVLO]: Under-voltage lockout - a protective shutdown that stops the device from draining its battery below a safe level.
*[VU]: Volume Unit; a meter showing how loud the incoming sound is
*[WASM]: WebAssembly
*[WAV]: Waveform Audio File; uncompressed audio that plays on almost any device
*[WebAssembly]: Binary instruction format that runs in the browser; used to run C++ app code in the emulator
*[WebSocket]: Persistent two-way browser connection; carries the live caption link between device and phone
*[Wi-Fi]: Wireless Fidelity
*[NVS]: Non-Volatile Storage; the small settings area in the ESP32's flash that keeps saved WiFi and other settings across restarts
*[Web Serial]: Browser feature that lets a web page talk to a device over a USB serial connection; available in desktop Chromium-based browsers
*[mDNS]: Multicast DNS; the local-network name service that makes cyberfidget.local resolve without a router change
*[microSD]: Compact removable Secure Digital memory-card format
*[The Archives]: The shared collection of apps, screensavers, and sprite packs at cyberfidget.com/explore
*[share sheet]: The list of apps your phone offers when you send something on to someone else
*[animation state]: Named sequence of sprite frames for one action
*[built app]: The runnable copy produced when Studio builds an app
*[companion page]: The phone companion's web page, built into firmware and optionally overridden from the memory card
*[internal storage]: Storage built into the Cyber Fidget where apps live
*[project file]: A .cfapp.json file containing a whole Studio project
*[sprite]: Image or animation used by an app for a character, object, or effect
*[node]: A point in a wireframe model's shape, positioned in 3D space
*[strut]: A straight line connecting two nodes in a wireframe model
*[wireframe model]: A 3D shape built from points (nodes) connected by straight lines (struts), with no solid surfaces
*[.cfapp.json]: Studio whole-project file containing code, sprites, models, captures, and settings
*[.cfmesh.json]: Studio file containing one model
*[.cfsprite.json]: Studio file containing one sprite
*[base64]: A way of writing binary data as plain text using letters, digits, + and /
