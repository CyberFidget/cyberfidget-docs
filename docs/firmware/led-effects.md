# LED Effects & Visualizer

The Music Player drives the Cyber Fidget's 4 RGBW NeoPixel LEDs in sync with audio playback, plus OLED visualizers on the Now Playing screen — a rolling amplitude graph and a VFD-style frequency spectrum display.

---

## What is this?

When music plays, the LEDs react to the audio in real-time — quiet passages produce a gentle blue pulse, medium levels shift to cyan/green, and loud peaks flash red with a white burst. There's also a "Pulse" mode that breathes independently of audio, and "Off" for when you want dark. Individual LEDs can be toggled on/off from a dedicated submenu.

The OLED screen has three visualizer modes: a time-domain amplitude graph (rolling waveform), a frequency-domain spectrum analyzer (like classic 80s VFD equalizer displays), or just the normal playhead with elapsed/remaining time.

---

## LED hardware

| Property | Value |
|----------|-------|
| Chip | RGBW NeoPixel (SK6812 compatible) |
| Count | 4 pixels |
| GPIO | 0 (`PIN_NEOPIXEL` from board variant) |
| Color order | GRB + White (`NEO_GRBW + NEO_KHZ800`) |
| Library | Adafruit NeoPixel |

The pixels are indexed 0-3: **Back** (0), **Front Top** (1), **Front Middle** (2), **Front Bottom** (3). The front three pixels get full-intensity colors; the back pixel gets a dimmed version (÷3).

!!! note "Why Adafruit NeoPixel instead of neopixelWrite()?"
    The ESP32 Arduino built-in `neopixelWrite(pin, r, g, b)` only drives a **single RGB pixel** (24 bits, no white channel). It also uses the RMT peripheral internally, so it has the same IRAM impact. It cannot drive a multi-pixel RGBW strip. Adafruit NeoPixel provides multi-pixel buffers, RGBW support, and color utilities.

---

## Audio analysis: SpectrumAnalyzer

Audio analysis is performed by `SpectrumAnalyzer`, a custom `ModifyingStream` that sits in the audio pipeline:

```
SD Card → AudioPlayer → MP3DecoderHelix → SpectrumAnalyzer → A2DPStream → BT Speaker
                                               ↓ (analysis)
                                       volumeRatio() — peak amplitude 0.0–1.0
                                       bands()[16]   — frequency spectrum 0.0–1.0
```

`SpectrumAnalyzer` replaces the original `VolumeMeter` from arduino-audio-tools. It provides the same `volumeRatio()` API for LED reactive effects, plus 16-band FFT frequency analysis for the spectrum visualizer. Audio passes through unchanged — zero latency, zero quality impact.

```cpp
// In createAudioPipeline():
if (!pSpectrumAnalyzer) {
    pSpectrumAnalyzer = new SpectrumAnalyzer(*pA2dpStream);
    pSpectrumAnalyzer->begin(44100, 2, 16);
}
pPlayer = new AudioPlayer(*pSourceSD, *pSpectrumAnalyzer, decoder);
```

!!! warning "Pipeline object lifecycle"
    Like all audio pipeline objects, the SpectrumAnalyzer is heap-allocated once and never destroyed. It persists across app enter/exit cycles via a null-pointer guard (`if (!pSpectrumAnalyzer)`). Direct access to `pA2dpStream` for BT management (disconnect, buffer manipulation) is unaffected.

---

## LED effect modes

Three modes, configured from the **LEDs submenu** (main menu → LEDs):

### Off (default)

LEDs are dark. `setColorsOff()` is called to ensure all pixels are cleared. This is the default mode to avoid micro-stutters when the spectrum visualizer is active.

### Reactive

LEDs respond to the current audio amplitude with smoothed, perceptually-corrected color mapping:

1. **EMA smoothing**: Raw amplitude is smoothed with exponential moving average (α = 0.25) to prevent flickering
2. **Gamma correction**: Smoothed value is raised to power 0.6 for perceptual brightness linearity
3. **Color mapping** by amplitude band:

