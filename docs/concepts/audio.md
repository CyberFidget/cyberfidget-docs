# Sound & Music

After this page you can play a melody and make a light react to sound.

The Cyber Fidget has a MAX98357A I2S amplifier with speaker for output and an ICS-43434 MEMS microphone for input. Your apps can play tones and react to sound levels. The device controls output volume; `setVolume()` has no effect in studio apps, on the device or in the browser emulator. The microphone isn't just for measuring loudness either - the device can  **capture real audio** and save it to the memory card, which is exactly what the built-in [Voice Notes](../firmware/voice-recorder.md) recorder does.

---

## What is this?

The device includes:

- **Speaker** - Plays tones and sounds. Your app sets a frequency (pitch) and duration.
- **Microphone** -- Listens to ambient sound. You can read how loud it is and react to it, and the firmware can record it to a file.

Both are opt-in: enable the mic when your app needs it, and disable it when you're done to save power.

!!! note "Level metering vs. recording"
    The app-facing audio API on this page is about *reacting* to sound -- reading the live
    microphone level so your app can respond to it. *Recording* sound to the card is a step
    beyond that, and it lives inside the built-in [Voice Notes](../firmware/voice-recorder.md)
    app, which captures audio on its own. Studio apps can read levels but cannot record audio through this interface.

---

## Concepts

### Playing tones

