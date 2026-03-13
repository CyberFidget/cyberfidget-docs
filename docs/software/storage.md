# Storage & SD

The Cyber Fidget has a microSD card slot for app storage, asset loading, and data logging.

!!! tip "Draft section"
   THIS SECTION IS STILL IN DRAFT

---

## Recommended card specs

| Spec | Recommendation |
|------|---------------|
| **Format** | FAT32 (required) |
| **Size** | 1 GB – 32 GB (FAT32 max). Larger cards may need manual formatting to FAT32. |
| **Speed** | Class 4 or higher. Class 10 / UHS-I recommended for faster read/write. |
| **Form factor** | microSD (not full-size SD) |

!!! tip "Tested brands"
    Phison-based cards in the 4–32 GB range work well. Avoid ultra-cheap no-name cards — they can have compatibility issues with SPI-mode access.

---

## Formatting

Format your card as **FAT32** before first use:

- **Windows:** Right-click the drive → Format → FAT32. For cards > 32 GB, use a tool like [Rufus](https://rufus.ie/) or [SD Card Formatter](https://www.sdcard.org/downloads/formatter/).
- **macOS:** Disk Utility → Erase → MS-DOS (FAT).
- **Linux:** `mkfs.vfat /dev/sdX1`

---

## Use cases

- **App storage** — Some apps load assets (images, animation frames, sound data) from the SD card
- **Data logging** — Apps can write sensor data, scores, or logs to files
- **File browsing** — The WiFi web portal can serve files from the SD card for easy transfer
- **Settings** — User preferences and configuration can be persisted across power cycles

---

## Hardware details

The SD card connects to the ESP32 via SPI:

| Pin | Signal |
|-----|--------|
| GPIO 5 | SCK (clock) |
| GPIO 19 | MOSI (data out) |
| GPIO 21 | MISO (data in) |

The SD card shares the 3.3V_RGB power rail (GPIO 2 enable), so it is powered down when the AUX regulator is disabled in deep sleep.

---

## See also

- [Hardware Specs](../hardware/specs.md) — Full component list
- [Pinout](../hardware/pinout.md) — GPIO assignments for SD SPI bus
- [Apps](apps.md) — Which apps use SD card storage
