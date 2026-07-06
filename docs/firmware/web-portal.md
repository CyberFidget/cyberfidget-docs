# Web Portal

The Web Portal turns the CyberFidget into a WiFi access point with a captive portal, giving you a browser-based interface to manage music files, create playlists, and preview tracks — all from your phone. It can also join your home WiFi network for easy access at `cyberfidget.local`.

---

## What is this?

Connect your phone to the "CyberFidget" WiFi network and a web portal opens automatically (captive portal). No app installs, no IP addresses to remember. From there you can:

1. **Upload** MP3 files via drag-and-drop
2. **Browse** your music library with real ID3 metadata (title, artist, album)
3. **Play** tracks through your phone's speaker (web audio)
4. **Manage** files — move, delete, create folders
5. **Build playlists** in M3U format that persist on the SD card
6. **Connect to WiFi** — join your home network for `cyberfidget.local` access

---

## How it works

```
Phone → Connects to "CyberFidget" WiFi AP
     → Captive portal auto-opens browser at 192.168.4.1
     → SPA loads (HTML/CSS/JS served from ESP32 flash)
     → API calls read/write files on the SD card
     → Audio served directly from SD over HTTP
```

Or, if connected to your home WiFi:

```
Phone → Same WiFi network as CyberFidget
     → Browse to http://cyberfidget.local
     → Same portal, no WiFi switching needed
```

The portal is a standalone app launched from the main menu under **Tools → CyberFidget Portal**. It stops Bluetooth (shared radio) and starts WiFi, so you can't play music through a BT speaker while the portal is running.

!!! warning "WiFi and Bluetooth share the ESP32 radio"
    The ESP32 can't run WiFi AP and BT A2DP simultaneously with enough bandwidth for audio streaming. The portal calls `btStop()` on entry and WiFi shuts down on exit. BT reconnects automatically when you return to the Music Player.

---

## Architecture

### App lifecycle

```
Menu → "CyberFidget Portal" → AppManager::switchToApp(APP_WEB_PORTAL)
  1. MusicPlayerApp::end()        — saves state, stops playback
  2. WebPortalApp::begin()        — btStop(), WiFi AP+STA, mDNS, DNSServer, AsyncWebServer
     ... user manages files via captive portal or cyberfidget.local ...
  3. WebPortalApp::end()          — server stop, mDNS stop, WiFi.mode(WIFI_OFF)
  4. Back to menu
```

### WiFi modes

The portal runs in **AP+STA dual mode** (`WIFI_AP_STA`):

- **Access Point** — "CyberFidget" network is always available. Any device can connect directly and access the portal at `192.168.4.1`.
- **Station** — If you've configured a WiFi network in Settings, the CyberFidget also joins your home WiFi. This makes the portal accessible at `cyberfidget.local` or the device's LAN IP from any device on your network.

WiFi credentials are stored in NVS (non-volatile storage) and auto-connect on every portal launch. Use the Settings page to scan, connect, or forget networks.

!!! tip "mDNS: cyberfidget.local"
    When connected to your WiFi, the device registers `cyberfidget.local` via mDNS. This works on iOS, macOS, Linux, and Android 10+. If mDNS doesn't resolve on your device, the IP address is always shown on the OLED and in the portal status bar.

### Captive portal

Uses `DNSServer` to redirect **all** DNS queries to `192.168.4.1`. When a phone connects to the AP, its OS sends connectivity-check requests which hit our web server, triggering the "Sign in to WiFi" popup.

The `onNotFound()` handler redirects unknown URLs to `/` — this catches captive portal detection from iOS, Android, Windows, and macOS.

!!! note "Android captive portal browser limitations"
    Android's "Sign in" mini-browser doesn't support file picker inputs. A banner detects this and prompts users to open `192.168.4.1` in their full browser (Chrome, etc.) where file upload works normally.

### OLED display

While the portal is running, the 128x64 OLED shows:

```
┌────────────────────────────────┐
│ ===== CyberFidget Web ======== │
│ AP: 192.168.4.1                │
│ HomeNet 192.168.1.42           │
│ cyberfidget.local              │
│ 42 files | 2 clients           │
└────────────────────────────────┘
```

If not connected to a WiFi network, lines 3-4 show "WiFi: not connected" and the file count instead.

