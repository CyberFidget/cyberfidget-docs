<!-- Cyber Fidget documentation - CC BY-SA 4.0 -->
# Link your Fidget

Linking puts a Cyber Fidget on your account. Once it has saved WiFi, it can receive app changes from that account when it checks in, without a cable. Linking requires an account and a WiFi connection. You can still install apps and firmware from the website over a Universal Serial Bus (USB) cable without linking.

## Before you start

Save a WiFi network on the Fidget through the [Web Portal](../firmware/web-portal.md#settings-page). Sign in at [cyberfidget.com](https://cyberfidget.com/). The Fidget needs to be able to reach the website using its saved network.

## Link it

1. On the Fidget, open **Settings > Link**. It shows a short code and the address `cyberfidget.com/my-fidget/link`.
2. Open [Link your Fidget](https://cyberfidget.com/my-fidget/link) while signed in. Type the code shown on the Fidget and select **Link my Fidget**.
3. The website says **Confirm on your Fidget**. Check the account in the Fidget's `Link to @<account>?` prompt, then choose **OK**. Choose **Not me** if it is the wrong account. The code expires after 10 minutes; open **Settings > Link** for a new one if needed.
4. The website shows **Linked to your account**. The Fidget can receive changes at its next check-in. See [Updates](updates.md) for when it checks in and how to check now.

## Unlink or pass it on

On the Fidget, open **Settings > Link**. When it shows **Linked account**, press Enter, choose **Unlink**, then confirm **Unlink this Fidget?** with **Unlink**. **Settings > Updates > Unlink this Fidget** opens the same link screen. You can also unlink it from **Your Fidgets** on the website. Unlinking stops changes from that account; waiting changes are discarded, while apps already on the Fidget stay. If you unlink on the Fidget while it cannot reach the website, it says **Unlinked on this Fidget** and finishes notifying the website when you next link or check for updates.

If the Fidget changes hands, the new person signs in to their own account and repeats the link steps on the Fidget. The Fidget asks `Link to @<account>?` before changing the link. It then asks **Clear the apps from the previous account?**: choose **Clear** to remove those apps or **Keep** to leave them on the Fidget. The previous account can no longer send changes after the new link is confirmed; its **Your Fidgets** page shows **Linked elsewhere**.

## If linking does not finish

Check the saved network and connection using the [Web Portal common issues](../firmware/web-portal.md#common-issues). If the code expired or you chose **Not me**, open **Settings > Link** for a new code. A request to link again leaves the existing link in place until you confirm the new one on the Fidget.
