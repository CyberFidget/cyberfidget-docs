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
| `/api/files` | GET | Recursive JSON folder tree |
| `/api/tracks` | GET | Flat JSON array with ID3 metadata per track |
| `/api/upload?dir=/media/...` | POST | Multipart file upload |
| `/api/delete?path=/media/...` | POST | Delete file or folder |
| `/api/mkdir?path=/media/...` | POST | Create directory |
| `/api/move?from=...&to=...` | POST | Move/rename file |
| `/api/status` | GET | File count, SD space, connected clients |
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