During uploads, the bottom line shows a progress bar.

---

## SD card layout

Media files live under `/media/` with arbitrary nesting:

```
/media/
├── track.mp3                     ← flat files
├── Artist Name/
│   ├── track.mp3                 ← artist folders
│   └── Album Name/
│       └── track.mp3             ← artist/album nesting
├── playlists/
│   ├── Chill.m3u                 ← M3U playlist files
│   └── Workout.m3u
└── My Folder/
    └── track.mp3                 ← user-defined folders
```

The Music Player's `AudioSourceIdxSD` and `ID3Scanner` both scan `/media/` recursively — any `.mp3` file at any depth is discovered.

!!! tip "Organize however you want"
    The scanner doesn't care about folder structure. Flat files, nested by artist/album, or any combination — it all works. Folders are just for your own organization.

---

## API reference

All API routes are under the ESPAsyncWebServer running on port 80.

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Portal page (SPA from PROGMEM) |
| `/media/*` | GET | Static file serving from SD (for audio playback) |
| `/recordings/*` | GET | Static voice-note serving from SD (playback + download) |
| `/web/*` | GET | [Phone companion](companion.md) app from SD (`/web/` on the card); a built-in fallback page explains how to get the SD pack when it's missing |
| `/ws/live` | WS | Live caption link: mic audio out as binary PCM frames, JSON `time`/`caption` frames back; single client; contract pinned in `LiveLinkProtocol.h` |
| `/api/files` | GET | Recursive JSON folder tree (music view, MP3-filtered) |
| `/api/tracks` | GET | Flat JSON array with ID3 metadata per track |
| `/api/recordings` | GET | Voice notes merged with `index.csv` metadata |
| `/api/browse?path=/...` | GET | Single-level listing of any folder (name, type, size, modified date) for the Files browser |
| `/api/download?path=/...` | GET | Download any file off the card as an attachment |
| `/api/upload?dir=/...` | POST | Multipart file upload into any folder |
| `/api/delete?path=/...` | POST | Delete a file or a folder (folders delete recursively; voice notes also drop the `index.csv` row) |
| `/api/mkdir?path=/...` | POST | Create a directory anywhere on the card |
| `/api/move?from=...&to=...` | POST | Move/rename a file or folder (voice notes also update the `index.csv` row) |
| `/api/time?ms=<epoch>` | POST | Set the device clock from the browser's wall-clock |
| `/api/status` | GET | File count, SD space, connected clients, live-link health (`live.connected`, sent/dropped frame counts) |
| `/api/playlists` | GET | List all M3U playlists |
| `/api/playlist?name=...` | GET | Read playlist tracks |
| `/api/playlist?name=...` | POST | Save playlist (JSON body) |
| `/api/playlist/delete?name=...` | POST | Delete playlist |
| `/api/wifi/scan` | GET | Scan nearby WiFi networks |
| `/api/wifi/connect` | POST | Connect to WiFi (JSON: ssid, pass) |
| `/api/wifi/status` | GET | WiFi connection status, IP, mDNS |
| `/api/wifi/forget` | POST | Clear saved WiFi credentials |

### Example: `/api/tracks` response

```json
[
  {
    "path": "/media/Rock/song.mp3",
    "title": "Song Title",
    "artist": "Artist Name",
    "album": "Album Name",
    "size": 4521984
  }
]
```

ID3 tags are read on-the-fly from each MP3 file (ID3v2 first, ID3v1 fallback). Title falls back to filename if no tags are present.

### Example: `/api/recordings` response

```json
{
  "sd": true,
  "items": [
    {
      "name": "REC_0042.wav",
      "timestamp": "2026-06-09T14:23:11",
      "duration": 123,
      "bytes": 3936000
    }
  ]
}
```

The list is built from `/recordings/index.csv` (written by the Voice Notes app, parsed with the shared `RecNaming::parseIndexRow`) and filtered to rows whose `.wav` still exists on the card. `timestamp` is empty when the recording was made before the clock was set; `duration` is whole seconds; `bytes` is the audio data length. When no card is mounted the response is `{"sd": false}` so the UI can tell "no card" apart from "no notes yet".

### Example: `/api/browse` response

