<!-- Cyber Fidget documentation - CC BY-SA 4.0 -->
# Link your Fidget

Linking puts a Cyber Fidget on your account. Once it has saved WiFi, it can receive app changes from that account when it checks in, without a cable. Linking requires an account and a WiFi connection. You can still install apps and firmware from the website over a Universal Serial Bus (USB) cable without linking.

## Before you start

Save a WiFi network on the Fidget: open **Settings > Setup WiFi** and follow [Setting up WiFi](../firmware/web-portal.md#setting-up-wifi). A Fidget can remember up to three networks. Sign in at [cyberfidget.com](https://cyberfidget.com/). The Fidget needs to be able to reach the website using its saved network.

## Link it

1. On the Fidget, open **Settings > Link**. It shows a short code and the address `cyberfidget.com/my-fidget/link`.
2. Open [Link your Fidget](https://cyberfidget.com/my-fidget/link) while signed in. Type the code shown on the Fidget and select **Link my Fidget**.
3. The website says **Confirm on your Fidget**. Check the account in the Fidget's `Link to @<account>?` prompt, then choose **OK**. Choose **Not me** if it is the wrong account. The code expires after 10 minutes; open **Settings > Link** for a new one if needed.
4. The website shows **Linked to your account**. The Fidget can receive changes at its next check-in. See [Updates](updates.md) for when it checks in and how to check now.

## Link it from the My Fidget page

The [My Fidget](https://cyberfidget.com/my-fidget/) page can walk you through the same steps. The first time you plug in a Fidget over USB that is not on your account while you are signed in, a **Use it without the cable** panel opens once. After that, open it from the button on that Fidget's card.

1. **WiFi** - on the Fidget, open **Settings > Setup WiFi**. On your phone or computer, join the network named `CyberFidget-` plus the last 4 characters of the Fidget's ID, using the password on the Fidget's screen, then pick your home network. (Older firmware names its network `CyberFidget_AP`.)
2. **Link** - on the Fidget, open **Settings > Link** and type the code it shows into the panel, then press **OK** on the Fidget.
3. **Done** - you can unplug the Fidget any time. Changes you make now reach it over WiFi.

Signed out, you do not see this panel, and everything works over the cable.

## Unlink or pass it on

On the Fidget, open **Settings > Link**. When it shows **Linked account**, press Enter, choose **Unlink**, then confirm **Unlink this Fidget?** with **Unlink**. **Settings > Updates > Unlink this Fidget** opens the same link screen. You can also unlink it from [Your Fidgets](your-fidgets.md) on the website. Unlinking stops changes from that account; waiting changes are discarded, while apps already on the Fidget stay. If you unlink on the Fidget while it cannot reach the website, it says **Unlinked on this Fidget** and finishes notifying the website when you next link or check for updates.

If the Fidget changes hands, the new person signs in to their own account and repeats the link steps on the Fidget. The Fidget asks `Link to @<account>?` before changing the link. It then asks **Clear the apps from the previous account?**: choose **Clear** to remove those apps or **Keep** to leave them on the Fidget. The previous account can no longer send changes after the new link is confirmed; its **Your Fidgets** page shows **Linked elsewhere**.

## If linking does not finish

Linking uses the Fidget's own WiFi, not your computer's connection. When a link fails, **Settings > Link** says why:

| The Fidget shows | What it means |
| --- | --- |
| **Needs WiFi first** / **Settings > Setup WiFi** | No WiFi network is saved. Save one with **Settings > Setup WiFi**, then try again. |
| **Can't reach WiFi** / **Check it's in range** | A network is saved, but the Fidget could not join it. Move closer to the router or check the saved network. |
| **Could not link** / **Try again later** | Anything else, for example the website could not be reached. Try again later. |

Check the saved network and connection using the [Web Portal common issues](../firmware/web-portal.md#common-issues). If the code expired or you chose **Not me**, open **Settings > Link** for a new code. A request to link again leaves the existing link in place until you confirm the new one on the Fidget.
