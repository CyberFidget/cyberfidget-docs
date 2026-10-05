# Sound & Music

The Cyber Fidget has a MAX98357A I2S amplifier with speaker for output and an ICS-43434 MEMS microphone for input. You can play tones at any frequency, control volume, and react to sound levels in your apps. The microphone isn't just for measuring loudness either - the device can  **capture real audio** and save it to the memory card, which is exactly what the built-in [Voice Notes](../firmware/voice-recorder.md) recorder does.

---

## What is this?

The device includes:

- **Speaker** — Plays tones and sounds. You set a frequency (pitch) and volume.
- **Microphone** — Listens to ambient sound. You can read how loud it is and react to it, and the firmware can record it to a file.

Both are opt-in: enable the mic when your app needs it, and disable it when you're done to save power.

!!! note "Level metering vs. recording"
    The app-facing audio API on this page is about *reacting* to sound — reading the live
    microphone level so your app can respond to it. *Recording* sound to the card is a step
    beyond that, and today it lives inside the built-in [Voice Notes](../firmware/voice-recorder.md)
    app, which captures audio on its own. A reusable capture API for your own apps is planned;
    for now, level metering is what's exposed below.

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

### Sounds that work on the speaker

The built-in speaker is tiny (13 mm across), and a speaker that small cannot push much air at low pitches. In practice it barely reproduces notes below about 700-800 Hz. Its sweet spot is roughly **1-4 kHz** (1000-4000 Hz).

- Keep important beeps and alerts between **C5 and C7** (523-2093 Hz), or anywhere in the 1-4 kHz range, so they are easy to hear.
- Low notes such as C4 (262 Hz) still work, because the Fidget's tones include **harmonics** (quieter copies of the note at 3x, 5x and 7x its frequency) that the speaker can reproduce. They just sound noticeably quieter, so avoid low notes for anything the user must notice.
- Tones are timed exactly: a 100 ms tone lasts 100 ms, plus a fade-out of about 5 ms at the end that prevents a click.
- Several notes at once (chords) are possible in the built-in apps. This is not yet available to your own apps, so plan on one sound at a time.

### Playing a sequence

To play a short melody or alert without writing your own timing code, describe it as an array of `ToneStep` entries and hand it to `playSequence()`:

```cpp
struct ToneStep {
    float    freq;        // Hz; 0 = rest (silence)
    uint16_t durationMs;  // how long the tone lasts
    uint16_t gapAfterMs;  // extra silence after the step
};
```

```cpp
static const AudioManager::ToneStep WIN_JINGLE[] = {
    { 1046.50f, 100, 50 },  // C6, then a 50 ms pause
    { 0,         80,  0 },  // rest for 80 ms
    { 1318.51f, 200,  0 },  // E6
};
static const int WIN_JINGLE_LEN = sizeof(WIN_JINGLE) / sizeof(WIN_JINGLE[0]);

HAL::audioManager().playSequence(WIN_JINGLE, WIN_JINGLE_LEN);
```

- `playSequence(const ToneStep* steps, int count)` starts playback and returns immediately; the sequence plays in the background while your `update()` keeps running.
- `stopSequence()` stops it early.
- `isSequencePlaying()` returns `true` while it is still playing in built-in firmware apps. In apps you build with the App Builder and install on the device, it currently always returns `false`, so time your app's own logic instead of polling it.
- The steps are copied when you call `playSequence()`, up to 128 steps; a longer list is cut to 128.

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

The `AudioManager` mic path is metering-only: it publishes a level, not a stream of samples. The Voice Notes recorder opens the same ICS-43434 microphone on its own I2S port and pulls the raw sample stream for capture, independent of `AudioManager`. Factoring that capture path into a shared, app-callable component is future work.

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
| `playSequence(const ToneStep* steps, int count)` | Plays a list of tones and rests (up to 128 steps) |
| `stopSequence()` | Stops the sequence |
| `isSequencePlaying()` | `true` while a sequence is playing (built-in apps; always `false` in installed App Builder apps for now) |
| `enableMic(bool on)` | Opt-in mic |
| `getMicVolumeLinear()` | 0.0..1.0 |
| `getMicVolumeDb()` | dBFS (≤ 0) |
