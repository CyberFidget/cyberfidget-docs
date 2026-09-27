<!-- Cyber Fidget documentation - CC BY-SA 4.0 -->
# Update or reset your Fidget

There are several ways to change the firmware on your Cyber Fidget or to start it over. Most of the time you want a normal update, which keeps everything you saved. The others are for going back to an earlier version or for a clean start.

| You want to... | Use | Keeps your saved WiFi, settings and apps? |
| --- | --- | --- |
| Get the newest version | A [normal update](#update-normally), over WiFi or from the website | Yes |
| Try new features early | [Test versions](#stable-or-test-versions) | Yes |
| Go back to an earlier version | The [version picker on the website](#go-back-to-an-earlier-version) | Yes |
| Start over, keeping the firmware you have | [Reset to factory](#reset-to-factory-on-the-fidget) on the Fidget | No |
| Start over with a fresh copy of the firmware, or rescue a Fidget that does not start properly | [Erase everything and reinstall](#erase-everything-and-reinstall-on-the-website) on the website | No |

None of these touch the memory card or anything on it.

## Update normally

A normal update replaces the firmware and keeps the Fidget's saved WiFi networks, settings, installed apps and account link.

- **Over WiFi.** A linked Fidget with saved WiFi finds new versions when it checks in, and offers them with **Install now**, **Remind me later** or **Skip this version**. See [Updates](updates.md) for when it checks and what each choice does.
- **From the website over a Universal Serial Bus (USB) cable.** Open the [website update page](https://cyberfidget.com/update/) in Google Chrome or Microsoft Edge on a computer, plug in the Fidget, and choose **Install update**. This works for every Fidget, including one that cannot install an update over WiFi yet. The install takes about a minute; keep the Fidget plugged in.

## Stable or test versions

Test versions are early builds for trying new features before everyone gets them. Finished releases are called stable.

- **On the Fidget**, **Settings > Updates > Versions** chooses **Stable** or **Test**; press Enter to switch. With **Test**, updates over WiFi also offer test versions. A Fidget running a test version starts out on **Test** until you change it.
- **On the website update page**, the **Version** list shows stable releases first, with the newest one marked **(latest)** and chosen by default. Test versions are listed separately, under **Test versions**, each marked **(test version)**. The website installs a test version only when you pick one.

## Go back to an earlier version

If a new version misbehaves, you can go back to an earlier one from the [website update page](https://cyberfidget.com/update/) over USB:

1. Plug the Fidget into a computer and open the update page in Chrome or Edge.
2. In the **Version** list, pick the earlier version you want.
3. Choose **Install update**.

Like any normal update, this keeps your saved WiFi, settings and apps. Updates over WiFi never go back to an earlier version, so use the website for this. Later, the Fidget may offer the newer version again; choose **Skip this version** if you want it to stop asking (see [Updates](updates.md#choose-what-to-do)).

## Reset to factory (on the Fidget)

**Settings > Reset to factory** erases what you have saved on the Fidget and keeps its firmware. Use it before passing the Fidget on, or when you want to start fresh without a computer.

It erases:

- Apps sent to the Fidget, and the menu order
- Saved WiFi networks
- Settings, including the update settings in **Settings > Updates**
- The link to your account
- The battery record

It keeps the firmware version the Fidget is running, the built-in apps that come with it, and the memory card.

To reset:

1. Open **Settings > Reset to factory**. The screen says **Erase everything?** and lists what goes and what stays.
2. Hold **Enter** for three seconds. A bar fills while you hold; letting go early empties it again. Press **Back** to leave without erasing.
3. The Fidget shows **Erasing...**, then restarts like new.

The reset is refused, and nothing is erased, when:

| Message | Why | What to do |
| --- | --- | --- |
| **Finish update first** | A newly installed firmware version has not finished its first start yet (see [Updates](updates.md#what-you-will-see-afterward)). | Let the Fidget finish starting, then try again. |
| **Update is starting** | An update is about to start. | Let the update finish, then try again. |
| **Check is still busy**, **WiFi did not stop** or **Bluetooth is busy** | Something was still using the network or radio. | Try again in a moment. |

If the Fidget says **Could not erase apps**, it could not clear its app storage and leaves the settings in place; try again. Afterward, set up WiFi again with **Settings > Setup WiFi**, and [link the Fidget](link-your-fidget.md) again to get changes from your account.

## Erase everything and reinstall (on the website)

**Erase everything and reinstall** erases the whole Fidget and installs a fresh copy of the firmware you choose. It is under **Advanced** on the [website update page](https://cyberfidget.com/update/), and it needs a USB cable and Chrome or Edge on a computer. Use it when the Fidget is stuck on something it saved, when it does not start properly, or when you want a clean start on a particular version.

It erases saved WiFi networks, installed apps and their order, settings, the link to your account, and the battery record. It keeps the memory card and everything on it.

1. Plug in the Fidget and open **Advanced** on the update page, then choose **Erase everything and reinstall**.
2. Check the list of what it erases and keeps, and pick the **Version to install**. Its list and default match the normal **Version** list.
3. Type `ERASE` in the box and choose **Erase and reinstall**.

The website downloads and checks every part of the firmware before it erases anything. If something goes wrong before the erase, it says **Nothing was erased - your Fidget is unchanged.** Once the erase has started, the Fidget is blank until the install finishes: if the install stops then, keep the Fidget plugged in and try again, because it needs a finished reinstall to start up. When it is done, the page says **Your Cyber Fidget is like new**, and the Fidget restarts. Choose **Link it to your account** to get your changes over WiFi again.

## Which one to use

- **Something is wrong with a new version:** go back to an earlier version with a normal website install. Your saved things stay.
- **You are giving the Fidget away, or want its saved things gone:** use **Reset to factory** on the Fidget. No computer needed.
- **Reset to factory did not help, the Fidget does not start properly, or you want a fresh copy of a particular version:** use **Erase everything and reinstall** on the website.
