# Phone Companion

The phone companion turns your phone into an accessory for the Cyber Fidget: hear
what the device hears, watch live captions appear on the device's screen, turn
saved voice notes into text, and write up a whole day as a tidy note -- all served
by the device itself, with your audio staying on hardware you own.

It is a small web app stored on the memory card. The device's [Web Portal](web-portal.md)
serves it at `/web/`, so the phone needs nothing installed: join the device's WiFi
(or have both on your home network), open the portal, and tap **Live listening**.

---

## Getting the companion onto the card

The companion ships as a folder called the *SD pack*. If you open `/web/` and the
pack isn't on the card yet, the device shows a built-in page with these same steps.

1. Build the pack from the firmware repository (`portal-companion/` -- see its
   README): `npm install`, then `npm run build`. A packaged download is planned.
2. Copy the resulting `dist/web/` folder onto the memory card as `/web/`, so the
   card contains `/web/index.html`. You can also upload the files through the
   portal's **Files** tab.
3. Reopen `/web/` from the portal. That's it -- the pack is ~32 MB, almost all of
   it the on-phone speech machinery.

---

## Live listening

Tap **Start live session** and the companion asks for your OK first:

> Sound from your device streams over its WiFi to this page and is turned into
> text right here on your phone. Nothing is uploaded anywhere.

Once connected you get a phosphor-style waveform of what the microphone hears.
Two buttons matter:

- **Hear it** -- plays the audio on your phone. It starts *muted* on purpose: with
  the phone next to the device you'd get feedback. Use earbuds, or listen from
  another room (this is the "remote microphone" trick).
- **Start captions** -- speech becomes text on your phone *and* on the device's
  OLED screen. The first time, you'll be asked to download the transcription pack
  (see below).

Only one phone can listen at a time -- a second connection is politely refused and
told why. Stopping the session, closing the page, leaving the network, or leaving
the portal app on the device all end the stream immediately.

!!! note "Keep the screen on"
    Phones pause background pages aggressively, so a live session is a
    screen-on activity. Where the browser allows it the companion holds a screen
    wake lock; on most phones (the device serves plain `http://`, which browsers
    treat as a limited context) you may need to raise your screen timeout for
    long sessions. The UI says which case you're in.

### Captions on the device screen

While captions run, the device's OLED becomes a caption display -- the wearable
half of the accessibility use case. In-progress phrases update in place; finished
phrases commit and scroll up. Press **Up** on the device to toggle a larger,
3-line text size. Captions may lag a few seconds behind speech depending on the
phone doing the transcribing.

---

## Transcription -- on your phone, not a server

Turning speech into text happens entirely on the phone, powered by a one-time
download (the *transcription pack*, about 60 MB for the standard pack). After
that one download it works fully offline -- the usual flow is: download it once at
home, then caption live sessions anywhere, including on the device's own WiFi
with no internet in sight.

- The download never starts on its own: you get a clear size and a "best on
  WiFi" prompt first.
- The pack is kept by your browser. If the phone ever clears it (some phones
  tidy up storage that hasn't been used in a while), the companion simply offers
  the download again -- nothing is lost.
- A second, larger pack is offered for newer phones: sharper English results,
  more demanding hardware.

### Transcripts for saved notes

The **Notes** tab lists every voice note on the card. Tap **Transcribe** and the
phone reads the recording from the card, transcribes it locally, shows the text
in a retro terminal view -- and writes it back to the card as a sidecar text file
next to the note (`REC_0042.txt` beside `REC_0042.wav`). Your words stay
consolidated in one user-owned place: the card.

---

## Daily notes

The **Daily** tab gathers everything transcribed on a chosen day -- live caption
sessions and note transcripts -- and shows you *exactly* the text that would be
sent, word for word. Then, only with your per-action OK, it asks a summary
generator to write a markdown daily note.

The summary generator runs on an account **you** bring: Anthropic, OpenAI, or
Google, configured in **Setup** with your own key. Every send names the provider
and asks fresh -- there is no "always allow". The finished note downloads to your
phone and can also be saved to the card as `/notes/2026-06-12.md`.

!!! warning "Your key, your custody"
    The provider key is stored only in your phone's browser, only for the
    device's pages. It is never uploaded, and the transcripts go straight from
    your phone to your chosen provider -- cyberfidget.com is never in the path.
    This needs internet, so the device should be joined to your home WiFi
    (portal **Settings**) with the phone on the same network.

---

## How it works

For the curious:

- The live stream is a single WebSocket at `/ws/live` on the device. The device
  sends raw PCM audio (16 kHz, 16-bit mono, 5,120-byte frames -- 160 ms each);
  the phone sends small JSON messages back: a clock sync on connect, and caption
  text as it transcribes. The exact contract lives in the firmware source
  (`lib/WebPortalApp/LiveLinkProtocol.h`) so both ends evolve together.
- If WiFi hiccups and the phone can't drain audio fast enough, the device drops
  the *oldest* unsent audio rather than stalling -- you lose a moment of sound,
  never the connection. Drops are counted in `/api/status`.
- Transcription uses an open speech model running in the browser via
  [transformers.js](https://github.com/huggingface/transformers.js), with the
  phone's GPU when the browser offers it and plain CPU otherwise. The model files
  are cached in IndexedDB, which is why the one-time download survives offline use.
- The microphone pipeline (capture task, ring buffer) is shared firmware code
  (`lib/MicCapture/`) -- the same path the [Voice Notes](voice-recorder.md) app
  records through, which is also why live listening and SD recording don't run
  at the same time.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `/web/` shows "not on the memory card yet" | SD pack missing or no card | Copy the pack to the card as `/web/` (steps above) |
| "Another phone is already listening" | One listener at a time | Stop the session on the other phone |
| Captions never start | Transcription pack not downloaded | **Setup** tab -> Download (needs internet once) |
| Captions lag badly | Phone transcribing slower than real time | Try the standard pack, close other tabs, or use a newer phone |
| Daily note fails to send | Phone has no internet (device AP only) | Join the device to home WiFi in portal **Settings**, keep the phone on that WiFi |
| Session drops when the phone locks | Browsers pause background pages | Keep the screen on during sessions |
