# Storage & SD

Apps live in the Cyber Fidget's internal storage, the companion page is built into its firmware, and app art is compiled into each app when it is built. The microSD card holds music, voice recordings, the companion's speech-recognition payload, and any optional companion page override; it does not hold apps or supply their art.

!!! tip "Draft section"
   THIS SECTION IS STILL IN DRAFT

---

## Inserting and removing cards safely

!!! warning "Use the battery switch - software power-off is not enough"
    Slide the **battery switch OFF** before inserting or removing a
    microSD card. Powering the device off from the power app does not
    fully de-energize the card slot: on current firmware, some of the
    slot's signal lines can stay electrically active while the device
    appears off. A card inserted against active signal lines can be
    **permanently damaged** - current flows into the unpowered card
    through its protection diodes, which can corrupt the card's
    controller so badly that no computer will recognize it afterward.

    The battery switch cuts power to everything, so with it OFF a
    card swap is always safe.

In short:

- **Safe:** battery switch OFF, then insert or remove the card.
- **Not safe:** swapping cards while the device is on - including on a
  "No SD card" screen - or after powering off through the power app.
- Make sure the card is **fully seated** (it should sit flush in the
  slot). A partially inserted card can make contact on its signal pins
  without receiving power, which risks the same damage.

A firmware update that removes this hazard is in development; the
battery-switch habit remains good practice even after it ships.

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

- **Music** - The card holds music files
- **Voice recordings** - The card holds recordings made with Voice Notes
- **Phone companion** - The card holds its speech-recognition payload and may hold a newer page override; the device already has the companion page in its firmware
- **File browsing** - The WiFi web portal can list, upload, and download the card's files, which is the easiest way to move music and recordings on and off

---

## Hardware details

The SD card connects to the ESP32 via SPI:

| Pin | Signal |
|-----|--------|
| GPIO 5 | SCK (clock) |
| GPIO 19 | MOSI (data out) |
| GPIO 21 | MISO (data in) |
| GPIO 8 | CS (chip select) |

The SD card shares the 3.3V_RGB power rail (GPIO 2 enable), so it is powered down when the AUX regulator is disabled in deep sleep. The SPI bus lines, however, live on the always-on 3.3V domain, and on current firmware they can remain driven during deep sleep (the ESP32's GPIO deep-sleep hold latches digital pads at their pre-sleep state) - which is why swapping cards requires the battery switch, not just software power-off. See [Inserting and removing cards safely](#inserting-and-removing-cards-safely).

---

## See also

- [Hardware Specs](../hardware/specs.md) — Full component list
- [Pinout](../hardware/pinout.md) — GPIO assignments for SD SPI bus
- [Apps](apps.md) — Which apps use SD card storage