```json
{
  "sd": true,
  "path": "/media",
  "entries": [
    { "name": "Rock", "type": "dir", "size": 0, "mtime": 1717000000 },
    { "name": "intro.mp3", "type": "file", "size": 4096, "mtime": 1717000000 }
  ]
}
```

`/api/browse` lists the **direct children** of one folder (defaults to the card root, `/`), with no type filter, so the Files browser can show every file and folder. `type` is `"dir"` or `"file"`; `size` is bytes (`0` for folders); `mtime` is the file's modified time as a Unix timestamp. `mtime` is only meaningful once the device clock has been set -- files written before then come back as `0`, which the browser shows as "No date". As with `/api/recordings`, a missing card returns `{"sd": false}`.

### Example: `/api/playlist` save body

```json
{
  "tracks": [
    "/media/Rock/song.mp3",
    "/media/Pop/track.mp3"
  ]
}
```

---

## Web UI features

### Track table

The default view shows all tracks in a sortable, searchable table with columns for title, artist, album, and size. Data comes from `/api/tracks` with real ID3 metadata.

Each track has action buttons (visible on hover/tap):
- **Play** — streams audio through the phone's browser
- **+PL** — add to a playlist via dropdown
- **Del** — delete with confirmation

### Web audio player

Tracks are served directly from the SD card via `serveStatic("/media/", SD, "/media/")`. The browser's native `<audio>` element handles decoding — zero CPU cost on the ESP32.

The player bar shows:
- Now-playing title and artist
- Play/pause, previous, next controls
- Visual progress bar (interactive scrubbing planned for future)
- Elapsed and remaining time

Playing any track auto-builds a queue from all loaded tracks, so next/prev cycles through your library.

### Voice notes

The **Voice notes** tab lists every recording made by the [Voice Notes](voice-recorder.md) app, newest first, reading metadata straight from `/recordings/index.csv`. Each note shows its date, length, and size, with:

- **Play** — a native `<audio>` element streams the WAV straight from the SD card (`serveStatic("/recordings/", SD, "/recordings/")`), with scrubbing for free. WAV was chosen in part so every browser can play it with zero transcoding.
- **Download** — saves the original `.wav` to your phone or computer.
- **Rename** — renames the file and rewrites the matching `index.csv` row (and any transcript sidecar) in lockstep, so a note never loses its metadata. Reuses `/api/move`, constrained to flat `.wav` names within `/recordings/`.
- **Delete** — removes the `.wav`, its `index.csv` row, and any transcript sidecar together. Reuses `/api/delete`.

Everything stays on the card and in your own browser — no recording audio, filename, or transcript ever touches a project server. The tab shows "Insert a memory card..." when no card is mounted and "No voice notes yet..." when the card has none.

!!! note "Device clock and timestamps"
    The Cyber Fidget has no battery-backed real-time clock, so on a cold boot it doesn't know the date. When the portal page loads it POSTs the browser's wall-clock to `/api/time` (`settimeofday`), so any recording made afterwards lands a real timestamp in `index.csv`. The browser sends a timezone-adjusted epoch so the device — which keeps time as UTC — records your *local* wall-clock time. Recordings made before the first portal visit of a session stay stamped "No date". In "Deep Sleep" on mainboard v1.2, the clock may drift up to ~2 seconds per day / 1 minute per month (ESP32 internal real-time clock is rated +/- 20 parts per million drift at 32kHz).

### Files

The **Files** tab is a raw browser for the whole memory card -- the power-user view alongside the curated Media and Voice notes tabs. Where Media is shaped for music and Voice notes for recordings, Files shows **everything**: every file and folder of any type, the way Windows Explorer or macOS Finder does.

- **Navigate** one folder at a time -- click a folder to go in, use the breadcrumb at the top to jump back out. You always see the direct contents of the current folder, not a flattened dump of the whole card, so it stays clear what lives inside what.
- **See** each item's name, size, and modified date. (Dates only appear once the clock has been set this session -- see the note above; older files show "No date".)
- **Download** any single file, or tick several and download them as one `.zip` bundle (the same one-at-a-time, keep-this-page-open transfer the Voice notes tab uses, so the device only ever serves one file at a time).
- **Upload** by dropping files onto the current folder (or tapping to choose them).
- **New folder**, **Rename**, and **Delete** -- delete works on a single file, several selected items at once, or a whole folder (deleting a folder removes everything inside it).

