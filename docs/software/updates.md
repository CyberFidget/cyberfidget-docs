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

**Apply app changes automatically: On** is a separate setting in **Settings > Updates** and is on by default. It applies waiting app changes during a check-in; it does not install firmware. With it off, the prompt says **App changes waiting** and offers **Get them now** or **Later**. **Get them now** checks and applies the waiting changes once. **Later** leaves them waiting for a future check. These account app changes need a linked Fidget.

## What you will see afterward

The status bar says **Checking for updates...** during a check, **Update ready** or `Update <version> ready` when firmware is offered, or **App changes waiting** when app changes need your choice. Its WiFi symbol shows how recently the Fidget checked in. Open the status row in **Settings > Updates** for more detail. A successful firmware installation reports `Updated to <version>`.

A newly installed firmware version starts on probation: it must pass its checks and run its first app before the Fidget keeps it. If it does not start properly, the Fidget returns to the previous version and shows **The update did not finish. Nothing changed.** Opening a newly delivered app just after the Fidget used WiFi may restart it once; it opens straight into that app after the restart.

## If a check does not work

Check the saved network and connection in the [Web Portal common issues](../firmware/web-portal.md#common-issues). If the Fidget is not linked, follow [Link your Fidget](link-your-fidget.md). For a USB connection or install problem, see [First flash troubleshooting](../getting-started/first-flash-arduino.md#troubleshooting).
