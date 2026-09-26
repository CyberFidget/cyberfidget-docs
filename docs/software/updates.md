<!-- Cyber Fidget documentation - CC BY-SA 4.0 -->
# Updates

Your Cyber Fidget checks for app changes and firmware updates over saved WiFi. App changes sent from your account need a [linked Fidget](link-your-fidget.md). You can also install apps and firmware from the website over a Universal Serial Bus (USB) cable without linking.

## When it checks

With **Auto-check: On**, a linked Fidget normally checks in once a day while asleep. With **Check at start-up: On**, it also checks at start-up if its last check-in was over an hour ago. Both settings are on by default. A check needs saved WiFi; automatic checks also wait for enough battery and may retry later after a failure.

Open **Settings > Updates** to change **Auto-check: On/Off** or **Check at start-up: On/Off**. Turning off **Check at start-up** leaves the daily sleep check on. Turning off **Auto-check** stops automatic check-ins; app changes then wait until you check manually. The screen explains: **Automatic check-ins are off. Remote changes wait for a manual check.** [Stay awake](awake-and-dev-mode.md) makes no automatic checks, while Dev mode checks for sent apps while it is connected.

To check yourself, choose **Check for updates** on the main menu, or **Settings > Updates > Check now**. A manual check still works with **Auto-check: Off**. If the Fidget used Bluetooth in this power cycle, it says **Restarting to check...** and resumes the check after restarting.

## Choose what to do

When a firmware version is available, the prompt says `Update <version> ready (<source>)` and offers:

| Choice | What happens |
| --- | --- |
| **Install now** | Starts installation if this Fidget is allowed to install firmware over WiFi. Otherwise it directs you to update from the website. |
| **Remind me later** | Leaves the offer waiting. It can appear again at a later start-up or check. |
| **Skip this version** | Hides this version; a newer version can still be offered. You can undo the skip in **Settings > Updates**. |

Firmware installation over WiFi is currently limited to Fidgets opted in through a USB serial command. See [Letting a Fidget install updates over WiFi (test ring)](../reference/serial-commands.md#letting-a-fidget-install-updates-over-wifi-test-ring). Other Fidgets show **Installing on your Fidget is coming soon. Update it from the website for now.** Use the [website update page](https://cyberfidget.com/update/) with USB for those Fidgets.

### Signed updates

A **digital signature** is a short code that only the holder of Cyber Fidget's private signing key can produce for one exact firmware file. Your Fidget carries the matching public keys, which can check a signature but cannot make one. If even one byte of the file changes, the signature no longer matches.

When an update carries a signature, the Fidget downloads the whole file, checks that it matches the size and checksum it was promised, and then checks the signature, all **before** it switches to the new version. If the signature is wrong, or was made with a key this Fidget does not know, it refuses the update and shows **This update could not be verified. Nothing changed.** Your Fidget keeps running the version it had, and that version is not offered automatically again. The USB opt-in does not override this: a signed update that fails its check is always refused.

Official releases are **not signed yet**: no official keys are built into the firmware so far, so official updates still install over WiFi only on Fidgets that have the USB opt-in, as described above. When official signing is turned on, a correctly signed official update will install over WiFi without the USB opt-in, on a Fidget whose firmware already includes the official keys.

Firmware you build yourself is never signed with Cyber Fidget's key. It still installs over USB from your computer or the website, as before. Over WiFi, an unsigned update installs only on a Fidget with the USB opt-in.

### A Fidget that needs one website update first

Some Fidgets were set up with an older storage layout that has no room to hold a second copy of the firmware while the new one downloads, so they cannot install an update over WiFi at all. When a new version is offered to one of these, the Fidget does not show the usual choices. Instead it says **Update once on website for WiFi updates**, with a single **OK**. It shows this once for each offered version; a newer version shows it once again. It does not restart, start a download, or report a failed update.

A manual check on such a Fidget reports `Update <version> available`, and while that version is on offer, the status row in **Settings > Updates** keeps showing **Update once on website for WiFi updates**. Update it once from the [website update page](https://cyberfidget.com/update/) over USB. That installation also gives the Fidget the newer layout, with room for later updates over WiFi, and it keeps the Fidget's saved WiFi networks and settings.

**Apply app changes automatically: On** is a separate setting in **Settings > Updates** and is on by default. It applies waiting app changes during a check-in; it does not install firmware. With it off, the prompt says **App changes waiting** and offers **Get them now** or **Later**. **Get them now** checks and applies the waiting changes once. **Later** leaves them waiting for a future check. These account app changes need a linked Fidget.

## What you will see afterward

The status bar says **Checking for updates...** during a check, **Update ready** or `Update <version> ready` when firmware is offered, or **App changes waiting** when app changes need your choice. Its WiFi symbol shows how recently the Fidget checked in. Open the status row in **Settings > Updates** for more detail. A successful firmware installation reports `Updated to <version>`.

A newly installed firmware version starts on probation: it must pass its checks and run its first app before the Fidget keeps it. Until its first menu appears, it does not use WiFi or Bluetooth and does not react to buttons (or to USB serial commands), so nothing can interrupt that first start. It also does not go to sleep while on probation, because waking from sleep before it is kept would undo a good update. If the battery runs flat during probation, the Fidget shuts down as usual, and this does not count as a failed update: if the new version had already passed its checks it is kept, and otherwise the Fidget returns to the previous version without the failed-update message, and the new version can be offered again. If it does not start properly, the Fidget returns to the previous version and shows **The update did not finish. Nothing changed.** That version is then not offered automatically again on this Fidget, so the start-up prompt stays quiet about it. A manual check still offers it, as `Update <version> ready` with the note **It did not finish last time**, so you can choose to try again. A newer version is offered as usual.

Opening a newly delivered app just after the Fidget used WiFi may restart it once; it opens straight into that app after the restart.

## If a check does not work

A check needs a saved WiFi network the Fidget can reach. To add one, open **Settings > Setup WiFi** (see [Setting up WiFi](../firmware/web-portal.md#setting-up-wifi)). To see which networks are saved, or to choose which one is tried first, open **Settings > Saved WiFi** (see [Saved WiFi on the device](../firmware/web-portal.md#saved-wifi-on-the-device)). For other connection problems, see the [Web Portal common issues](../firmware/web-portal.md#common-issues). If the Fidget is not linked, follow [Link your Fidget](link-your-fidget.md). For a USB connection or install problem, see [First flash troubleshooting](../getting-started/first-flash-arduino.md#troubleshooting).
