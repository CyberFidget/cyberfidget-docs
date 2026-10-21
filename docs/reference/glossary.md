# Glossary

Hover over terms in the docs to see short definitions. This page lists terms, acronyms, file types, and product names used in the documentation.

---

## Acronyms & abbreviations

| Term | Definition |
|------|------------|
| **A2DP** | Advanced Audio Distribution Profile -- Bluetooth stereo audio streaming protocol. |
| **Accelerometer** | A motion sensor that measures acceleration, including gravity, so the device can tell which way it is tilted or when it is shaken. See [Motion Sensing](../concepts/accelerometer.md). |
| **ADC** | Analog-to-Digital Converter -- converts the slider's voltage to a number (e.g. 0-4095). |
| **API** | Application Programming Interface -- how code talks to a library or service. |
| **Binary angle** | An angle stored as a whole number from 0 to 255, where 256 steps make one full turn (64 is a quarter turn). The 3D model functions use binary angles. |
| **BLE** | Bluetooth Low Energy -- used for wireless features on the device. |
| **CC BY-SA** | Creative Commons Attribution-ShareAlike - others may reuse and change the work if they credit the maker and share their version under the same license. Shared art uses version 4.0. |
| **CC0** | Creative Commons Zero - a public-domain dedication that allows reuse without the usual copyright restrictions. |
| **CI** | Continuous Integration -- automatic checks and builds triggered by code changes. A studio app can build on your computer or the build server. |
| **CMake** | Cross-platform build system used to configure the WASM/Emscripten build. |
| **CORS** | Cross-Origin Resource Sharing -- browser rules that block loading WASM from `file://` URLs. |
| **CSS** | Cascading Style Sheets -- used to style the emulator (LEDs, layout). |
| **dB** | Decibel - a unit for comparing loudness. 3 dB quieter is about half the power. |
| **dBFS** | Decibels relative to Full Scale - a loudness scale where 0 is the loudest level the microphone can measure and quieter sounds are negative numbers (for example -60 for a quiet room). |
| **DER** | Distinguished Encoding Rules - a compact binary layout; firmware update signatures use it before being written as base64 text. |
| **DIO** | Dual input/output - a flash mode accepted in release metadata. |
| **DNS** | Domain Name System - turns names like cyberfidget.com into network addresses. On its own WiFi network the Fidget answers every name lookup with its own address, which is how the portal's sign-in page opens by itself. |
| **DOM** | Document Object Model -- the browser's representation of the page (buttons, canvas). |
| **ECDSA** | Elliptic Curve Digital Signature Algorithm - the method used to sign firmware updates, so a Fidget can check that an update came from Cyber Fidget. |
| **EDNS** | Extension Mechanisms for DNS - extra options many phones and browsers add to a name lookup. The Fidget's portal answers lookups with or without them. |
| **EMA** | Exponential Moving Average; smoothing that blends each reading with previous readings. |
| **EQ** | Equalizer - a filter that makes some pitches louder or quieter. The speaker's EQ lifts the pitches the small speaker plays well. |
| **ESP32** | Espressif's 32-bit microcontroller -- the main chip on Cyber Fidget hardware. |
| **FPS** | Frames Per Second -- the emulator runs at 50 FPS like the real device. |
| **FreeRTOS** | Free Real-Time Operating System -- the RTOS layer used by ESP-IDF under the hood. |
| **GPIO** | General-Purpose Input/Output -- physical pins used for buttons, etc. |
| **GPU** | Graphics Processing Unit -- when the phone's browser exposes it, the companion transcribes speech much faster. |
| **HAL** | Hardware Abstraction Layer -- the layer that swaps ESP32 drivers for browser equivalents in the emulator. |
| **Harmonics** | Quieter extra pitches at 2x, 3x, 4x... a note's frequency, mixed into the sound. A small speaker that cannot reproduce a low note can still play its harmonics, so the note stays recognizable but quieter. |
| **Hz / kHz** | Hertz / kilohertz -- vibrations per second (1 kHz = 1000 Hz); the unit of pitch. Higher is a higher note. |
| **I2C** | Inter-Integrated Circuit -- serial bus used for the OLED, accelerometer, and fuel gauge. |
| **I2S** | Inter-IC Sound -- digital audio bus used for the speaker amplifier and MEMS microphone. |
| **IDE** | Integrated Development Environment -- e.g. the App Builder on the website. |
| **IndexedDB** | A database built into the browser. The studio uses it for built apps; the phone companion uses it for its transcription download. |
| **IPv4 / IPv6** | Internet Protocol version 4 / version 6 - the two kinds of network address. IPv4 is the familiar four-number form, like `192.168.4.1`; IPv6 is the newer, longer form. |
| **JS** | JavaScript. |
| **JSON** | JavaScript Object Notation - a structured text format for storing data. |
| **Kalman filter** | A calculation that estimates a stable value from noisy sensor readings. |
| **LED** | Light-Emitting Diode. |
| **Li-ion** | Lithium-ion -- a family of rechargeable battery chemistries. |
| **LiPo** | Lithium Polymer -- rechargeable battery type used in Cyber Fidget (400 mAh). |
| **MCU** | Microcontroller Unit -- the processor that controls an embedded device. |
| **mDNS** | Multicast DNS -- the local-network name service that makes `cyberfidget.local` resolve without any router configuration. |
| **MEMS** | Micro-Electro-Mechanical Systems -- miniaturized sensor technology used in the ICS-43434 microphone. |
| **microSD** | Compact removable Secure Digital memory-card format. |
| **milli-g** | One thousandth of the acceleration due to gravity; 1000 milli-g is one g. |
| **MIT License** | A short permissive license: anyone may use, change and share the code as long as the license notice stays with it. Shared app code uses it. |
| **ms** | Millisecond - one thousandth of a second. |
| **NeoPixel** | Adafruit's addressable RGB(W) LED product line; firmware uses a shim that matches its API. |
| **NTP** | Network Time Protocol; a way to set a clock from a network time server. |
| **NUL** | The character with code 0. C uses it to mark the end of text, so a serial command line may not contain one. |
| **NVS** | Non-Volatile Storage - the small settings area in the ESP32's flash that keeps saved WiFi networks, the account link, and other settings across restarts. |
| **OLED** | Organic Light-Emitting Diode -- the 128 x 64 pixel display on Cyber Fidget. |
| **OTA** | Over-the-air update - firmware delivered over a network instead of a cable. On the device and website, the action is called an "update." |
| **P-256** | A standard elliptic curve (also called prime256v1); the firmware update signing key must use it. |
| **PCB** | Printed Circuit Board. |
| **PCM** | Pulse-Code Modulation -- uncompressed digital audio stored as raw samples. |
| **PEM** | Privacy-Enhanced Mail - a text format for storing keys, used for the release signing key. |
| **PNG** | Portable Network Graphics - a common lossless image file format. Aseprite can export its sprite sheets as PNG images. |
| **PSRAM** | Pseudo-Static RAM - extra memory on the ESP32 module, used to buffer audio while recording and to run apps sent to the Fidget (a little slower than the chip's internal memory). |
| **Q8 / Q14** | Whole numbers that stand for fractions: a Q8 value divided by 256, or a Q14 value divided by 16384, gives the real value. A model size of 256 in Q8 means 1.0, normal size. |
| **QIO** | Quad input/output - a flash mode accepted in release metadata. |
| **RC** | Release Candidate - a test version of the firmware, tagged like `v1.4.0-rc1`. On the device and website it is called a "test version." |
| **RGBW** | Red, Green, Blue, White -- four-channel LED color. |
| **RS-232** | Recommended Standard 232 -- a serial communication standard. |
| **SD** | Secure Digital -- the micro-SD card slot. |
| **SHA-256** | Secure Hash Algorithm 256-bit - a digest used to check that downloaded bytes match the update manifest. |
| **SPH** | Smoothed Particle Hydrodynamics; a way to simulate fluids with interacting particles. |
| **SPI** | Serial Peripheral Interface -- serial bus used for the SD card. |
| **SPP** | Serial Port Profile -- Bluetooth serial data streaming protocol. |
| **SSD1306** | The display controller chip used in the Cyber Fidget OLED. |
| **SSID** | Service Set Identifier - the name of a WiFi network. Over USB the Fidget sends it as hex; see [Set up WiFi over USB](usb-wifi-setup.md). |
| **URL** | Uniform Resource Locator - an address for a web resource. |
| **USB** | Universal Serial Bus -- used for charging and serial communication via USB-C. |
| **USB-C** | USB Type-C -- the reversible connector used for charging and serial communication. |
| **UTF-8** | The standard way of storing text of any language as bytes. |
| **UVLO** | Under-voltage lockout - a protective shutdown that stops the device from draining its battery below a safe level. |
| **VU** | Volume Unit -- a level meter showing how loud the microphone is hearing you (used by the Voice Notes recorder). |
| **WASM** | WebAssembly -- binary format that runs in the browser; the emulator runs C++ apps as WASM. |
| **WAV** | Waveform Audio File -- uncompressed audio format; plays on nearly any phone or computer with no special software. Voice Notes recordings are saved as WAV. |
| **Web Serial** | A browser feature that lets a web page talk to a device over a USB serial connection. Available in desktop Chromium-based browsers such as Chrome and Edge. |
| **WebAssembly** | Binary instruction format for the web; the emulator compiles C++ to WASM. |
| **WebSocket** | A persistent two-way connection between a browser page and a server -- the phone companion's live caption link to the device. |
| **Wi-Fi** | Wireless Fidelity -- used for OTA and network features. |
| **Wireframe** | A 3D shape drawn only as points and the straight lines between them, with no solid sides. |
| **XBM** | X BitMap; a one-bit image format with on/off pixels stored in bytes. |

---

## Studio terms

| Term | Meaning |
|------|---------|
| ***** | In a declaration, marks a pointer that holds an address; before a pointer, reads the object at that address. |
| **&** | In a parameter type, a reference to an existing object rather than a copy; before a value, its address. |
| **Actor** | A thing on the screen in an app: a position plus an animation that is playing. See [Sprites & Animation](../concepts/sprites.md#actors). |
| **Animation** | Named sequence of sprite frames for one action; the editor's name for an animation state. |
| **Animation player** | Code that keeps track of time and says which frame of an animation to show; `AnimationPlayer` in the sprite functions. See [Sprites & Animation](../concepts/sprites.md#animations-and-sprite-sheets). |
| **Animation state** | A named sequence of sprite frames for one action, such as running or jumping. |
| **Array** | A numbered list of values of one type, such as the bytes of a picture. |
| **Asset** | A sprite or model that can be used in a Studio project. |
| **Bitmap** | A picture stored as a grid of on/off pixels. |
| **bool** | A C++ type holding either true or false. |
| **buffer** | An area of memory holding data while code works on it; the drawing buffer holds the next screen image. |
| **Build** | Studio's step that turns your project, including its art, into a runnable app. |
| **Built app** | The runnable copy produced when Studio builds an app. |
| **Callback** | A function you give the device to call for you when something happens, such as a button press. |
| **Capture** | An item stored in a Studio project's captures. |
| **Cel** | An animator's word for one picture of an animation; the studio names a sprite's frames `cel_0`, `cel_1` and so on in code. |
| **Collision** | Two sprites touching, where a lit pixel of one sits on a lit pixel of the other. See [Sprites & Animation](../concepts/sprites.md#collision). |
| **Companion page** | The phone companion's web page, built into firmware and optionally overridden from the memory card. |
| **Compile** | Turn the code you wrote into a program the device (or the emulator) can run. |
| **Computational thinking** | Ways of solving problems that suit computers: breaking them into pieces (decomposition), spotting patterns, leaving out detail you don't need, and writing step-by-step instructions. See [Make a game, step by step](../getting-started/make-a-game.md#step-0-plan-the-game). |
| **const** | Marks a value that cannot be changed through this declaration; after a method signature, the method does not change its object. |
| **const char*** | A pointer to text ending with a zero character; the characters cannot be changed through this pointer. |
| **Core loop** | The action a player repeats all game long, such as moving a paddle to catch a dot. See [Make a game, step by step](../getting-started/make-a-game.md#2-group-the-ideas-by-what-they-do). |
| **Decomposition** | Breaking a big problem or idea into small pieces you can solve one at a time. See [Make a game, step by step](../getting-started/make-a-game.md#step-0-plan-the-game). |
| **Emulator** | A copy of the device that runs in your browser, so you can try an app without a Cyber Fidget. |
| **Firmware** | The built-in software that runs on the device. |
| **Fixed-point** | Counting in fractions with whole numbers, for example 256 units per pixel, so movement can be smoother than one pixel at a time. |
| **float** | A C++ number type that can hold a fractional part. |
| **Flow** | How densely the Brush paints or the Erase tool removes pixels, from 0 to 100%. |
| **Frame** | One picture in an animation sequence. |
| **Frame rate** | Number of frames shown each second. |
| **framebuffer** | A buffer that stores the pixel values for a screen image. |
| **GIF** | Graphics Interchange Format; an image file format that can store an animation. |
| **GRBW** | Green, Red, Blue, White; the order used to send channels to the LED hardware. |
| **int** | A signed whole number; on the device, -2,147,483,648 to 2,147,483,647. |
| **int16_t** | A signed whole number from -32,768 to 32,767. |
| **int32_t** | A signed whole number from -2,147,483,648 to 2,147,483,647. |
| **Internal storage** | Storage built into the Cyber Fidget where apps live. |
| **Juice** | Extra feedback, such as flashes, sounds and shakes, that makes an action in a game feel good. See [Make a game, step by step](../getting-started/make-a-game.md#2-group-the-ideas-by-what-they-do). |
| **lambda** | A short unnamed C++ function. |
| **Layer** | Separate set of pixels in a frame, with its own drawing order and visibility. |
| **long** | A signed whole number; on the device, -2,147,483,648 to 2,147,483,647. |
| **Loop mode** | What an animation does after its last frame: start again, play backward, stop, or hold the last frame. See [Loop modes](../concepts/sprites.md#loop-modes). |
| **macro** | Named code expanded by the C++ preprocessor before compilation. |
| **MB** | Megabyte; a unit of file size, about one million bytes. |
| **Mesh** | A 3D model's data: its list of points and its list of lines. `Mesh` in the 3D functions. See [3D Models](../concepts/3d-models.md). |
| **mg** | Milli-g in motion readings; one thousandth of the acceleration due to gravity. |
| **Mirror twin** | In the 3D tab with Mirror on, the matching point or line on the other side of a model's middle; editing one changes the other the same way. See [3D Models in the Studio](../studio/3d-models.md#editing-a-model). |
| **Namespace** | A family name for a group of C++ names, such as `cf::gfx`, that keeps them apart from other code using the same names. |
| **Node** | A point in a wireframe model's shape, positioned in 3D space. |
| **nullptr** | A C++ value meaning a pointer does not point to an object. |
| **pivot** | The point on a sprite placed at its screen position. |
| **Pointer** | A value that holds the address of something else in memory, written with `*` in its type, such as `const Sprite*`. |
| **pose** | A set of bone angles describing how a figure is positioned. |
| **potentiometer** | A variable resistor; moving the slider changes the voltage read by the device. |
| **Project** | A person's Studio work, including its code, art, captures, and settings. |
| **Project file** | A `.cfapp.json` file containing a whole Studio project. |
| **Pseudo-code** | The steps of a program written in plain words, laid out like code but not in any programming language. |
| **rig** | Connected bones and poses used to animate a figure. |
| **ring buffer** | A queue that reuses a fixed amount of memory. |
| **singleton** | An object shared through one instance. |
| **Sprite** | An image or animation used by an app for a character, object, or effect. |
| **Sprite sheet** | A named group of animations for one character or object. See [Sprites & Animation](../concepts/sprites.md#animations-and-sprite-sheets). |
| **static** | In front of a variable or function at the top of a file: keeps it to that file, and a variable keeps its value for as long as the app runs. |
| **String** | A C++ object holding text. |
| **Strut** | A straight line connecting two nodes in a wireframe model. |
| **uint16_t** | A whole number from 0 to 65,535. |
| **uint32_t** | A whole number from 0 to 4,294,967,295. |
| **uint8_t** | A whole number from 0 to 255. |
| **unsigned long** | A non-negative whole number; on the device, 0 to 4,294,967,295, used for elapsed time. |
| **Viewport** | Visible area of the canvas. |
| **void** | A return type meaning that a function returns no value. |
| **Wireframe model** | A 3D shape built from points (nodes) connected by straight lines (struts), with no solid surfaces -- drawn as spinning line art on the device. |
| **OBJ** | Wavefront OBJ, a plain-text 3D model file listing vertices and the faces or lines that join them. Studio can import it. |
| **STL** | Stereolithography file, a 3D model file made of triangles, common in 3D printing. Studio can import it. |
| **Vertex** | A corner point of a 3D model; becomes a node in Studio. |
| **Triangle** | A flat three-cornered patch; most 3D programs build every face from triangles. |
| **Decimate** | Reduce a 3D model to fewer triangles while keeping its overall shape. |

---

## Website terms

| Term | Meaning |
|------|---------|
| **API key** | A secret code from a model provider's developer website that lets the studio's code generator use your own account with that provider; the provider charges you for what you use. See [Use your own key](../software/credits.md#use-your-own-key). |
| **Base64** | A way of writing binary data as plain text using letters, digits, `+` and `/`; update signatures are sent this way. |
| **Check-in** | A linked Fidget contacting the website over its own WiFi to collect waiting app changes and look for firmware updates. See [Updates](../software/updates.md#when-it-checks). |
| **Closed beta** | A feature open only to accounts that have been given access, while it is being tried out. See [Beta Access](../software/beta-access.md). |
| **Credits** | Units on a signed-in account that pay for code generator requests. Credits are rolling out. See [Use my credits](../software/credits.md#use-my-credits). |
| **Digital signature** | A short code that only the holder of a private key can make for one exact file. Anyone with the matching public key can check it, and changing even one byte of the file makes the check fail. Cyber Fidget uses signatures to confirm that an update is official. |
| **Erase everything and reinstall** | The website's clean-start install over USB: it erases the whole Fidget and installs a fresh copy of the chosen firmware version. See [Update or reset your Fidget](../software/updating.md#erase-everything-and-reinstall-on-the-website). |
| **Free allowance** | Code generator requests you can use without sign-in or payment. The studio shows how many free generations you have and when they reset. See [Free (built-in)](../software/credits.md#free-built-in). |
| **Host** | Firmware code that runs a studio app, on the device or in the browser emulator. |
| **Loadout** | The collection of apps and menu choices for your Fidget. |
| **Manifest (update manifest)** | A small JSON document that identifies a firmware download, its size and Secure Hash Algorithm 256-bit (SHA-256) hash, and the hardware it supports. See the [firmware update manifest reference](firmware-update-manifest.md). |
| **Model (code generator)** | The program a provider runs to write app code from your description in the App Builder. See [Code generator](../software/code-generator.md) and [Choosing a model](../software/ota-builder.md#choosing-a-model). |
| **Pairing / linking** | Establishing an association between a Cyber Fidget and an account. On the device and website, the action is called "link your Fidget." |
| **Polyphony** | Playing several notes at the same time, such as a chord. In an app, use `playNote()`; see [Notes](../concepts/audio.md#notes-several-sounds-at-once). |
| **Remix** | Make your own copy of something another person shared, such as an app or art from The Archives, and change it. |
| **Reset to factory** | The **Settings > Reset to factory** item on the Fidget. It erases sent apps, saved WiFi, settings, the account link and the battery record, and keeps the firmware and the memory card. See [Update or reset your Fidget](../software/updating.md). |
| **Share link** | An unlisted link to a copy of something you made in Studio, as it was when you shared it. Anyone holding the link can open and forward it. See [Share a link](../software/import-export.md#share-a-link). |
| **Share sheet** | The list of apps your phone offers when you send something on to someone else. |
| **Sync session** | A run of USB serial commands from the website (or your own program) that copies apps and the menu to the Fidget. While one is active, the Fidget holds off its WiFi check-ins. See [Serial commands](serial-commands.md#sync-sessions-and-a-busy-fidget). |
| **Test version** | An early firmware build for trying features before general release (a release candidate). Chosen with **Settings > Updates > Versions: Test** or from the **Test versions** group on the website update page. |
| **The Archives** | The shared collection of apps, screensavers, sprite packs and models at cyberfidget.com/explore. Makers submit their apps for review before they are listed. See [Get apps from The Archives](../software/sharing-apps.md). |
| **Token (code generator)** | A small piece of text, often part of a word. Model providers count and charge by tokens, and **Max output tokens** limits the length of one reply. |

---

## File types & artifacts

| Term | Meaning |
|------|--------|
| **.cfapp.json** | Studio whole-project file containing code, sprites, models, captures, and settings. |
| **.cfmesh.json** | Studio file containing one model. |
| **.cfsprite.json** | Studio file containing one sprite. |
| **.cpp** | C++ source file (implementation). |
| **.h** | C/C++ header file (declarations). |
| **.js** | JavaScript file -- code run by a web page or browser worker (a background task). The studio uses JavaScript for its interface, build tools and emulator; a built app is a .wasm file. |
| **.wasm** | WebAssembly binary -- the compiled app. |
| **.wav** | Waveform audio file -- the uncompressed recordings made by the Voice Notes app. |
| **.yml / .yaml** | YAML config -- e.g. GitHub Actions workflow or MkDocs config. |

---

## Products & projects

| Term | Meaning |
|------|--------|
| **Adafruit** | Maker electronics company; NeoPixel and many Arduino libraries. |
| **AP2112K** | Diodes Inc. 3.3V LDO regulator -- used for main logic, OLED, and LED power rails. |
| **baud** | Serial connection speed, measured in transmitted symbols per second. |
| **CF_TEST_CLI** | Firmware build option that includes extra device testing commands. |
| **chamfer** | A 45-degree angled cut on a corner. The case has one at each corner of the screen opening, hiding about 8 pixels of the display there. |
| **CircuitPython** | Adafruit's Python runtime for microcontrollers. Hardware support designed-in but currently untested on Cyber Fidget. |
| **CP2102N** | Silicon Labs USB-to-UART bridge chip -- provides the serial connection over USB-C. |
| **CRC-32** | Cyclic Redundancy Check, 32-bit - a checksum used to detect damaged data. |
| **Cyber Fidget** | The physical device and ecosystem (hardware, firmware, website, docs). |
| **Emscripten** | Toolchain that compiles C/C++ to WebAssembly and JavaScript. |
| **GitHub Actions** | GitHub service that runs automated checks and builds for a repository. Studio app builds do not require your own fork; they can run on your computer or the build server. |
| **Home Assistant** | Free, open-source home automation software that runs on a computer on your home network and controls smart lights, speakers and other devices. The Home Remote app talks to it. |
| **Home Remote** | The built-in app that controls Home Assistant lights, speakers, scenes and scripts. See [Home Remote](../firmware/home-remote.md). |
| **ICS-43434** | InvenSense/TDK I2S MEMS microphone used in Cyber Fidget. |
| **LIS2DH12** | STMicroelectronics 3-axis digital accelerometer used in Cyber Fidget. |
| **Long-lived access token** | A key you make in your Home Assistant profile that lets another program use your Home Assistant. Home Remote calls it the access key. |
| **MAX17048** | Analog Devices/Maxim fuel gauge IC for LiPo battery state-of-charge monitoring. |
| **MAX98357A** | Analog Devices/Maxim I2S Class-D amplifier driving the on-board speaker. |
| **MCP73831** | Microchip single-cell LiPo charge management controller. |
| **pioarduino** | Community-maintained PlatformIO platform fork for ESP32 (ESP-IDF 5.1.4 + Arduino ESP32 3.0.3). |
| **PlatformIO** | IDE and build system for embedded development; recommended for Cyber Fidget via the pioarduino fork. |
| **PROGMEM** | Program memory; marks constant data for storage with the program on embedded boards. |
| **Scene (Home Assistant)** | Saved settings for several devices that Home Assistant applies together. Home Remote can run one. |
| **Script (Home Assistant)** | A list of actions Home Assistant runs in order. Home Remote can start one. |
| **SK6812** | Individually addressable RGBW LED (NeoPixel-compatible) -- four are used in Cyber Fidget. |
| **ThingPulse** | Source of the OLED font data used in the WASM shim. |

---

## Emulator-specific

| Term | Meaning |
|------|--------|
| **Bridge** | `wasm_bridge.js` -- glue between the WASM module and the on-screen emulator. |
| **Serial Monitor** | A tool for reading serial messages from firmware over a cable. The studio panel is called Console; it shows build and run messages. Studio apps cannot use `Serial.println()`. |
| **Shim** | A stub header (e.g. `Arduino.h`, `SSD1306Wire.h`) that replaces real hardware libraries so the same app code compiles for the browser. |
