# Firmware Development

This section covers the internals of the Cyber Fidget firmware — how to build it, how it's structured, and the design decisions behind the major subsystems.

---

## What is this?

The Cyber Fidget runs custom firmware on an ESP32 microcontroller. The firmware handles everything: buttons, display, LEDs, sound, Bluetooth, SD card, and the app framework that ties it all together. If you've read the [Concepts](../concepts/index.md) section, you know how apps work from the *outside*. This section shows how things work on the *inside*.

---

## Firmware

The firmware ships as a single unified build on `main` — all apps (games, screensavers, tools, music player, web portal) are included. The BT A2DP audio stack initially caused an IRAM overflow, but this was solved by [patching the linker script](IRAM-overflow-solution.md) to move unused libc functions out of IRAM. No apps needed to be removed.

---

## Build system

The firmware uses **PlatformIO** with the **pioarduino** platform (ESP-IDF 5.1.4 + Arduino ESP32 3.0.3).

```ini
platform = https://github.com/pioarduino/platform-espressif32/releases/...
board = adafruit_feather_esp32_v2
framework = arduino
```

Key build flags for the BT audio stack:

- `-DAUDIOTOOLS_NO_ANALOG` / `NO_PWM` / `NO_ADC` / `NO_DAC` — Strip unused audio backends
- `-DCONFIG_ESP32_WIFI_IRAM_OPT=0` — Move WiFi fast-path code out of IRAM
- `-DA2DP_SPP_SUPPORT=1` — Enable SPP alongside A2DP on IDF 5.x
- `build_type = release` — Debug builds add ~4KB of IRAM overhead

---

## Architecture overview

```
┌─────────────────────────────────────────────┐
│             AppManager (singleton)          │
│  Owns lifecycle: begin() → update() → end() │
├──────────┬──────────┬───────────────────────┤
│ MenuMgr  │ PowerMgr │ MusicPlayerApp  ...   │
├──────────┴──────────┴───────────────────────┤
│                   HAL                       │
│  Display · Buttons · Slider · LEDs · Audio  │
├─────────────────────────────────────────────┤
│          ESP-IDF / Arduino / FreeRTOS       │
├─────────────────────────────────────────────┤
│                ESP32 Hardware               │
│   OLED·Buttons·SK6812/NeoPixels·I2S·BT·SD   │
└─────────────────────────────────────────────┘
```

- **AppManager** schedules one active app at a time. Every 20ms, it calls the active app's `update()`.
- **HAL** wraps all hardware access behind a consistent API.
- **Apps** are self-contained classes registered via `APP_ENTRY` macros in `AppManifest.h`.

See [How an App Works](../concepts/app-lifecycle.md) for the app-level view.

---

## In this section

- [Music Player Architecture](music-player.md) — How the BT A2DP music player works
- [LED Effects & Visualizer](led-effects.md) — Music-reactive NeoPixels, per-LED control, OLED amplitude and spectrum visualizers
- [Bluetooth A2DP Guide](bt-a2dp-guide.md) — Hard-won lessons on ESP32-A2DP lifecycle management
- [Web Portal](web-portal.md) — WiFi captive portal for file management and settings
- [IRAM Optimization for Bluetooth](IRAM-overflow-solution.md) — How we fit BT A2DP into the ESP32's 128KB IRAM budget
