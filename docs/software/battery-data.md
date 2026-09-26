<!-- Cyber Fidget documentation - CC BY-SA 4.0 -->
# Battery data

Your Cyber Fidget keeps a battery record: its battery readings and when it started, slept and shut down. It keeps this on the Fidget whether or not you share it. There are two separate ways to share a copy with Cyber Fidget, and both are your choice:

- **Share battery data**, a setting on the Fidget. A [linked Fidget](link-your-fidget.md) sends its record itself, at most about once a day.
- **The browser question**, asked when you connect your Fidget to the website over a Universal Serial Bus (USB) cable. The browser reads the record from the Fidget and sends one copy.

The [privacy page](https://cyberfidget.com/privacy/) describes what is kept and why.

## Share battery data (on the Fidget)

Open **Settings > Updates** and select **Share battery data: Off** to turn it on. It is **off** until you turn it on. When you turn it on, the Fidget explains:

> Share battery data. Daily at update checks: Battery readings and on/off/sleep events with times. No app content or WiFi names. Off anytime.

Press Enter or Back to close the explanation.

### When it sends

The Fidget sends its record only when all of these are true:

- **Share battery data** is on.
- The Fidget is [linked](link-your-fidget.md) to an account.
- It has just finished a successful **automatic** check-in: the daily check-in while asleep, or the check-in at start-up (see [Updates](updates.md#when-it-checks)). Manual checks, Stay awake and Dev mode never send it.
- The battery is at least 3.6 volts and 20 percent, the same limit automatic check-ins use.
- Its last accepted report was at least 21 hours ago.
- That check-in still has enough time left. The Fidget never keeps WiFi on longer just to send this.

So it sends at most about once a day. If a send fails, nothing is lost: the Fidget tries again at a later automatic check-in and sends everything the site has not yet accepted. The website accepts at most one new report from the same Fidget every 20 hours.

### What is included

- **Battery records** added since the last report the site accepted, up to 1,024 of them (more than a full day awake). Each has a record number, the battery voltage, charge percentage and charging rate, and what happened: a start, a daily check-in, a reading taken while awake, going to sleep, or a low-battery shutdown. Depending on the kind, it also holds why the Fidget woke, how many check-ins it has made, or how long it had been on.
- **Running totals**: how many times it has started and checked in, total time on, approximate charge cycles, the lowest and highest battery voltage seen, and how many records were written or lost.
- The Fidget's **device identifier** (12 characters derived from its hardware address) and its **firmware version**.
- The time it was sent, and whether older records were missing from this report.

### What is not included

- Your apps, their code or files, and your Studio projects.
- WiFi network names or passwords.
- Your account. The Fidget proves it is a linked Fidget when it sends, but the website stores the report **by device identifier only**, not with your account.

### Turn it off

Open **Settings > Updates** and select **Share battery data: On** to turn it off. It stops future reports right away. Reports already sent are kept; to have them deleted, contact Cyber Fidget as described on the [privacy page](https://cyberfidget.com/privacy/).

## The browser question

When you connect your Fidget over USB on **My Fidget** or in **Studio**, the website may ask **Help improve Cyber Fidget?**:

> Would you share a device health and usage record from this Cyber Fidget? It covers battery readings, charging, starts, time on and asleep, and the software version. It does not include your app code or design files.

- **Yes** reads the record from the Fidget and sends one copy. Afterward the page shows, for example, **Your Cyber Fidget has started up 42 times and been on about 12.5 hours since its record began.**
- **No** sends nothing.
- Tick **Don't ask again** to make your answer stick: with **Yes**, this browser shares at each connect without asking; with **No**, it stops asking.
- Closing the question without answering sends nothing, and it asks again at your next connect. It asks at most once per Fidget per visit.

This choice belongs to **this browser and this Fidget** only. It is separate from **Share battery data** on the Fidget: turning one on or off does not change the other. To change the browser choice later, use **Usage sharing: On / Off / Not set** in the device panel on My Fidget. If a share fails, the page says **Could not share the usage record this time.**

Browser shares do not need an account and are not linked to one either.
