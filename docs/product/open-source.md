# Open Source

Cyber Fidget is open source at its core. The firmware, documentation, and hardware designs are publicly available so you can study how it works, modify it, and contribute back.

---

## Repositories

| Repository | Description | License |
|---|---|---|
| [cyberfidget-firmware](https://github.com/cyberfidget/cyberfidget-firmware) | Firmware source, HAL API, and WASM emulator | GPL-3.0 with linking exception |
| [cyberfidget-docs](https://github.com/cyberfidget/cyberfidget-docs) | This documentation site | CC BY-SA 4.0 |

---

## Licenses

### Firmware & WASM Emulator — GPL-3.0 with linking exception

The firmware is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html) with a linking exception for user applications.

In plain terms: you can use, study, modify, and share the firmware. If you distribute a modified version of the firmware itself, you must share your changes under the same license.

### Your apps are yours

Cyber Fidget apps interact with the hardware through a **Hardware Abstraction Layer (HAL)** — a clean set of API headers for the display, buttons, audio, LEDs, and sensors. The GPL-3.0 linking exception is built around this boundary: any app that talks to the firmware solely through the HAL API is **not** considered a derivative work of the firmware.

That means apps you write are entirely yours. Use any license you want, keep them private, sell them — no restrictions. The HAL exists specifically to give you full ownership of the things you create.

!!! warning "Contributions to the base firmware"
    The linking exception applies to **your apps**, not to the firmware itself. If you contribute changes to the core firmware, HAL, or emulator infrastructure, those contributions fall under GPL-3.0 and must be shared under the same license.

### Documentation & Hardware Designs — CC BY-SA 4.0

This documentation site and hardware design files are licensed under [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/). You can share and adapt the content with credit, and any derivatives must use the same license.

### Hardware files

!!! info "Planned"
    The following hardware files are being prepared for public release under CC BY-SA 4.0:

    - Enclosure STL files
    - Block-level schematics (pin mapping)
    - Board layout reference (PDF)

    These aren't published yet — check back or watch the [firmware repo](https://github.com/cyberfidget/cyberfidget-firmware) for announcements.

Gerber files and full PCB design source are withheld. They are covered by a CERN OHL-S abandonment trigger — if the project is inactive for 24 months, the PCB source files are automatically released under the [CERN Open Hardware Licence v2 — Strongly Reciprocal](https://ohwr.org/cern_ohl_s_v2.txt).

---

## Trademark

"Cyber Fidget" is a trademark of Dismo Industries LLC. Use of the name in derivative projects should not imply official endorsement or affiliation.

---

## Contributing

We welcome contributions to the firmware, documentation, and community apps. See the [Contribute](../contribute/contribute.md) page for guidelines, or jump straight to a repo above.

---

## See also

- [Contribute](../contribute/contribute.md) — Contribution guidelines
- [First Flash](../getting-started/first-flash-arduino.md) — Flash firmware for the first time
- [Firmware Overview](../firmware/index.md) — Build system and project structure
- [Browser Emulator](../software/emulator.md) — Run apps in your browser