| Amplitude | Color | Behavior |
|-----------|-------|----------|
| < 0.15 | Dim blue | Gentle sine-wave breathing pulse |
| 0.15 – 0.5 | Cyan → Green | Intensity scales linearly with amplitude |
| ≥ 0.5 | Red + White flash | Both channels scale with amplitude |

!!! tip "Booper pattern"
    The EMA + gamma approach comes from the `Booper` app in the main firmware, which uses `audioManager.getMicVolumeLinear()` to drive reactive LEDs from the microphone. Same smoothing math, different input source.

### Pulse

A gentle breathing animation independent of audio. Uses a sine wave to modulate blue LED brightness. Runs at the same 30fps update rate as reactive mode.

---

## LED submenu & per-LED control

The main menu's "LEDs" item opens a dedicated submenu with 6 options:

```
LEDs
├── Mode: Off / Reactive / Pulse   (Enter cycles)
├── Back LED: On / Off             (Enter toggles)
├── Front Top: On / Off            (Enter toggles)
├── Front Mid: On / Off            (Enter toggles)
├── Front Bottom: On / Off         (Enter toggles)
└── Sync: 150ms                    (Enter cycles 0-300ms in 25ms steps)
```

### Per-LED enable mask

A `uint8_t ledEnableMask` bitmask controls which LEDs participate in effects:

| Bit | Pixel | Name |
|-----|-------|------|
| 0 | 0 | Back |
| 1 | 1 | Front Top |
| 2 | 2 | Front Middle |
| 3 | 3 | Front Bottom |

Default: `0x0F` (all enabled). When a LED is disabled, it stays dark regardless of the active effect mode. When mode is Off, all LEDs are dark regardless of mask.

Toggling a LED off immediately clears that pixel via `HAL::setRgbLed()`. The mask is persisted in NVS so your configuration survives reboots.

---

## RGBController

The `RGBController` module manages the NeoPixel strip with a dirty-flag + throttle pattern:

- **Dirty flag**: Any color change calls `markDirty()` but does NOT call `strip.show()`.
- **Throttled show**: `updateStrip()` is called every `loopHardware()` cycle. It only calls `strip.show()` when dirty AND ≥33ms since last show (~30fps cap).
- **Dedup cache**: `setDeterminedColorsAll()` stores the last RGBW values and skips if identical. Prevents redundant SPI transactions when the color hasn't changed.

This keeps LED updates efficient — `strip.show()` for 4 RGBW pixels takes ~120μs, and it only fires when something actually changed.

`markDirty()` is exported from RGBController so that per-pixel `HAL::setRgbLed()` calls (used by the per-LED mask system) can trigger `strip.show()` on the next `updateStrip()` cycle.

---

## OLED visualizer modes

Three modes, cycled with **Up/Down buttons** in the Now Playing screen:

### Off (VIZ_OFF)

Normal playhead: elapsed M:SS + progress bar + remaining -M:SS.

### Amplitude (VIZ_AMPLITUDE)

A 16-bar rolling amplitude graph showing the last ~1 second of audio:

```
┌────────────────────────────┐
│  ⚡ Now Playing        87 ▊│
│ The Artist Name            │
│ ♫ Track Title Here ←scroll │
│                            │
│ ▶ Playing          [S]     │
│ ▃▅▇█▅▃▁▃▅▇▆▄▂▁▃           │  ← Amplitude bars
└────────────────────────────┘
```

- **16 bars**, each 7px wide + 1px gap = 128px total
- **Height**: 0–14px, proportional to amplitude at sample time
- **Sample rate**: ~60ms intervals → last ~1 second of audio history
- **Rolling buffer**: Circular array `amplitudeHistory[16]`, oldest sample drawn leftmost

### Spectrum (VIZ_SPECTRUM)

A VFD-style frequency spectrum display with 16 logarithmically-spaced bands:

```
┌────────────────────────────┐
│  ⚡ Now Playing        87 ▊│
│ The Artist Name            │
│ ♫ Track Title Here ←scroll │
│                            │
│ ▶ Playing          [S]     │
│ █▇▅▃▅▇█▅▃▁▂▃▅▇▆▄          │  ← Frequency bars
└────────────────────────────┘
```

