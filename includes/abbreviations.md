*[A2DP]: Advanced Audio Distribution Profile; Bluetooth stereo audio
*[ADC]: Analog-to-Digital Converter
*[API]: Application Programming Interface
*[BLE]: Bluetooth Low Energy
*[CC0]: Creative Commons Zero; a public-domain dedication that allows reuse without the usual copyright restrictions
*[CI]: Continuous Integration; automated checks and builds triggered by code changes
*[CMake]: Cross-platform Make; build system used for the WASM build
*[CORS]: Cross-Origin Resource Sharing
*[CP2102N]: Silicon Labs USB-to-UART bridge chip
*[CRC-32]: Cyclic Redundancy Check, 32-bit; a checksum used to detect damaged data
*[CF_TEST_CLI]: Firmware build option that includes extra device testing commands
*[Home Assistant]: Free, open-source home automation software that runs on your home network; the Home Remote app talks to it
*[NUL]: The character with code 0; it marks the end of text in C, so a command line may not contain one
*[chamfer]: A 45-degree angled cut on a corner; the case hides about 8 pixels of the screen at each corner
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
*[dBFS]: Decibels relative to Full Scale; 0 is the loudest level the microphone can measure and quieter sounds are negative
*[dB]: Decibel, a unit for comparing loudness; 3 dB quieter is about half the power
*[EQ]: Equalizer, a filter that makes some pitches louder or quieter
*[polyphony]: Playing several notes at the same time
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
*[IndexedDB]: A database built into the browser; used for studio built apps and the companion's transcription download
*[JS]: JavaScript
*[JSON]: JavaScript Object Notation; a structured text format for storing data
*[LED]: Light-Emitting Diode
*[LiPo]: Lithium Polymer battery
*[Li-ion]: Lithium-ion rechargeable battery
*[MCU]: Microcontroller Unit; the main processor in an embedded device
*[MEMS]: Micro-Electro-Mechanical Systems
*[ms]: Millisecond; one thousandth of a second
*[MB]: Megabyte; a unit of file size, about one million bytes
*[NeoPixel]: Adafruit brand of addressable RGB(W) LEDs
*[OLED]: Organic Light-Emitting Diode; the 128×64 display on Cyber Fidget
*[OTA]: Over-the-air update; firmware delivered over a network instead of a cable. Product controls say "update".
*[P-256]: A standard elliptic curve (also called prime256v1) used by the firmware update signing key
*[PCB]: Printed Circuit Board
*[PEM]: Privacy-Enhanced Mail; a text format for storing keys, such as the release signing key
*[PCM]: Pulse-Code Modulation; uncompressed digital audio samples
*[PNG]: Portable Network Graphics; a common lossless image file format
*[PSRAM]: Pseudo-Static RAM; extra memory used to buffer audio while recording and to run apps sent to the Fidget
*[Q8]: A whole number that stands for a fraction: divide it by 256 to get the real value, so 256 means 1.0
*[Q14]: A whole number that stands for a fraction: divide it by 16384 to get the real value, so 16384 means 1.0
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
*[GIF]: Graphics Interchange Format; an image file format that can store an animation

*[CC BY-SA]: Creative Commons Attribution-ShareAlike; reuse requires attribution and sharing adaptations under the same license
*[MIT License]: Permissive code license requiring the license notice to stay with copies
*[emulator]: A copy of the device that runs in your browser, so you can try an app without a Cyber Fidget
*[compile]: Turn the code you wrote into a program the device (or the emulator) can run
*[callback]: A function you give the device to call for you when something happens, such as a button press
*[pivot]: The point on a sprite placed at its screen position
*[bitmap]: A picture stored as a grid of on/off pixels
*[sprite sheet]: A named group of animations for one character or object
*[actor]: A thing on the screen in an app: a position plus an animation that is playing
*[collision]: Two sprites touching, where a lit pixel of one sits on a lit pixel of the other
*[rig]: Connected bones and poses used to animate a figure
*[pose]: A set of bone angles describing how a figure is positioned
*[EMA]: Exponential Moving Average; smoothing that blends each reading with previous readings
*[Kalman filter]: A calculation that estimates a stable value from noisy sensor readings
*[array]: A numbered list of values of one type, such as the bytes of a picture
*[namespace]: A family name for a group of C++ names that keeps them apart from other code
*[pointer]: A value that holds the address of something else in memory
*[fixed-point]: Counting in fractions with whole numbers, for example 256 units per pixel
*[animation player]: Code that keeps track of time and says which frame of an animation to show
*[loop mode]: What an animation does after its last frame
*[XBM]: X BitMap; a one-bit image format with on/off pixels stored in bytes
*[milli-g]: One thousandth of the acceleration due to gravity; 1000 milli-g is one g
*[SPH]: Smoothed Particle Hydrodynamics; a way to simulate fluids with interacting particles
*[NTP]: Network Time Protocol; a way to set a clock from a network time server
*[buffer]: An area of memory holding data while code works on it; the drawing buffer holds the next screen image
*[framebuffer]: A buffer that stores the pixel values for a screen image
*[float]: A C++ number type that can hold a fractional part
*[singleton]: An object shared through one instance
*[macro]: Named code expanded by the C++ preprocessor before compilation
*[lambda]: A short unnamed C++ function
*[ring buffer]: A queue that reuses a fixed amount of memory
*[potentiometer]: A variable resistor; moving the slider changes the voltage read by the device
*[GRBW]: Green, Red, Blue, White; the order used to send channels to the LED hardware
*[mg]: Milli-g in motion readings; one thousandth of the acceleration due to gravity
*[loadout]: The collection of apps and menu choices for your Fidget
*[PROGMEM]: Program memory; marks constant data for storage with the program on embedded boards

*[&]: In a parameter type, a reference to an existing object rather than a copy; before a value, its address.
*[*]: In a declaration, marks a pointer that holds an address; before a pointer, reads the object at that address.
*[bool]: A C++ type holding either true or false.
*[const]: Marks a value that cannot be changed through this declaration; after a method signature, the method does not change its object.
*[const char*]: A pointer to text ending with a zero character; the characters cannot be changed through this pointer.
*[int]: A signed whole number; on the device, -2,147,483,648 to 2,147,483,647.
*[int16_t]: A signed whole number from -32,768 to 32,767.
*[int32_t]: A signed whole number from -2,147,483,648 to 2,147,483,647.
*[long]: A signed whole number; on the device, -2,147,483,648 to 2,147,483,647.
*[nullptr]: A C++ value meaning a pointer does not point to an object.
*[String]: A C++ object holding text.
*[uint8_t]: A whole number from 0 to 255.
*[uint16_t]: A whole number from 0 to 65,535.
*[uint32_t]: A whole number from 0 to 4,294,967,295.
*[unsigned long]: A non-negative whole number; on the device, 0 to 4,294,967,295, used for elapsed time.
*[void]: A return type meaning that a function returns no value.
