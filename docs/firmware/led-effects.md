# LED Effects & Visualizer

The Music Player drives the Cyber Fidget's 4 RGBW NeoPixel LEDs in sync with audio playback, plus an optional OLED amplitude visualizer on the Now Playing screen.

---

## What is this?

When music plays, the LEDs react to the audio in real-time — quiet passages produce a gentle blue pulse, medium levels shift to cyan/green, and loud peaks flash red with a white burst. There's also a "Pulse" mode that breathes independently of audio, and "Off" for when you want dark. An optional 16-bar amplitude graph replaces the playhead on the OLED, showing a rolling waveform of the last ~1 second of audio.

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

## Amplitude tap: VolumeMeter

Audio amplitude is measured by inserting a `VolumeMeter` into the audio pipeline. This is a built-in class from [arduino-audio-tools](https://github.com/pschatzmann/arduino-audio-tools) that wraps an output stream:

```
SD Card → AudioPlayer → MP3DecoderHelix → VolumeMeter → A2DPStream → BT Speaker
```

`VolumeMeter` is a `ModifyingStream` — its `write()` method calls `updateVolumes(data, len)` to compute peak amplitude, then passes the audio through unchanged to the wrapped stream. Zero latency, zero quality impact.

```cpp
// In createAudioPipeline():
if (!pVolumeMeter) {
    pVolumeMeter = new VolumeMeter(*pA2dpStream);
}
pPlayer = new AudioPlayer(*pSourceSD, *pVolumeMeter, decoder);
```

`pVolumeMeter->volumeRatio()` returns a float 0.0–1.0 representing the current peak amplitude.

!!! warning "Pipeline object lifecycle"
    Like all audio pipeline objects, the VolumeMeter is heap-allocated once and never destroyed. It persists across app enter/exit cycles via a null-pointer guard (`if (!pVolumeMeter)`). Direct access to `pA2dpStream` for BT management (disconnect, buffer manipulation) is unaffected.

---

## LED effect modes

Three modes, cycled from the main menu under **"LEDs: Off/Reactive/Pulse"**:

### Off

LEDs are dark. `setColorsOff()` is called to ensure all pixels are cleared.

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

```cpp
// Reactive color mapping (simplified)
float raw = pVolumeMeter->volumeRatio();
float smoothed = ledSmoothedAmplitude * 0.75f + raw * 0.25f;  // EMA
float amp = powf(smoothed, 0.6f);                              // gamma

if (amp < 0.15f) {
    // Blue breathing pulse
    float breath = (sinf(millis() / 400.0f) + 1.0f) * 0.5f;
    uint8_t blue = (uint8_t)(breath * amp * 80.0f);
    setDeterminedColorsAll(0, 0, blue, 0);
} else if (amp < 0.5f) {
    // Cyan-green gradient
    float t = (amp - 0.15f) / 0.35f;
    setDeterminedColorsAll(0, (uint8_t)(t * 30), (uint8_t)((1.0f - t) * 25), 0);
} else {
    // Red + white flash
    float t = (amp - 0.5f) / 0.5f;
    setDeterminedColorsAll((uint8_t)(t * 30), 0, 0, (uint8_t)(t * 20));
}
```

!!! tip "Booper pattern"
    The EMA + gamma approach comes from the `Booper` app in the main firmware, which uses `audioManager.getMicVolumeLinear()` to drive reactive LEDs from the microphone. Same smoothing math, different input source.

### Pulse

A gentle breathing animation independent of audio. Uses a sine wave to modulate white LED brightness. Runs at the same 30fps update rate as reactive mode.

---

## RGBController

The `RGBController` module manages the NeoPixel strip with a dirty-flag + throttle pattern:

- **Dirty flag**: Any color change calls `markDirty()` but does NOT call `strip.show()`.
- **Throttled show**: `updateStrip()` is called every `loopHardware()` cycle. It only calls `strip.show()` when dirty AND ≥33ms since last show (~30fps cap).
- **Dedup cache**: `setDeterminedColorsAll()` stores the last RGBW values and skips if identical. Prevents redundant SPI transactions when the color hasn't changed.

This keeps LED updates efficient — `strip.show()` for 4 RGBW pixels takes ~120μs, and it only fires when something actually changed.

---

## OLED visualizer

A 16-bar amplitude graph on the Now Playing screen, toggled with **Up/Down buttons** while in the player view.

```
┌────────────────────────────┐
│  ⚡ Now Playing        87 ▊│
│ The Artist Name            │
│ ♫ Track Title Here ←scroll │
│                            │
│ ▶ Playing          [S]     │
│ ▃▅▇█▅▃▁▃▅▇▆▄▂▁▃           │  ← Visualizer replaces playhead
└────────────────────────────┘
```

- **16 bars**, each 7px wide + 1px gap = 128px total
- **Height**: 0–14px, proportional to amplitude at sample time
- **Sample rate**: ~60ms intervals → last ~1 second of audio history
- **Rolling buffer**: Circular array `amplitudeHistory[16]`, oldest sample drawn leftmost

!!! tip "Display priority"
    The volume overlay (slider-triggered) takes priority over the visualizer. When the slider is touched, the volume bar appears for 2 seconds, then the visualizer resumes. When the visualizer is off, the normal playhead (elapsed/remaining time + progress bar) is shown.

---

## NVS settings persistence

User preferences survive reboots via NVS namespace `"mpsettings"`:

| Key | Type | Values |
|-----|------|--------|
| `shuffle` | bool | Shuffle state |
| `ledmode` | uint8_t | 0=Off, 1=Reactive, 2=Pulse |
| `viz` | bool | Visualizer on/off |

Settings are loaded in `begin()` after `loadPlaybackState()` and saved in `end()` before `savePlaybackState()`.

---

## Controls

| Button | Context | Action |
|--------|---------|--------|
| Up / Down | Now Playing | Toggle OLED visualizer |
| Enter (main menu) | "LEDs: ..." item | Cycle LED mode: Off → Reactive → Pulse |

---

## Resource impact

| Resource | Before Phase 4 | After Phase 4 | Added |
|----------|----------------|---------------|-------|
| Flash | 74.6% | 74.8% | ~5 KB |
| RAM | 22.7% | 22.7% | ~500 bytes |
| IRAM | OK | OK | ~2-4 KB (NeoPixel RMT driver) |