- **16 bars** spanning ~60 Hz to ~16 kHz, logarithmically spaced
- **Fast attack, slow decay**: Bars snap up instantly but fade down smoothly (like classic VFD EQ displays)
- **Per-band AGC**: Each frequency band normalizes to its own peak, so bass can't flatten the treble

!!! tip "Display priority"
    The volume overlay (slider-triggered) takes priority over both visualizers. When the slider is touched, the volume bar appears for 2 seconds, then the visualizer resumes.

---

## How the spectrum analyzer works

The SpectrumAnalyzer uses a **Fast Fourier Transform (FFT)** to decompose audio into its frequency components. Here's the plain-English version of what happens:

### 1. Collect audio samples

The `write()` method receives raw PCM audio data (16-bit samples at 44,100 Hz). It forwards the audio to the Bluetooth output immediately, then copies mono samples (left channel only) into a 512-sample buffer. This gives us ~11.6ms of audio per window.

### 2. Apply a Hann window

Raw audio chunks have sharp edges at the start and end of each window, which creates false frequency content (spectral leakage). The **Hann window** is a bell-shaped curve that smoothly fades the edges to zero:

```
Hann[i] = 0.5 × (1 - cos(2π × i / 511))
```

Each sample is multiplied by its corresponding Hann coefficient before the FFT.

### 3. Run the FFT

A **radix-2 Cooley-Tukey FFT** transforms the 512 time-domain samples into 256 frequency bins. Each bin represents a ~86 Hz range (44100 / 512). The FFT is a self-contained implementation (~25 lines of C) that runs in-place — no external library dependencies.

The FFT runs from the **main loop** via `processFFT()`, not inside the audio `write()` path. This is critical — running FFT inside `write()` would block the Bluetooth audio stream and cause audible stuttering.

### 4. Map bins to bands

The 256 frequency bins are grouped into 16 logarithmically-spaced bands:

| Band | Frequency Range | What you hear |
|------|----------------|---------------|
| 0 | ~60–90 Hz | Sub-bass (kick drum) |
| 1 | ~90–130 Hz | Bass |
| 2–3 | ~130–265 Hz | Low-mid |
| 4–6 | ~265–770 Hz | Midrange (vocals) |
| 7–9 | ~770–2.2 kHz | Upper-mid (guitar, snare) |
| 10–12 | ~2.2–6.4 kHz | Presence/brilliance |
| 13–15 | ~6.4–16 kHz | Air (hi-hat, cymbals) |

The formula for band edges: `edge[i] = 60 × (16000/60)^(i/16)`

Logarithmic spacing is used because human hearing is logarithmic — the difference between 100 Hz and 200 Hz sounds the same as 1000 Hz and 2000 Hz. Equal-width bins would cram all the bass into one bar and waste 200+ bars on inaudible ultrasonic frequencies.

### 5. Per-band AGC (Automatic Gain Control)

Each band tracks its own maximum magnitude independently. The displayed value is `bandPeak / bandMax`, where `bandMax` slowly decays over time (~3 seconds to halve). This means:

- **Bass** normalizes to bass levels — a loud kick drum drives band 0 to 1.0
- **Treble** normalizes to treble levels — a hi-hat drives band 15 to 1.0
- Neither can flatten the other

Without per-band AGC, a heavy bass line would dominate the normalization and make all the treble bars appear flat — a common problem in naive spectrum analyzers.

### 6. Frame skipping

At 44,100 Hz with 512-sample windows, the raw FFT rate would be ~86 Hz — that's a lot of FFT computation per second. The `SKIP_FRAMES` constant (currently 1) tells the analyzer to process every other window, yielding ~43 Hz update rate. This balances visual smoothness against CPU overhead.

!!! warning "LED + FFT micro-stutter"
    When both music-reactive LEDs and the spectrum visualizer are active simultaneously, occasional micro-stutters may occur. This is because NeoPixel `strip.show()` uses the RMT peripheral (~120μs) which can compete with the audio write path. LEDs default to Off to avoid this. This is earmarked for future investigation (potential fix: reduce LED update rate when FFT is active, or move LEDs to a separate FreeRTOS task).

