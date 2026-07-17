<!--
Recovered verbatim from the retired product page (2026-07-12 state).
Rows still await a hardware-truth re-verification pass by the maintainer,
EXCEPT Development (verified 2026-07-17: MicroPython flashed and tested;
CircuitPython unverified - the retired page's claim was corrected).
Placement under reference/ is provisional pending the docs IA work.
-->

# Hardware specifications

This page preserves the detailed component specifications formerly published
on the product page. It is a part-level reference for the Cyber Fidget
hardware.

!!! note "Specifications may evolve"
    These specifications may evolve as production refines.

| Component | Details |
|---|---|
| Microcontroller | ESP32-PICO-MINI-02 dual-core MCU with integrated Wi-Fi (2.4 GHz 802.11 b/g/n) and Bluetooth Classic + BLE |
| Display | 0.96-inch 128 x 64 monochrome OLED (SSD1306 family) |
| Audio | MAX98357A digital I2S amplifier with on-board speaker, plus ICS-43434 MEMS microphone |
| Motion | LIS2DH12 3-axis accelerometer |
| Lighting | Four SK6812 RGBW LEDs with per-pixel control - three on front, one on back - plus one red light |
| Power | Rechargeable 400mAh Li-ion polymer battery with MAX17048 fuel gauge, MCP73831 charge IC, and swappable pack connector. Typical use: hours of active time, weeks of standby/deep sleep |
| Voltage regulation | Triple AP2112K-3.3 regulators for main logic, OLED, and LEDs for complete control of power consumption |
| Storage | microSD slot for app storage and file browsing |
| Connection | USB-C port providing RS-232 serial connection and charging |
| Inputs | 6 tactile buttons and 1 analog slider, included tuned debouncer in firmware |
| Size | 2.2 in x 1.6 in x 0.8 in (about 55.3 mm x 41.3 mm x 19.6 mm) |
| Weight | About 68 g, depending on backplate design |
| Assembly | High-quality kit - no soldering, just screws. Designed for repairability and customization |
| Accessories | Interchangeable color gels (clear, red, teal, and more) and multiple machined backplate designs available |
| Enclosure | Precision-machined aluminum chassis with replaceable backplate. Models available for 3D printing |
| Development | Arduino (ESP32) and MicroPython supported; CircuitPython may be compatible but is untested. Best experience with VS Code + PlatformIO |

## Reading this table

A *fuel gauge* is a battery-monitoring circuit that estimates the
battery's remaining charge. Other technical terms and part names used
above are explained in the [glossary](glossary.md), and most show a
definition when you hover over them.