Everything stays on the card and in your own browser -- nothing is uploaded to a project server.

!!! warning "The Files tab can delete anything on the card"
    Unlike the Media and Voice notes tabs, the Files browser can rename and delete *any* file or folder, including ones other features rely on (the music index, a recording's `index.csv`, configuration files). Deleting a folder removes everything inside it, and there is no recycle bin -- removed files are gone. Use it the way you would use Explorer or Finder.

### Live listening

The **Live listening** entry in the sidebar opens the [phone companion](companion.md)
(served from `/web/` on the card): live audio streaming from the device's microphone,
captions on the device's OLED, voice-note transcription, and daily-note summaries.
When the companion SD pack isn't on the card, the link lands on a built-in page that
explains how to get it.

### Playlists

M3U files stored in `/media/playlists/`. The web UI supports:
- Create/delete playlists
- Add tracks from the file browser
- Play entire playlists (sequential playback)
- Per-track play buttons within expanded playlists
- Missing file detection (dimmed with warning if referenced file no longer exists)

### Now-playing highlight

The currently playing track is highlighted with a cyan accent bar:
- In the **track table** when playing from the table or folder view
- In the **playlist** when playing from a playlist

The highlight follows next/prev navigation and persists across sort/search/re-render.

### Settings page

The Settings page provides WiFi network configuration:

- **WiFi Status** — shows current connection state, network name, IP address, and mDNS hostname
- **Network Scanner** — scan for nearby WiFi networks with signal strength bars
- **Connect** — select a network, enter password, connect. Credentials are saved to NVS for auto-reconnect.
- **Forget** — clear saved credentials and disconnect from the network
- **AP Info** — shows the always-available access point details

---

## Build impact

| | Before (Phase 2.75) | After (Phase 3.1) | Delta |
|---|---|---|---|
| RAM | 16.3% (53 KB) | 22.7% (74 KB) | +21 KB |
| Flash | 52.3% (1.6 MB) | 74.6% (2.3 MB) | +700 KB |

The flash increase is primarily ESPAsyncWebServer + WiFi libraries + ESPmDNS + the portal HTML/CSS/JS. RAM increase is the WiFi AP+STA stack (freed when portal exits).

---

## Files

| File | Lines | Purpose |
|------|-------|---------|
| `lib/WebPortalApp/WebPortalApp.h` | ~80 | Class declaration (AP+STA, mDNS) |
| `lib/WebPortalApp/WebPortalApp.cpp` | ~1000 | App lifecycle, WiFi STA, API routes, ID3 reader, OLED render |
| `lib/WebPortalApp/portal_page.h` | ~950 | PROGMEM SPA (HTML + CSS + JS + Settings page) |
| `scripts/add_network_lib.py` | ~35 | PlatformIO pre-build script for Network library |

### Network library linkage

pioarduino's ESP32 Arduino 3.x core split the WiFi library into `WiFi` + `Network`. PlatformIO's library dependency finder discovers WiFi (via ESPAsyncWebServer) but misses Network. The `add_network_lib.py` script compiles and links the framework's Network library using `env.BuildLibrary()`.

---

## Common issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Sign in to WiFi" browser can't upload files | Android captive portal WebView has restricted file input | Open `192.168.4.1` in Chrome/Firefox instead |
| Portal page doesn't load | DNS redirect failed | Manually navigate to `http://192.168.4.1` |
| Upload fails with 507 | SD card full | Delete files to free space |
| BT speaker won't reconnect after portal | WiFi didn't shut down cleanly | Restart the device |
| `idx.txt` showing in file list | Music index cache file | Filtered out in `/api/files` and `/api/tracks` |
| Track shows "-" for artist/album | No ID3 tags in the MP3 file | Re-tag the file with a tool like Mp3tag |
| `cyberfidget.local` doesn't resolve | mDNS not supported on device (older Android) | Use the IP address shown on the OLED or portal status bar |
| WiFi connection times out | Wrong password or network out of range | Re-enter password via Settings, move closer to router |
| Can't reach portal from home WiFi | Not connected to any WiFi network | Open Settings, scan, and connect to your WiFi first |
