# Bluetooth A2DP Guide

Hard-won lessons from debugging BT Classic A2DP source mode on the ESP32 with the [ESP32-A2DP](https://github.com/pschatzmann/ESP32-A2DP) and [arduino-audio-tools](https://github.com/pschatzmann/arduino-audio-tools) libraries. This guide exists to save future developers from the same multi-day debugging sessions.

---

## What is this?

A2DP (Advanced Audio Distribution Profile) is the Bluetooth protocol for streaming stereo audio. The ESP32 acts as a **source** (like a phone) and sends audio to a **sink** (speaker/headphones). The `A2DPStream` class from arduino-audio-tools wraps the ESP32-A2DP library, which wraps the ESP-IDF Bluetooth APIs.

This stack works — but has sharp edges around lifecycle management that aren't documented anywhere else.

---

## The golden rule: never destroy the pipeline

The A2DPStream, AudioPlayer, AudioSourceIdxSD, and MP3 decoder must all be **heap-allocated once and kept alive** for the entire app session. Never delete and recreate them.

Why:

- `BluetoothA2DPSource` has an internal FreeRTOS task (`BtAppT`) that loops forever and is never shut down
- A heartbeat timer (`osi_alarm`) fires every ~10 seconds and is never cancelled
- The global `self_BluetoothA2DPSource` pointer is never cleared by the destructor
- AudioPlayer and AudioSourceIdxSD have intertwined ring buffers and decoder contexts

!!! warning "Create once, reuse forever"
    ```cpp
    // In createAudioPipeline() — only runs once per app lifetime
    if (pA2dpStream == nullptr) {
        pA2dpStream = new A2DPStream();
        // ... configure and begin ...
    }
    // Pipeline already exists? Return immediately.
    ```

---

## Disconnect flow

Disconnecting from a BT speaker requires careful orchestration because of how the A2DP buffer interacts with the BT controller task.

### The problem: BufferRTOS blocks the BTC task

The A2DP buffer (`BufferRTOS<uint8_t>`) uses `portMAX_DELAY` for both reads and writes. When the player is stopped and the buffer is empty:

1. The BT data callback calls `xStreamBufferReceive()` → blocks forever (nothing to read)
2. This callback runs on the **BTC task** (Bluetooth Controller task)
3. `esp_a2d_source_disconnect()` dispatches through the **same BTC task queue**
4. Disconnect request sits in the queue forever → **hangs**

### The fix: unblock the buffer before disconnecting

```cpp
void MusicPlayerApp::disconnectBT() {
    // 1. Tell library not to auto-reconnect
    pA2dpStream->source().set_auto_reconnect(false);

    // 2. Reduce read timeout so callback returns quickly on empty buffer
    auto* buf = pA2dpStream->getBuffer();
    if (buf) buf->setReadMaxWait(pdMS_TO_TICKS(50));

    // 3. Write silence to wake any currently-pending read
    uint8_t silence[512] = {0};
    pA2dpStream->write(silence, sizeof(silence));
    delay(100);  // Let BTC task process with new short timeout

    // 4. NOW the disconnect can go through
    esp_a2d_source_disconnect(connectedAddress);
}
```

!!! danger "Never use `clear()` on the A2DP buffer"
    `A2DPStream::clear()` sets `is_a2dp_active = false`, which stops the data callback from draining the buffer. On the next reconnect, writes fill the buffer to 100% and block forever.

### Restoring for reconnect

When reconnecting, restore the blocking timeout so the data callback waits for data instead of returning silence:

```cpp
auto* buf = pA2dpStream->getBuffer();
if (buf) buf->setReadMaxWait(portMAX_DELAY);
```

---

## Stop playback safely

`AudioPlayer::stop()` calls `setActive(false)` which triggers an auto-fade that writes 2KB+ of silence to the A2DP stream. After multiple BT disconnect/reconnect cycles, these writes can hang.

```cpp
// Safe stop sequence
pPlayer->setAutoFade(false);
pPlayer->stop();
pPlayer->setAutoFade(true);
```

---

## Heartbeat auto-reconnect

The ESP32-A2DP library has a heartbeat timer that fires every ~10 seconds. In the `UNCONNECTED` state, the handler unconditionally calls `esp_a2d_connect(peer_bd_addr)` — **ignoring the `reconnect_status` flag**.

This means `set_auto_reconnect(false)` doesn't actually prevent reconnection.

### Library patch required

In `BluetoothA2DPSource.cpp`, the heartbeat handler needs a guard:

```cpp
// In bt_app_av_state_unconnected_hdlr():
if (reconnect_status != NoReconnect) {  // ← ADD THIS CHECK
    esp_a2d_connect(peer_bd_addr);
}
```

Without this patch, the device will reconnect to the old speaker ~10 seconds after you disconnect.

---

## Wrong disconnect API

`BluetoothA2DPCommon::disconnect()` calls `esp_a2d_sink_disconnect()` — this is the **sink** API. For source mode, you need:

```cpp
#include <esp_a2dp_api.h>
esp_a2d_source_disconnect(address);
```

---

## Two address variables

The library maintains two different address variables:

| Variable | Used by | Access |
|----------|---------|--------|
| `peer_bd_addr` | Heartbeat auto-reconnect | Protected, no public getter (needs patch) |
| `last_connection` | `reconnect()`, `set_auto_reconnect(addr)` | Internal |

### Library patch required

Add to `BluetoothA2DPCommon.h`:

```cpp
esp_bd_addr_t* get_current_peer_address() {
    return &peer_bd_addr;
}
```

This lets you read the actual address the heartbeat timer will try to connect to.

---

## Write timeout safety net

`A2DPStream::write()` has a polling loop that checks `availableForWrite()` every 5ms. The default `tx_write_timeout_ms = -1` means it polls forever — blocking when BT drops during playback.

```cpp
auto cfg = pA2dpStream->defaultConfig(TX_MODE);
cfg.tx_write_timeout_ms = 200;  // Give up after 200ms
```

This is a backstop. The primary protection is detecting `!isConnected()` in `update()` and stopping playback before writes block.

---

## BT disconnect detection during playback

Without active detection, a BT drop during playback causes `pPlayer->copy()` to block on A2DP writes:

```cpp
// In update(), before calling copy():
if (pA2dpStream && !pA2dpStream->isConnected()) {
    stopPlayback();
    btConnected = false;
    return;
}
```

Also detect heartbeat auto-reconnect recovery:

```cpp
if (pA2dpStream && pA2dpStream->isConnected() && !btConnected) {
    btConnected = true;  // Heartbeat reconnected us
}
```

---

## Device switching (A → B)

Direct disconnect-then-reconnect fails: the new connection drops after ~2-3 seconds. The BT stack needs time to clean up.

### Two-phase switch

1. **Phase 1**: Stop playback, disconnect, poll `isConnected()` until false (3s timeout)
2. **Phase 2**: 1 second settle time for stack cleanup
3. **Reconnect**: Restore `portMAX_DELAY`, call `reconnect()`, enter connecting state

---

## BT controller memory

`esp_bt_controller_mem_release()` is **permanent** — Bluetooth can never be restarted after this call.

`BluetoothA2DPCommon::end(true)` calls it internally.

!!! danger "Never call `end(true)` on A2DPStream"
    Use `end(false)` (the default) which only disconnects. Or better yet, don't call `end()` at all — keep the stream alive.

---

## Summary: what works

| Operation | Safe approach |
|-----------|--------------|
| **Create pipeline** | Heap-allocate once, reuse across sessions |
| **Stop playback** | Disable auto-fade, stop, re-enable auto-fade |
| **Disconnect** | Reduce buffer timeout, write silence, delay, then `esp_a2d_source_disconnect()` |
| **Reconnect** | Restore `portMAX_DELAY`, `set_auto_reconnect(addr)`, `reconnect()` |
| **Switch devices** | Two-phase: wait for disconnect + 1s settle, then reconnect |
| **Exit app** | Keep BT connected (don't disconnect on exit) |
| **Detect BT drop** | Check `isConnected()` before `copy()` in update loop |
