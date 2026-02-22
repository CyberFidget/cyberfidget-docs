# Sound & Music

The Cyber Fidget has a speaker for output and a microphone for input. You can play tones at any frequency, control volume, and react to sound levels in your apps.

---

## What is this?

The device includes:

- **Speaker** — Plays tones and sounds. You set a frequency (pitch) and volume.
- **Microphone** — Listens to ambient sound. You can read how loud it is and react to it.

Both are opt-in: enable the mic when your app needs it, and disable it when you're done to save power.

---

## Concepts

### Playing tones

You play a tone by specifying its **frequency** in Hertz (Hz). Higher Hz = higher pitch. Musical notes have standard frequencies:

| Note | Frequency (Hz) |
|------|----------------|
| C4   | 261.63         |
| D4   | 293.66         |
| E4   | 329.63         |
| F4   | 349.23         |
| G4   | 392.00         |
| A4   | 440.00         |
| B4   | 493.88         |
| C5   | 523.25         |

!!! tip "Octaves"
    Each octave doubles the frequency. C5 is twice C4. Use `freq * pow(2, octave)` to shift notes up or down.

### Volume

Volume is a float from `0.0` (silent) to `1.0` (full). The framework clamps values in this range.

### Microphone input

The mic is **opt-in**. Call `enableMic(true)` in `begin()` and `enableMic(false)` in `end()`. While enabled:

- `getMicVolumeLinear()` — Returns 0.0 to 1.0 (linear amplitude).
- `getMicVolumeDb()` — Returns dBFS (decibels below full scale), typically negative (e.g. -60 to 0).

---

## Code example: melody and sound reaction

```cpp
#include "HAL.h"

void begin() {
    HAL::audioManager().enableMic(true);  // Turn on mic for reactive mode
    HAL::audioManager().setVolume(0.7f); // 70% volume
}

void update() {
    // Play a short melody (C4, E4, G4)
    static unsigned long lastNote = 0;
    static int noteIndex = 0;
    float notes[] = { 261.63f, 329.63f, 392.00f };
    if (millis() - lastNote > 500) {
        HAL::audioManager().playTone(notes[noteIndex], 200);
        noteIndex = (noteIndex + 1) % 3;
        lastNote = millis();
    }

    // React to mic: dim LEDs when quiet, bright when loud
    float micLin = HAL::audioManager().getMicVolumeLinear();
    uint8_t brightness = (uint8_t)(micLin * 255);
    HAL::setRgbLed(pixel_Front_Top, brightness, 0, 0, 0);
    updateStrip();
}

void end() {
    HAL::audioManager().stopTone();
    HAL::audioManager().enableMic(false);
}
```

!!! note "Always disable the mic in end()"
    Call `enableMic(false)` in your app's `end()` to stop the mic task and free resources.

---

## Framework details

### AudioManager

The `AudioManager` singleton (accessed via `HAL::audioManager()`) handles:

- **Tone output** — `SineWaveGenerator` → `VolumeStream` → I2S → MAX98357A amplifier
- **Mic input** — ICS-43434 I2S mic → `VolumeMeter` → atomic level (0..1)

### I2S

Audio uses the ESP32's I2S peripherals:

- **I2S0** — Speaker (TX) on pins 27 (LRCLK), 26 (BCLK), 14 (DOUT)
- **I2S1** — Microphone (RX) on pins 25 (LRCLK), 32 (BCLK), 33 (DATA IN)

The mic runs in a separate FreeRTOS task and publishes `micVolumeAtomic` roughly every 20 ms.

### API summary

| Method | Description |
|--------|-------------|
| `setVolume(float)` | 0.0..1.0 |
| `playTone(float freq, int durationMs)` | 0 = indefinite |
| `stopTone()` | Stops current tone |
| `enableMic(bool on)` | Opt-in mic |
| `getMicVolumeLinear()` | 0.0..1.0 |
| `getMicVolumeDb()` | dBFS (≤ 0) |
