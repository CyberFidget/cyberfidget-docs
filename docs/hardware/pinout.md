# Pinout Reference

!!! note "PCB rev 1.x"
    Pin assignments are verified against the Rev 1.2 schematic. GPIO18 and GPIO23 do not exist on the ESP32-PICO-MINI-02 variant used in Cyber Fidget.

---

## GPIO assignment table

| GPIO | Function | Type | Device / Notes |
|------|----------|------|----------------|
| 0 | Boot Mode + NeoPixel Data | I/O | Momentary boot button (back) + 4x SK6812 RGBW LEDs |
| 2 | AUX Power Enable | Output | AP2112K 3.3V_RGB rail (LEDs, slider, amp, mic, SD, provisional hall sensors) |
| 4 | ACCL_INT1 | Input | LIS2DH12 interrupt 1 (100k pullup) |
| 5 | SD Card SCK | Output | SPI clock for microSD (MCU_SCK) |
| 7 | OLED Reset | Output | SSD1306 display reset |
| 12 | OLED Power Enable | Output | AP2112K regulator for OLED 3.3V rail |
| 13 | Charge Enable / Red LED | Output | MCP73831 (requires solder bridge); dedicated charge status LED |
| 14 | I2S DOUT (speaker) | Output | MAX98357A DIN |
| 15 | Button 6 (SW_6) / Wake | Input | Bottom-Right; internal pullup (no ext 47k) + deep sleep ext0 wake |
| 19 | SD Card MOSI | Output | SPI data to microSD (MCU_MOSI) |
| 20 | I2C SCL | Output | Shared: OLED, LIS2DH12, MAX17048, MCP23017 x2 |
| 21 | SD Card MISO | Input | SPI data from microSD (MCU_MISO) |
| 22 | I2C SDA | Bidir | Shared: OLED, LIS2DH12, MAX17048, MCP23017 x2 |
| 25 | I2S LRCLK (mic) | Output | ICS-43434 MIC_WS |
| 26 | I2S BCLK (speaker) | Output | MAX98357A SPK_BCLK |
| 27 | I2S LRCLK (speaker) | Output | MAX98357A SPK_LRC |
| 32 | I2S BCLK (mic) | Output | ICS-43434 MIC_SCK |
| 33 | I2S DATA IN (mic) | Input | ICS-43434 MIC_SD |
| 34 | Button 5 (SW_5) | Input | Bottom-Left (input-only GPIO) |
| 35 | Slider ADC | Analog In | Linear slide potentiometer (HALL_LINEAR net, ADC1_CH7) |
| 36 | Button 1 (SW_1) | Input | Top-Left (input-only GPIO) |
| 37 | Button 2 (SW_2) | Input | Top-Right (input-only GPIO) |
| 38 | Button 3 (SW_3) | Input | Middle-Left (input-only GPIO) |
| 39 | Button 4 (SW_4) | Input | Middle-Right (input-only GPIO) |

!!! info "Button numbering"
    The schematic uses 1-indexed switch names (SW_1 through SW_6). The firmware uses 0-indexed button indices (0 through 5). Both refer to the same physical buttons:

    | Firmware index | Schematic | Position |
    |----------------|-----------|----------|
    | 0 | SW_1 | Top-Left |
    | 1 | SW_2 | Top-Right |
    | 2 | SW_3 | Middle-Left |
    | 3 | SW_4 | Middle-Right |
    | 4 | SW_5 | Bottom-Left |
    | 5 | SW_6 | Bottom-Right |

---

## I2C bus

All I2C devices share the same bus on GPIO 22 (SDA) and GPIO 20 (SCL):

| Device | Address | Notes |
|--------|---------|-------|
| OLED (SSD1306) | 0x3C | Display |
| Accelerometer (LIS2DH12) | 0x19 | Default (0x18 if solder bridge closed) |
| Fuel Gauge (MAX17048) | 0x36 | Battery state-of-charge |
| I/O Expander (MCP23017) x2 | — | On bus; may not be used in current firmware |

---

## I2S audio

Two I2S peripherals handle audio:

**Speaker output (I2S port 0, TX):**

| Pin | Signal | Notes |
|-----|--------|-------|
| GPIO 27 | LRCLK | Word select |
| GPIO 26 | BCLK | Bit clock |
| GPIO 14 | DOUT | Data to MAX98357A |

**Microphone input (I2S port 1, RX):**

| Pin | Signal | Notes |
|-----|--------|-------|
| GPIO 25 | LRCLK | Word select |
| GPIO 32 | BCLK | Bit clock |
| GPIO 33 | DATA IN | Data from ICS-43434 |

---

## SPI (SD card)

| Pin | Signal |
|-----|--------|
| GPIO 5 | SCK (clock) |
| GPIO 19 | MOSI (data out) |
| GPIO 21 | MISO (data in) |

---

## Button hardware debounce

Buttons SW_1 through SW_5 use hardware RC debounce:

- **R** = 10k, **C** = 10nF (time constant ~100 us)
- **Pull-up** = 47k to 3.3V

Button SW_6 (GPIO 15) uses the ESP32's internal pullup instead of an external 47k resistor. GPIO 15 also serves as the deep sleep wake pin (`esp_sleep_enable_ext0_wakeup`).

The firmware adds a 20 ms software debounce and a 1500 ms hold threshold on top of the hardware debounce.

---

## Serial

- **Baud rate:** 921600 (default)
- **USB bridge:** CP2102N USB-to-UART
- Default UART pins: GPIO 1 (TX), GPIO 3 (RX)

---

## See also

- [Hardware specs](specs.md) — Full component list and dimensions
- [Buttons & Events](../concepts/buttons.md) — How button presses become actions in code
- [Sound & Music](../concepts/audio.md) — I2S audio details
- [The Slider](../concepts/slider.md) — ADC reading and filtering
