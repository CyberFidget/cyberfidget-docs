<!-- Cyber Fidget documentation - CC BY-SA 4.0 -->
# Set up WiFi over USB

A Fidget can learn your WiFi over its USB cable instead of through its own setup network (**Settings > Setup WiFi**). The website's **Use it without the cable** panel on [My Fidget](https://cyberfidget.com/my-fidget/) does this for you: it lists the networks your Fidget can see, you pick one and type its password, and the website sends that to the Fidget and checks that it can join. You can also send the same commands from your own program. This page describes them.

These commands use the same connection and conventions as the other [serial commands](serial-commands.md): 921600 baud, one command per line, replies starting with `[cmd]` (success) or `[err]` (refused).

## Does this Fidget have them?

Firmware that has these commands says so in its `syncinfo` reply with an extra line before the last one:

```
[cmd] syncinfo.setup=1
```

Older firmware has no `syncinfo.setup` line and answers `[err] unknown command: <command>` to the commands below. The website then shows the older steps (the Fidget's own **Setup WiFi**), with no error.

## Network names travel as hex

A network's name (its SSID) can contain spaces, symbols, and letters from any language, so replies never print it as text. They print its bytes as hex: two lowercase hex digits per byte. For example, `HomeNet` is `486f6d654e6574`. Decode the hex to bytes, then read the bytes as UTF-8 text to show the name. Keep the original bytes if you plan to save that network: a name that is not valid UTF-8 must be sent back exactly as it was received.

## Commands

| Command | Replies |
| --- | --- |
| `wifi scan` | `[cmd] wifi.scan=started`, then one `[cmd] wifi.net=rssi=<dBm> sec=<open\|wpa\|wpa2\|wpa3\|ent> ssid_hex=<hex>` line per network (each name once, strongest first, at most 20), then `[cmd] wifi.scan.done=<count>`. The scan takes a few seconds. |
| `wifi add <len> <crc32>` + payload | `[cmd] wifi.saved=ssid_hex=<hex> position=1`, or `[err] wifi.full=1`, `[err] wifi.invalid`, `[err] wifi.crc`, `[err] wifi.busy reason=<reason>` |
| `wifi saved` | `[cmd] wifi.saved.n=<count>`, one `[cmd] wifi.saved.net=ssid_hex=<hex>` line per saved network (first tried first), then `[cmd] wifi.saved.done=<count>`. Names only, never passwords. |
| `wifi try` | `[cmd] wifi.try=started`, then `[cmd] wifi.try=ok ssid_hex=<hex>` or `[cmd] wifi.try=fail reason=<auth\|absent\|timeout\|busy>`. Joining can take up to about 15 seconds. |

`sec=open` means the network needs no password. `rssi` is the signal strength in dBm (decibel-milliwatts): closer to zero is stronger, so -40 is a strong signal and -80 a weak one.

`wifi try` tries only the first saved network, which is the one `wifi add` saved last. Its failure reasons mean:

| Reason | Meaning |
| --- | --- |
| `auth` | The network refused the password. |
| `absent` | The Fidget could not find the network (or nothing is saved). |
| `timeout` | The join did not finish in time. |
| `busy` | Something else on the Fidget needed the radio and stopped the try. |

## Saving a network: `wifi add`

`wifi add` carries the password, so it is sent as a framed payload rather than as text on the command line:

1. Build the payload: the network name's bytes, one zero byte (NUL), then the password's UTF-8 bytes. An open network has an empty password, so its payload ends with the NUL.
2. Send `wifi add <len> <crc32>` where `<len>` is the payload length in bytes and `<crc32>` is its CRC-32 as 8 lowercase hex digits, followed by a newline and then exactly `<len>` payload bytes. Send the header and the payload in one write.
3. Wait for the reply before sending anything else. A command sent sooner makes the Fidget refuse the add.

Limits: the name is 1 to 32 bytes, the password 0 to 64 bytes, and neither may contain a NUL, a carriage return (CR) or a line feed (LF). The website refuses such a name or password before sending anything.

The Fidget keeps up to three networks and tries the most recently saved one first. Saving a network it already has replaces that network's password and moves it to the front. When three are saved, a new one is refused with `[err] wifi.full=1`; remove one with **Settings > Setup WiFi** on the Fidget first.

The password is never echoed. No reply, log line or `wifi saved` answer contains it, and the Fidget wipes its copies of the payload whatever the outcome. The website keeps it only until it is sent: it clears the password field when you press Save, and the password is never stored in the browser, logged, included in error reports, or sent to cyberfidget.com.

### After a refused add: resync

After `[err] wifi.invalid`, `[err] wifi.crc`, `[err] wifi.busy`, or no reply at all, the Fidget cannot tell whether more payload bytes are still on the way. It ignores every line it receives, without running or echoing it, until you resync:

1. Wait at least 100 ms without sending anything.
2. Send a newline, `version`, and a newline (`\nversion\n`). The first newline ends any half-finished line the refused payload left behind.
3. If no `[cmd] version=...` reply arrives, repeat from step 1.

The website tries up to five times, then asks you to unplug the Fidget and plug it back in. `[err] wifi.full=1` does not need a resync.

## When the Fidget is busy

`wifi scan` and `wifi try` are refused with `[err] wifi.busy reason=<reason>` while something else is using the radio. `wifi add` is refused the same way, with `reason=wifi`, only while a `wifi try` is running.

| Reason | What is using it | What to do |
| --- | --- | --- |
| `portal` | The Fidget's own **Setup WiFi** is open. | Close it on the Fidget. |
| `music` | The music player is open. | Close the music player. |
| `bluetooth` | Bluetooth has been used since the Fidget was turned on. WiFi needs a fresh start. | Restart the Fidget. |
| `wifi` | Another scan or try is still running. | Wait for it to finish. |
| `checkin` | The Fidget is checking in over WiFi. | Try again in a moment. |
| `link`, `ferry`, `update` | Linking, a USB file transfer, or an update is under way. | Try again when it finishes. |

## Example

```
> syncinfo
[cmd] syncinfo.fs_total=... (more lines)
[cmd] syncinfo.setup=1
[cmd] syncinfo.fw=1.4.1
> wifi scan
[cmd] wifi.scan=started
[cmd] wifi.net=rssi=-41 sec=wpa2 ssid_hex=486f6d654e6574
[cmd] wifi.scan.done=1
> wifi add 16 <crc32>        (followed by the 16 payload bytes "HomeNet", NUL, "secret12")
[cmd] wifi.saved=ssid_hex=486f6d654e6574 position=1
> wifi try
[cmd] wifi.try=started
[cmd] wifi.try=ok ssid_hex=486f6d654e6574
```