---

## BT latency compensation (Sync Delay)

### The problem

The SpectrumAnalyzer analyzes audio as it enters the A2DP transmit buffer. The BT speaker plays that audio ~200–500ms later (A2DP buffering + codec + link latency + speaker's own buffer). Without compensation, LEDs flash *before* the corresponding sound is heard.

### How it works

The SpectrumAnalyzer maintains a **delay ring buffer** — a circular array of 16 recent analysis frames, each timestamped with `millis()`. Instead of returning the current amplitude and spectrum data, the delayed accessors (`delayedVolumeRatio()`, `delayedBands()`) walk the ring buffer and return the frame closest to `millis() - delayMs`.

```
Audio pipeline timeline:
    t=0ms    Audio enters SpectrumAnalyzer → analysis stored in ring buffer
    t=150ms  delayedVolumeRatio() returns the t=0 analysis → LEDs react
    t=150ms  Speaker plays the t=0 audio → LEDs match what you hear
```

### Buffer details

| Property | Value |
|----------|-------|
| Buffer size | 16 frames |
| Frame contents | 16 band magnitudes + peak amplitude + timestamp |
| Memory cost | ~1.2 KB |
| Update rate | ~43 Hz (when spectrum enabled) or main loop rate |
| Max delay | ~350ms at 43 Hz update rate |

The ring buffer is populated from two paths:

- **`processFFT()`**: When the spectrum visualizer is active, each FFT result automatically stores a frame
- **`storeDelayFrame()`**: When spectrum is off (VIZ_AMPLITUDE or VIZ_OFF mode), the main loop explicitly stores amplitude-only frames to keep the delay buffer current for LED effects

### User-tunable delay

The **Sync** setting in the LED submenu adjusts the delay from 0–300ms in 25ms steps. The default is 150ms, which works well for most BT speakers. Speakers with larger internal buffers may need 200–300ms; wired or low-latency codecs may work best at 50–100ms.

!!! tip "Finding the right delay"
    Play a track with a strong beat (kick drum on every beat). Watch the LEDs flash red on the kick. If the flash comes before the sound, increase the delay. If after, decrease it. The sweet spot is when the flash and the thump feel simultaneous.

---

## NVS settings persistence

User preferences survive reboots via NVS namespace `"mpsettings"`:

| Key | Type | Default | Values |
|-----|------|---------|--------|
| `shuffle` | bool | false | Shuffle state |
| `ledmode` | uint8_t | 0 (Off) | 0=Off, 1=Reactive, 2=Pulse |
| `vizmode` | uint8_t | 0 (Off) | 0=Off, 1=Amplitude, 2=Spectrum |
| `ledmask` | uint8_t | 0x0F (all on) | Bitmask: bit0=Back, bit1=FrontTop, bit2=FrontMid, bit3=FrontBot |
| `leddelay` | uint16_t | 150 | BT latency compensation in ms (0–300) |

Settings are loaded in `begin()` after `loadPlaybackState()` and saved in `end()` before `savePlaybackState()`.

---

## Controls

| Button | Context | Action |
|--------|---------|--------|
| Up / Down | Now Playing | Cycle visualizer: Off → Amplitude → Spectrum |
| Enter | LED submenu: Mode | Cycle LED mode: Off → Reactive → Pulse |
| Enter | LED submenu: LED items | Toggle individual LED on/off |

---

## Resource impact

| Resource | Phase 4 | Phase 4.1 + 4.2 | Phase 4.3 | Notes |
|----------|---------|------------------|-----------|-------|
| Flash | 74.8% | 74.9% | 75.0% | +~1 KB for AVRCP TG + delay buffer |
| RAM | 22.7% | 22.7% | 22.7% | +~1.2 KB delay ring buffer (within margin) |
| IRAM | OK | OK | OK | ~2-4 KB (NeoPixel RMT driver) |
