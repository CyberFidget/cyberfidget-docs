<!-- Cyber Fidget documentation - CC BY-SA 4.0 -->
# Awake & dev mode

Open **Settings > Awake & dev mode** and use Left or Right to choose a mode. Press Enter to apply it, or Back to leave without changing it. The setting survives a restart until you turn it off or a stop rule ends it.

| Mode | What it does |
| --- | --- |
| **Off** | Normal use: the Fidget sleeps after about a minute without use and can make its daily check-in. |
| **Stay awake** | Keeps the Fidget awake without keeping WiFi connected. Bluetooth apps still work. Useful when developing over a Universal Serial Bus (USB) cable; no account is needed. |
| **Dev mode** | Keeps the Fidget awake and listens over WiFi for apps sent from your account. It needs a [linked Fidget](link-your-fidget.md) and saved WiFi. It uses noticeably more battery. |

For **Stay awake** and **Dev mode**, choose **After 30 min without use** or **Until I stop it**. Use means a button press, or an app arriving in Dev mode. Either choice also ends after 48 hours without a button press, or when the battery is low and the Fidget is not charging. Returning to **Off** restores normal sleep. The status bar shows an eye marker beside the battery for either awake mode. While Dev mode is listening, it also shows a WiFi marker and **Dev mode**; the back light slowly breathes blue while the menu is open. Apps control their own lights while running.

## How often Dev mode checks in

While Dev mode is listening, the Fidget checks in with the website for new apps. It checks quickly, about every 2 seconds, only while a Studio tab with **Send to my Fidget automatically** turned on is open for that Fidget, or a send to it is under way, and for about a minute afterward. The rest of the time it checks about every 30 seconds. To keep data use small, a check-in sends the Fidget's app list only at the start of a session or when that list has changed, and the Fidget keeps one secure connection open between quick check-ins instead of opening a new one each time.

## Send from Studio

In [Studio](https://cyberfidget.com/create/), build an app for the linked Fidget and turn on **Send to my Fidget automatically**. When the Fidget is listening, Studio shows **Ready for changes**. Each completed build can then be sent to the Fidget. This control is available for supported built apps and screensavers, not drawn projects. If the Fidget is linked but is not listening, Studio shows **Linked - checks in periodically**; a manually sent app goes over at its next check-in, or you can select **Check for updates** on the Fidget. Dev mode sends require an account and a link; you can still send an app over USB without them.

## If a send does not work

When a send over the USB cable fails, the website names what went wrong. In every case your Fidget is fine, nothing was half-installed, and your changes are still saved on the website, ready to send again.

| Message | What happened | What to do |
| --- | --- | --- |
| **Your Fidget didn't answer.** | The Fidget did not reply over the cable. | Press a button on it or plug it in again, then try again. |
| **Your Fidget is busy.** | The Fidget was in the middle of something else. The website already waits and retries once before saying this. | Wait a moment, then try again. |
| **The connection dropped mid-send.** (or **The cable may have been unplugged mid-send.**) | The cable or connection was lost during the send. | Check the cable and try again. |
| **Your changes could not be sent.** (or `<name> didn't make it across.`) | Any other failure. | Try again. |

If only part of a send went across, the website says **Some changes did not go across.**, lists what made it, and keeps the rest to try again.

Building an app again after it is already on your Fidget sends the new build as an update: it replaces the app in the same menu place instead of adding a second copy. Studio says **Updated your Fidget's changes. Open My Fidget to send.** when it queues the update, and **Already on your Fidget - nothing to send.** when the build has not changed. Older Fidget firmware cannot replace an app this way; for that Fidget the update stays waiting, with the note **Update your Fidget's firmware to send a new build of an app it already has.**, and goes across once you [update the firmware](updates.md). The rest of the send still goes ahead.

## When listening pauses

Some apps need more memory or use the same radio. Before opening one, the Fidget shows **Pausing dev mode...** and stops listening until you return to the menu. A send made while it is paused can arrive after listening resumes. Delivered apps normally open directly and dev mode keeps listening while they run, when there is enough memory; a new build of the app that is running relaunches it in place, without pressing Back. Only if memory is unusually short does the Fidget restart once and go straight into the app.

The Music Player asks **Music uses Bluetooth. Restart without dev mode? Dev mode comes back next restart.** Choose **Restart** to use it for this power cycle, or **Cancel** to stay in the menu. Dev mode resumes on the next restart.

## If Dev mode is not ready

If you see **Dev mode: link this Fidget first**, follow [Link your Fidget](link-your-fidget.md). For **Dev mode: no saved network**, add one with **Settings > Setup WiFi** (see [Setting up WiFi](../firmware/web-portal.md#setting-up-wifi)). For **Dev mode: not connected**, check **Settings > Saved WiFi** and the [Web Portal common issues](../firmware/web-portal.md#common-issues). For an app that has not arrived, use [Check for updates](updates.md#when-it-checks) after the connection is working.
