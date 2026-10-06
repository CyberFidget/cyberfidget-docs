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

### Volume

Volume is a float from `0.0` (silent) to `1.0` (full). The framework clamps values in this range.

### Microphone input

The mic is **opt-in**. Call `enableMic(true)` in `begin()` and `enableMic(false)` in `end()`. While enabled:

- `getMicVolumeLinear()` — Returns 0.0 to 1.0 (linear amplitude).
- `getMicVolumeDb()` — Returns dBFS (decibels below full scale), typically negative (e.g. -60 to 0).

### Notes: several sounds at once

`playTone()` makes one sound at a time. A **note** is a tone that can sound together with other notes, which is called **polyphony** (many voices at once). Notes are how you play a chord, or let a new note start while an older one is still ringing.

```cpp
int playNote(float frequency, int durationMs = 0);
void stopNote(int handle);
void stopNotes();
```

- `playNote()` starts a note and returns a **handle**, a number greater than 0 that identifies that note. It returns `-1` if the note could not start. A `durationMs` of `0` (the default) holds the note until you stop it.
- `stopNote(handle)` ends only that note. If the note was already replaced by a newer one, the call does nothing.
- `stopNotes()` ends every note at once.
- Up to **7 notes** sound at the same time, alongside one `playTone()`. When all seven are busy, a new note takes the place of a note that is already fading out, or, if none is, the oldest note.
- Every note plays about **3 dB** quieter than `playTone()` (a dB, or decibel, is a unit of loudness; 3 dB quieter is about half the power). That leaves room for several notes at once, so chords are less likely to distort.

Low notes below about 700 Hz are hard to hear on the speaker, so keep important notes higher than that.

This app plays a C major chord (C5, E5, G5) while you are holding the first button, and stops it when you let go:

```cpp
#include "HAL.h"
#include "RGBController.h"

static int chord[3] = { -1, -1, -1 };

static void startChord() {
    chord[0] = HAL::audioManager().playNote(523.25f);  // C5, held
    chord[1] = HAL::audioManager().playNote(659.25f);  // E5
    chord[2] = HAL::audioManager().playNote(783.99f);  // G5
}

static void stopChord() {
    for (int i = 0; i < 3; i++) {
        HAL::audioManager().stopNote(chord[i]);
        chord[i] = -1;
    }
}

static void onFirstButton(const ButtonEvent& e) {
    if (e.eventType == ButtonEvent_Pressed)  startChord();
    if (e.eventType == ButtonEvent_Released) stopChord();
}

void begin() {
    setColorsOff();
    HAL::buttonManager().registerCallback(button_TopLeftIndex, onFirstButton);
}

void update() {
}

void end() {
    HAL::buttonManager().unregisterCallback(button_TopLeftIndex);
    HAL::audioManager().stopNotes();
    setColorsOff();
}
```

!!! note "Notes need a newer firmware"
    <!-- TODO: fill in the release that ships notes and mic -->
    Apps that use notes need Cyber Fidget firmware **NEXT_RELEASE or newer**. Apps are checked automatically against what the firmware on your device supports. On older firmware the device shows "App needs firmware NEXT_RELEASE or newer"; press any button to return to the menu. Apps that only play tones with `playTone()` are not affected.

### Reading the microphone

The microphone can drive your app: a level bar, an LED that brightens with sound, a clap detector. Turn it on, read the level every frame, and turn it off when you are done:

```cpp
#include "HAL.h"
#include "RGBController.h"

void begin() {
    setColorsOff();
    HAL::audioManager().enableMic(true);
}

void update() {
    float level = HAL::audioManager().getMicVolumeLinear();  // 0.0 to 1.0

    DisplayProxy& display = HAL::displayProxy();
    display.clear();
    display.drawRect(0, 28, 128, 8);                         // bar outline
    display.fillRect(0, 28, (int)(level * 128), 8);          // bar fill
    display.display();
}

void end() {
    HAL::audioManager().enableMic(false);
    setColorsOff();
}
```

`getMicVolumeLinear()` gives a loudness from 0.0 (silence) to 1.0 (the loudest the microphone can measure). `getMicVolumeDb()` gives the same level in **dBFS** (decibels relative to full scale): 0 is the loudest possible sound and quieter sounds are negative numbers, for example -60 for a quiet room.

- The emulator has no microphone, so in the emulator both functions read silence. Test microphone apps on a real Cyber Fidget.
- Just after the device wakes up, while it is checking for updates, the microphone may read silence for a few seconds. It then starts reporting normally.

If your app exits without turning the microphone off, the system turns it off for you (and stops any notes). Doing it yourself in `end()` is still good practice, because `end()` is where an app cleans up after itself.

!!! note "The microphone functions need a newer firmware"
    <!-- TODO: fill in the release that ships notes and mic -->
    Apps that read the microphone need Cyber Fidget firmware **NEXT_RELEASE or newer**. On older firmware the device shows "App needs firmware NEXT_RELEASE or newer"; press any button to return to the menu.

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
| `enableMic(bool on)` | Opt-in mic |
| `getMicVolumeLinear()` | 0.0..1.0 |
| `getMicVolumeDb()` | dBFS (≤ 0) |

Functions for notes (each needs firmware NEXT_RELEASE or newer):

| Method | Description |
|--------|-------------|
| `playNote(float freq, int durationMs)` | Starts a note and returns its handle (or -1); 0 = held until stopped |
| `stopNote(int handle)` | Ends that note only |
| `stopNotes()` | Ends all notes |
