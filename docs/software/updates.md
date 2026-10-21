<!-- Cyber Fidget documentation - CC BY-SA 4.0 -->
# Updates

Your Cyber Fidget checks for app changes and firmware updates over saved WiFi. App changes sent from your account need a [linked Fidget](link-your-fidget.md). You can also install apps and firmware from the website over a Universal Serial Bus (USB) cable without linking.

[Open the update page](https://cyberfidget.com/update/){ .md-button }

## The short version

- Your Fidget checks for updates on its own about once a day over saved WiFi.
- Choose **Check for updates** to check any time.
- When an update is offered, choose **Install now**, **Remind me later** or **Skip this version**.
- After installation, it restarts and reports `Updated to <version>`.
- If it asks you to update from the website, use the [update page](https://cyberfidget.com/update/) in a [supported browser](supported-browsers.md) on a computer with a USB cable.
- App changes from your account need a [linked Fidget](link-your-fidget.md).

## When it checks

With **Auto-check: On**, a linked Fidget normally checks in once a day while asleep. With **Check at start-up: On**, it also checks at start-up if its last check-in was over an hour ago. Both settings are on by default. A check needs saved WiFi; automatic checks also wait for enough battery and may retry later after a failure.

Open **Settings > Updates** to change **Auto-check: On/Off** or **Check at start-up: On/Off**. Turning off **Check at start-up** leaves the daily sleep check on. Turning off **Auto-check** stops automatic check-ins; app changes then wait until you check manually. The screen explains: **Automatic check-ins are off. Remote changes wait for a manual check.** See [Awake and dev mode](awake-and-dev-mode.md) for checks while the Fidget stays awake.

To check yourself, choose **Check for updates** on the main menu, or **Settings > Updates > Check now**. A manual check still works with **Auto-check: Off**.

### Stable or test versions

**Settings > Updates > Versions: Stable** or **Versions: Test** chooses which firmware releases the Fidget is offered. Press Enter to switch. With **Stable**, the Fidget is offered only finished releases. With **Test**, it is also offered test versions: early builds for trying features before general release. A Fidget running a test version starts out on **Test** until you change it. Switching clears any update already on offer, so the next check looks again. An update for the other choice says **This update needs Test versions.**

## Choose what to do

When a firmware version is available, the prompt says `Update <version> ready (<source>)` and offers:

| Choice | What happens |
| --- | --- |
| **Install now** | Starts installation over WiFi if this Fidget supports it and has enough battery. It says **Charge your Fidget first.** if the battery is low, or directs you to the website if it cannot install over WiFi. |
| **Remind me later** | Leaves the offer waiting. It can appear again at a later start-up or check. |
| **Skip this version** | Hides this version; a later version can still be offered. You can undo the skip in **Settings > Updates**. |

Official releases are signed to confirm they come from Cyber Fidget; see [Signed updates](#signed-updates). If your Fidget asks you to update from the website, open the [website update page](https://cyberfidget.com/update/) in a [supported browser](supported-browsers.md) on a computer with a USB cable. This also applies to **Update once on website for WiFi updates**.

To go back to an earlier version, pick it in the update page's **Version** list. This keeps saved WiFi, settings and apps. See [Go back to an earlier version](updating.md#go-back-to-an-earlier-version).

### Signed updates

**Why updates are signed:** a Fidget can download and install firmware over WiFi, with no cable to your computer. Signing makes sure the firmware it installs that way really comes from Cyber Fidget, so nobody can pass off their own firmware as an official update and slip it onto your Fidget over the air.

**Your Fidget is not locked down.** Signatures are checked only for updates over WiFi. Installing over USB needs no Cyber Fidget signature: you can install firmware you build or change yourself from your computer (see [Firmware development](../firmware/index.md)). The device's startup code doesn't check signatures, so you stay free to put your own software on it. The website update page installs the official releases over USB.

### App changes from your account

**Apply app changes automatically: On** is a separate setting in **Settings > Updates** and is on by default. It applies waiting app changes during a check-in; it does not install firmware. With it off, the prompt says **App changes waiting** and offers **Get them now** or **Later**. **Get them now** checks and applies the waiting changes once. **Later** leaves them waiting for a future check. These account app changes need a linked Fidget.

## What you will see afterward

The status bar says **Checking for updates...** during a check, **Update ready** or `Update <version> ready` when firmware is offered, or **App changes waiting** when app changes need your choice. Its WiFi symbol shows how recently the Fidget checked in. Open the status row in **Settings > Updates** for more detail. A successful firmware installation reports `Updated to <version>`.

After installation, the Fidget restarts. If an update does not finish, it returns to the version it had and says **The update did not finish. Nothing changed.** You can try again with a manual check.

A delivered app opens directly, or after one restart if memory is short. If it stops with an error or cannot load, press any button to return to the menu. If you see **Finishing check...**, wait for the automatic check to stop. For **Checking for updates. Try again in a moment.**, try opening the app again shortly.

## If a check does not work

A check needs a saved WiFi network the Fidget can reach. To add one, open **Settings > Setup WiFi** (see [Setting up WiFi](../firmware/web-portal.md#setting-up-wifi)). To see which networks are saved, or to choose which one is tried first, open **Settings > Saved WiFi** (see [Saved WiFi on the device](../firmware/web-portal.md#saved-wifi-on-the-device)). For other connection problems, see the [Web Portal common issues](../firmware/web-portal.md#common-issues). If the Fidget is not linked, **Check for updates** shows **Not linked yet** / **Settings > Link** (with automatic check-ins off, the headline reads **Not linked: Settings > Link**); follow [Link your Fidget](link-your-fidget.md). For a USB connection or install problem, see [First flash troubleshooting](../getting-started/first-flash-arduino.md#troubleshooting).

!!! advanced "Advanced: how updates work under the hood"

    You do not need these details to use updates. They explain the firmware, the built-in software that runs the device.

    ### Check timing

    [Stay awake](awake-and-dev-mode.md) makes no automatic checks. Dev mode checks for sent apps while it is connected. Firmware installation needs the same battery level as an automatic check.

    A check you start yourself looks for firmware releases. An automatic check-in looks for it when the website mentions an update, and otherwise whenever the Fidget last looked about 20 hours ago or more. So even a Fidget with nothing else waiting hears about a release within about a day. In Dev mode, the Fidget looks for firmware only when the website mentions an update, at most once an hour, and not while an app is waiting to be delivered; choosing **Check for updates** yourself checks for firmware releases even in Dev mode.

    If the Fidget used Bluetooth in this power cycle, it says **Restarting to check...** and resumes the check after restarting.

    ### Digital signatures

    A **digital signature** is a short code that only the holder of Cyber Fidget's private signing key can produce for one exact firmware file. Your Fidget carries the matching public keys, which can check a signature but cannot make one. If even one byte of the file changes, the signature does not match.

    When an update carries a signature, the Fidget downloads the whole file, checks that it matches the size and checksum it was promised, and then checks the signature, all **before** it switches to the offered version. If the signature is wrong, it refuses the update and shows **This update could not be verified. Nothing changed.** Your Fidget keeps running the version it had, and that version is not offered automatically again. The USB opt-in does not override this: a signed update that fails its check is refused. If an update was signed with a key this Fidget does not know yet (for example, a Fidget on older firmware when a different key starts being used), it keeps offering the update but asks you to install it from the website instead of over WiFi.

    Official releases **are signed**, and the firmware has the official public keys built in. A correctly signed official update installs over WiFi without the USB opt-in. A Fidget running firmware from before the official keys were built in does not know the key: it keeps the update on offer and asks you to install it from the website. One update from the website over USB gives it the keys, and later official updates can then install over WiFi.

    Firmware you build yourself isn't signed with Cyber Fidget's key. It installs over USB from your computer. Over WiFi, an unsigned update installs only on a Fidget with the USB opt-in.

    A Fidget that cannot install a particular update over WiFi shows **Installing on your Fidget is coming soon. Update it from the website for now.** This happens when its firmware does not know the signing key, or when the update is unsigned and the Fidget does not have the USB opt-in. See [Letting a Fidget install updates over WiFi (test ring)](../reference/serial-commands.md#letting-a-fidget-install-updates-over-wifi-test-ring).

    ### A Fidget that needs one website update first

    Some Fidgets were set up with an older storage layout that has no room to hold a second copy of the firmware while the offered version downloads, so they cannot install an update over WiFi at all. When a later version is offered to one of these, the Fidget does not show the usual choices. Instead it says **Update once on website for WiFi updates**, with a single **OK**. It shows this once for each offered version; a later version shows it once again. It does not restart, start a download, or report a failed update.

    A manual check on such a Fidget reports `Update <version> available`, and while that version is on offer, the status row in **Settings > Updates** keeps showing **Update once on website for WiFi updates**. Update it once from the [website update page](https://cyberfidget.com/update/) over USB. That installation also gives the Fidget a layout with room for later updates over WiFi, and it keeps the Fidget's saved WiFi networks and settings.

    ### First start after installation

    An installed firmware version starts on probation: it must pass its checks and run its first app before the Fidget keeps it. Until its first menu appears, it does not use WiFi or Bluetooth and does not react to buttons (or to USB serial commands), so nothing can interrupt that first start. It also does not go to sleep while on probation, because waking from sleep before it is kept would undo a good update.

    If the battery runs flat during probation, the Fidget shuts down as usual, and this does not count as a failed update: if the offered version had already passed its checks it is kept, and otherwise the Fidget returns to the previous version without the failed-update message, and that version can be offered again.

    If it does not start properly, the Fidget returns to the previous version and shows **The update did not finish. Nothing changed.** That version is then not offered automatically again on this Fidget, so the start-up prompt stays quiet about it. A manual check still offers it, as `Update <version> ready` with the note **It did not finish last time**, so you can choose to try again. A later version is offered as usual.

    ### Delivered apps and memory

    A delivered app opens directly, even just after the Fidget used WiFi. Only if memory is unusually short does the Fidget restart once and open straight into that app. To make that possible, apps sent to the Fidget run from its larger, slightly slower extra memory (Pseudo-Static RAM, PSRAM), so they run about 10 percent slower than in the chip's internal memory in measurements.

    If a sent app runs out of memory, the screen shows its name, **stopped: out of memory** and **press any button**; any other failure shows **stopped with an error** instead.

    If a sent app cannot be loaded at all, the screen shows **App failed to load**, the reason (**no app staged**, **file not found**, **empty file**, **file too large**, **out of memory** or **read failed**) and **press any button**. In every one of these cases, press any button to return to the menu.

    If you open an app that needs a lot of memory while an automatic check is running, the Fidget shows **Finishing check...** and stops the check first; if the check cannot stop yet, it says **Checking for updates. Try again in a moment.** A check you started yourself runs on.