Paste each block into the [studio starter](../getting-started/first-app.md) where its comments say. Each block works on its own. Keep the starter's bottom-left exit button and its `setColorsOff()` calls in `begin()` and `end()`.

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
- Tones are timed by the audio engine, independently of `update()`. A 100 ms tone lasts 100 ms, plus a fade-out of about 5 ms to reduce clicks. Studio apps use this engine on the device and in the browser emulator, so a tone's length does not depend on your drawing speed.
- Several notes at once (chords) work in your own apps too, with firmware 1.5.0 or newer: see [Notes: several sounds at once](#notes-several-sounds-at-once). With older firmware, plan on one sound at a time.

### Playing a sequence

To play a short melody or alert without writing your own timing code, describe it as an array of `ToneStep` entries and hand it to `playSequence()`:

| Field | Meaning |
|-------|---------|
| `freq` | Frequency in Hz; 0 is a rest (silence) |
| `durationMs` | Length of the tone or rest in milliseconds |
| `gapAfterMs` | Silence after that step, in milliseconds |

```cpp
// Paste inside begin(), below setColorsOff();
// Each step has frequency in Hz, duration in ms, then gap in ms.
static const AudioManager::ToneStep step[] = { {880, 100, 50} };
HAL::audioManager().playSequence(step, 1);

// Paste inside end(), above unregisterButtonCallbacks();
HAL::audioManager().stopSequence();
HAL::audioManager().stopTone();
```

```cpp
// Paste inside begin(), below setColorsOff();
static const AudioManager::ToneStep WIN_JINGLE[] = {
    { 1046.50f, 100, 50 },  // C6, then a 50 ms pause
    { 0,         80,  0 },  // Rest for 80 ms
    { 1318.51f, 200,  0 },  // E6
};
static const int WIN_JINGLE_LEN = sizeof(WIN_JINGLE) / sizeof(WIN_JINGLE[0]);
HAL::audioManager().playSequence(WIN_JINGLE, WIN_JINGLE_LEN);

// Paste inside end(), above unregisterButtonCallbacks();
HAL::audioManager().stopSequence();
HAL::audioManager().stopTone();
```

- `playSequence(const ToneStep* steps, int count)` starts playback and returns immediately; the sequence plays in the background while your `update()` keeps running.
- `stopSequence()` stops it early.
- `isSequencePlaying()` returns `true` while it is still playing in built-in firmware apps. In studio apps, on the device and in the browser emulator, it always returns `false`, so time your app's own logic instead of polling it. See [elapsed-time checks](update-loop.md#millis-based-timing-vs-delay).
- In a studio app, the host copies up to 64 steps when you call `playSequence()`; a longer list is cut to 64. The host is the firmware code that runs your app, on the device or in the browser emulator. The array does not need to remain alive during playback. The examples use `static const` for fixed melodies. Built-in firmware apps accept up to 128 steps.

### Volume

In built-in firmware apps, `setVolume()` accepts a float, a number with a fractional part, from `0.0` (silent) to `1.0` (full). In studio apps, `setVolume()` has no effect on the device or in the browser emulator. Use the emulator's volume and mute controls to adjust browser playback.

!!! tip "Checking browser sound problems"
    On a computer, press F12 and open the browser developer tools' Console tab to look for loading or playback errors. This is separate from the studio's **Console** panel. Studio apps cannot print messages with `Serial.println()`. See [emulator troubleshooting](../software/emulator.md#troubleshooting).

### Microphone input

The mic is **opt-in**. Call `enableMic(true)` in `begin()` and `enableMic(false)` in `end()`. While enabled:

- `getMicVolumeLinear()` -- Returns 0.0 to 1.0 (linear amplitude).
- `getMicVolumeDb()` -- Returns dBFS (decibels below full scale), typically negative (e.g. -60 to 0).

### Notes: several sounds at once

`playTone()` makes one sound at a time. A **note** is a tone that can sound together with other notes, which is called **polyphony** (many voices at once). Notes are how you play a chord, or let another note start while one is still ringing.

```cpp
// Paste at the top of the file, below the #include lines
static int noteHandle = -1;

// Paste inside begin(), below setColorsOff();
noteHandle = HAL::audioManager().playNote(1046.5f); // Hold C6 until stopped.

// Paste inside end(), above unregisterButtonCallbacks();
HAL::audioManager().stopNote(noteHandle);
HAL::audioManager().stopNotes();
HAL::audioManager().stopTone();
```

- `playNote()` starts a note and returns a **handle**, a number greater than 0 that identifies that note. It returns `-1` if the note could not start. A `durationMs` of `0` (the default) holds the note until you stop it.
- `stopNote(handle)` ends only that note. If the note was already replaced by a newer one, the call does nothing.
- `stopNotes()` ends every note at once.
- Up to **7 notes** sound at the same time, alongside one `playTone()`. When all seven are busy, another note takes the place of one that is already fading out, or, if none is, the one that started first.
- Every note plays about **3 dB** quieter than `playTone()` (a dB, or decibel, is a unit of loudness; 3 dB quieter is about half the power). That leaves room for several notes at once, so chords are less likely to distort.

Low notes below about 700 Hz are hard to hear on the speaker, so keep important notes higher than that (see [Sounds that work on the speaker](#sounds-that-work-on-the-speaker)).

This example plays a C major chord (C5, E5, G5) while you are holding the first button, and stops it when you let go:

```cpp
// Paste at the top of the file, below the #include lines
static int chord[3] = { -1, -1, -1 };
static void onFirstButton(const ButtonEvent& e) {
    if (e.eventType == ButtonEvent_Pressed) {
        chord[0] = HAL::audioManager().playNote(523.25f);  // C5
        chord[1] = HAL::audioManager().playNote(659.25f);  // E5
        chord[2] = HAL::audioManager().playNote(783.99f);  // G5
    }
    if (e.eventType == ButtonEvent_Released) {
        for (int i = 0; i < 3; ++i) {
            HAL::audioManager().stopNote(chord[i]);
            chord[i] = -1;
        }
    }
}

// Paste inside begin(), below setColorsOff();
buttonManager.registerCallback(button_TopLeftIndex, onFirstButton);

// Paste inside end(), above unregisterButtonCallbacks();
buttonManager.unregisterCallback(button_TopLeftIndex);
HAL::audioManager().stopNotes();
HAL::audioManager().stopTone();
```

!!! note "Notes need firmware 1.5.0 or later"
    Apps that use notes need Cyber Fidget firmware **1.5.0 or newer**. Apps are checked automatically against what the firmware on your device supports. On older firmware the device shows "App needs firmware 1.5.0 or newer"; press any button to return to the menu. Apps that only play tones with `playTone()` are not affected.

### Reading the microphone

The microphone can drive your app: a level bar, an LED that brightens with sound, a clap detector. Turn it on, read the level every frame, and turn it off when you are done:

```cpp
// Paste inside begin(), below setColorsOff();
HAL::audioManager().enableMic(true);

// Paste inside update(), just above display.display();
float level = HAL::audioManager().getMicVolumeLinear();
display.clear();
display.drawRect(10, 28, 108, 8);
display.fillRect(11, 29, (int)(level * 106), 6);

// Paste inside end(), above unregisterButtonCallbacks();
HAL::audioManager().enableMic(false);
```

`getMicVolumeLinear()` gives a loudness from 0.0 (silence) to 1.0 (the loudest the microphone can measure). `getMicVolumeDb()` gives the same level in **dBFS** (decibels relative to full scale): 0 is the loudest possible sound and quieter sounds are negative numbers, for example -60 for a quiet room.

- The emulator has no microphone, so in the emulator both functions read silence. Test microphone apps on a real Cyber Fidget.
- Just after the device wakes up, while it is checking for updates, the microphone may read silence for a few seconds. It then starts reporting normally.

If your app exits without turning the microphone off, the system turns it off for you (and stops any notes). Doing it yourself in `end()` is still good practice, because `end()` is where an app cleans up after itself.

!!! note "The microphone functions need firmware 1.5.0 or later"
    Apps that read the microphone need Cyber Fidget firmware **1.5.0 or newer**. On older firmware the device shows "App needs firmware 1.5.0 or newer"; press any button to return to the menu.

---

## Code example: melody and sound reaction

```cpp
// Paste at the top of the file, below the #include lines
static unsigned long lastNote = 0;
static int noteIndex = 0;

// Paste inside begin(), below setColorsOff();
lastNote = millis();
noteIndex = 0;
HAL::audioManager().enableMic(true);

// Paste inside update(), just above display.display();
static const float notes[] = { 1046.50f, 1318.51f, 1567.98f }; // C6, E6, G6
unsigned long frameTime = millis();
if (frameTime - lastNote >= 500) {
    HAL::audioManager().playTone(notes[noteIndex], 200);
    noteIndex = (noteIndex + 1) % 3;
    lastNote = frameTime;
}
float micLevel = HAL::audioManager().getMicVolumeLinear();
uint8_t brightness = (uint8_t)(micLevel * 255);
HAL::setRgbLed(pixel_Front_Top, brightness, 0, 0, 0);

// Paste inside end(), above unregisterButtonCallbacks();
HAL::audioManager().stopTone();
HAL::audioManager().enableMic(false);
```

!!! note "This example needs firmware 1.5.0 or later"
    It reads the microphone, so apps made from it need Cyber Fidget firmware **1.5.0 or newer**.

!!! note "Always disable the mic in end()"
    Call `enableMic(false)` in your app's `end()` to release the microphone.

---

## Framework details

??? info "Advanced: how the firmware handles audio"
    You do not need these details to build apps in the studio. They describe the firmware internals for readers writing an app by hand and building it into the firmware.

    ### AudioManager

    The firmware shares one `AudioManager` object, accessed via `HAL::audioManager()`. It handles:

    - **Tone and note output** - the audio engine (`AudioEngine`, 8 voices at 44.1 kHz) mixes tones, notes and sequences, applies the volume and the speaker EQ, then sends the samples over I2S to the MAX98357A amplifier. Tones and notes use a soft square wave (a square wave with its harshest harmonics removed; harmonics are the fainter, higher-pitched tones at whole-number multiples of a note's pitch that give a sound its character) so low notes stay audible on the small speaker.
    - **Mic input** -- The ICS-43434 microphone sends audio over I2S. `VolumeMeter` measures its level and shares a value from 0 to 1 with the app.

    The `AudioManager` mic path is metering-only: it publishes a level, not a stream of samples. The built-in Voice Notes recorder opens the same ICS-43434 microphone on its own I2S port and pulls the raw sample stream for capture, independent of `AudioManager`. Studio apps do not have access to that capture path.

    ### I2S

    Audio uses the ESP32's I2S peripherals:

    - **I2S0** -- Speaker (TX) on pins 27 (LRCLK), 26 (BCLK), 14 (DOUT)
    - **I2S1** -- Microphone (RX) on pins 25 (LRCLK), 32 (BCLK), 33 (DATA IN)

    The mic runs in a separate FreeRTOS task and publishes `micVolumeAtomic` roughly every 20 ms.

## Functions on this page

The note functions each need firmware 1.5.0 or newer.

--8<-- "includes/reference/audio.md"
