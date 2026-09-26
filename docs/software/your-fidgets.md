<!-- Cyber Fidget documentation - CC BY-SA 4.0 -->
# Your Fidgets

**Your Fidgets** at [cyberfidget.com/my-fidget/devices/](https://cyberfidget.com/my-fidget/devices/) lists every Cyber Fidget on your account, plus any Fidget this browser knows from a Universal Serial Bus (USB) connection. Open it from the account menu under your picture (**Your Fidgets**), or from the **Your Fidgets >** link on the **My Fidget** page. Signed out, the page asks you to sign in.

To add a Fidget to the list, [link it](link-your-fidget.md). **Link a new Fidget** at the bottom of the page opens the link page.

## What each Fidget shows

Each Fidget has a tab with its name, the last four characters of its ID, and a label:

| Label | Meaning |
| --- | --- |
| **Managed by you** | Linked to your account. |
| **On this browser** | Only this browser knows it, from a USB connection. It is not linked. |
| **Linked elsewhere** | Someone linked it to a different account, so it no longer gets your changes. |

For a linked Fidget, the tab shows its name, board, firmware version, last check-in (for example **just now**, **yesterday**, or a date), how it checks in, and how many changes are waiting. The check-in line reads **Everyday - checks in on its own schedule**, or **Dev mode - checks in every few seconds** / **Always on - checks in every few seconds** while [Dev mode](awake-and-dev-mode.md) is on. Anything the Fidget has not reported yet shows **not known yet**.

The **Device** card lists the changes waiting for that Fidget (new apps, new versions, hidden or shown apps, menu order). A linked Fidget receives them the next time it checks in; see [Updates](updates.md#when-it-checks). A Fidget only this browser knows receives them when you plug it in over USB, or once you link it (**Link it to your account**).

## Rename

Choose **Rename**, type a new name, and select **Save**. Names can be 1 to 24 characters. For a linked Fidget the new name is saved to your account and this browser uses it too; for a Fidget only this browser knows, only this browser's copy changes.

## Download what is on this Fidget

For a linked Fidget, **Download what is on this Fidget** asks it to report what it has. The Fidget answers at its next check-in, over WiFi, so the button waits and says **Waiting for your Fidget to send what it has - it happens at its next check-in.** Keep that Fidget's tab open; the page looks for the answer every 10 seconds. To hurry it along, choose **Check for updates** on the Fidget.

When the answer arrives, the browser saves `fidget-<last4>-installed.json` (named with the last four characters of the Fidget's identifier), a JavaScript Object Notation (JSON) file with the Fidget's app list as it reported it and the app files your account has a copy of. The page confirms how many items it downloaded and when they were reported. If the Fidget reports an app your account has no file for, the page lists it under **Not available**. Built-in apps are listed but not included, and changes still waiting to be sent are not part of the download.

The file is a record of the device, not a Studio project. See [Keeping and sharing your work](import-export.md#files-and-the-cyber-fidget).

## Update firmware

**Update firmware** opens the [website update page](https://cyberfidget.com/update/), which installs firmware over USB. For updates over WiFi, see [Updates](updates.md).

## Unlink, remove, or forget

| Action | Shown for | What it does |
| --- | --- | --- |
| **Unlink** | A linked Fidget | After you confirm with **Unlink this Fidget**, the Fidget stops getting your changes until it is linked again. Changes still waiting for it are discarded; apps already on it stay. |
| **Remove** | A linked Fidget that has not checked in for over 30 days | The page says **Not seen since** and the date. After you confirm with **Remove this Fidget**, it leaves your account, as with Unlink. |
| **Remove** | A Fidget marked **Linked elsewhere** | Clears it from your list. The other account is never shown. |
| **Forget on this browser** | Any Fidget this browser has saved details for | Removes its saved apps and pending changes from this browser only. Nothing is sent to your account or the Fidget; a linked Fidget stays linked. |

To link a Fidget again after unlinking or removing it, open **Settings > Link** on the Fidget. You can also unlink from the Fidget itself; see [Unlink or pass it on](link-your-fidget.md#unlink-or-pass-it-on).
