<!-- Cyber Fidget documentation - CC BY-SA 4.0 -->
# Awake & dev mode

Open **Settings > Awake & dev mode** and use Left or Right to choose a mode. Press Enter to apply it, or Back to leave without changing it. The setting survives a restart until you turn it off or a stop rule ends it.

| Mode | What it does |
| --- | --- |
| **Off** | Normal use: the Fidget sleeps after about a minute without use and can make its daily check-in. |
| **Stay awake** | Keeps the Fidget awake without keeping WiFi connected. Bluetooth apps still work. Useful when developing over a Universal Serial Bus (USB) cable; no account is needed. |
| **Dev mode** | Keeps the Fidget awake and listens over WiFi for apps sent from your account. It needs a [linked Fidget](link-your-fidget.md) and saved WiFi. It uses noticeably more battery. |

For **Stay awake** and **Dev mode**, choose **After 30 min without use** or **Until I stop it**. Use means a button press, or an app arriving in Dev mode. Either choice also ends after 48 hours without a button press, or when the battery is low and the Fidget is not charging. Returning to **Off** restores normal sleep. The status bar shows an eye marker beside the battery for either awake mode. While Dev mode is listening, it also shows a WiFi marker and **Dev mode**; the back light slowly breathes blue while the menu is open. Apps control their own lights while running.

## Send from Studio

In [Studio](https://cyberfidget.com/create/), build an app for the linked Fidget and turn on **Send to my Fidget automatically**. When the Fidget is listening, Studio shows **Ready for changes**. Each completed build can then be sent to the Fidget. This control is available for supported built apps and screensavers, not drawn projects. If the Fidget is linked but is not listening, Studio shows **Linked - checks in periodically**; a manually sent app goes over at its next check-in, or you can select **Check for updates** on the Fidget. Dev mode sends require an account and a link; you can still send an app over USB without them.

## When listening pauses

Some apps need more memory or use the same radio. Before opening one, the Fidget shows **Pausing dev mode...** and stops listening until you return to the menu. A send made while it is paused can arrive after listening resumes. Opening a newly delivered app after WiFi was used may restart the Fidget once and go straight into that app.

The Music Player asks **Music uses Bluetooth. Restart without dev mode? Dev mode comes back next restart.** Choose **Restart** to use it for this power cycle, or **Cancel** to stay in the menu. Dev mode resumes on the next restart.

## If Dev mode is not ready

If you see **Dev mode: link this Fidget first**, follow [Link your Fidget](link-your-fidget.md). For **Dev mode: no saved network** or **Dev mode: not connected**, check the [Web Portal common issues](../firmware/web-portal.md#common-issues). For an app that has not arrived, use [Check for updates](updates.md#when-it-checks) after the connection is working.
