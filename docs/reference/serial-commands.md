<!-- Cyber Fidget documentation - CC BY-SA 4.0 -->
# Serial commands

Cyber Fidget accepts text commands over its USB serial connection. Connect the USB cable, open a serial terminal at **921600 baud**, and send each command followed by a newline. Opening the port may restart the Fidget. Wait for it to start, then send `version` until it answers. Commands are case-insensitive; arguments may be case-sensitive. Success lines start with `[cmd]`, and errors start with `[err]`. Values in angle brackets below are placeholders; square brackets mean optional arguments. A reply that lists several lines is complete at its stated final line.

!!! tip "A console in the browser"
    The website's bench page, [cyberfidget.com/dev/chassis.html](https://cyberfidget.com/dev/chassis.html), is a serial console that needs no terminal program. It connects over Web Serial from a desktop Chromium-based browser (Chrome or Edge) at 921600 baud, waits for `version` to answer, and shows the Fidget's screen live. Type commands in **Command input** (Up and Down recall earlier ones), pick from the **Commands** list (a command with placeholders is copied into the input for you to finish), or read **Device help**, which lists the commands the connected Fidget's `help` reply names.

## Commands in every build

| Command and arguments | Reply format |
| --- | --- |
| `version` | `[cmd] version=<firmware-version>` |
| `info` | `[cmd] info.fw=...`, `.type=...`, `.built=...`, `.git=...`, `.dirty=...`, `.chip=...`, `.mac=...`, `.id=<12 hex digits>`, `.uptime_ms=...`, `.battery.voltage_mv=...`, `.battery.soc=...`, `.battery.crate=...`, `.board_rev=<major>.<minor>`, `.board=src=<source> hil=<0\|1> eng=<0\|1> layout=<n>`; ends with `[cmd] info.wake.cause=...` |
| `help` | `[cmd] help=<commands>`, `[cmd] help.sync=<commands>`, `[cmd] help.update=<commands>`; test builds add `[cmd] help.test=<commands>` |
| `mark <id>` | `[cmd] mark=<id> uptime_ms=<millis>`; without an ID: `[err] mark.usage=mark <id>` |
| `reboot` | `[cmd] reboot=now`, then the device restarts immediately |
| `battery` | `[cmd] battery.vcell_mv=<mV\|-1> soc=<percent> crate=<percent/hour>` |
| `diary` | `[cmd] diary.stats=boot=<n> checkins=<n> on_s=<n> cycles=<n> vmin=<mv> vmax=<mv> written=<n> dropped=<n>`, up to eight `[cmd] diary.rec=<seq> ev=<name> t=<n> mv=<n> soc=<x.x> crate=<x.xx>` lines, then `[cmd] diary.done=<total_records>` |
| `diary clear` | `[cmd] diary.clear=ok`; invalid argument: `[err] diary.usage=diary [clear]` |
| `menutree` | `[cmd] menutree.*` tagged menu-tree lines |
| `screencap` | `[cmd] screencap w=128 h=64 bpp=1 fmt=colpage len=<n> b64=<data>` |
| `screenstream off` | `[cmd] screenstream=off` |
| `screenstream on [fps]` | `[cmd] screenstream=on fps=<fps> interval_ms=<ms>`, followed by `screencap` frames until stopped |
| `upd slot` | `[cmd] upd.slot=<label> state=<state> boot=<label> other=<label> other_state=<state> pend_img=<0\|1> unsig_ok=<0\|1>` |
| `upd allow-unsigned on\|off` | `[cmd] upd.unsig_ok=<1\|0\|error>`; invalid argument: `[err] upd.usage=upd allow-unsigned on\|off` |

The file commands below use paths inside `/apps/` or `/assets/`. CRC-32 is a checksum used to detect damaged bytes. `fwdata` and `lapply` require raw bytes after their command header; `fread` and `lget` return raw bytes after the header. A plain text terminal is useful for inspecting them, but file transfers need a program that handles those bytes and checksums. See the firmware's sync protocol for complete transfer and error rules.

| Command and arguments | Reply format |
| --- | --- |
| `fwrite <path> <size> <crc32>` | `[cmd] fwrite.ok=<path> size=<n> chunk=<n> crc=<hex>` |
| `fwdata <off> <len> <crc32>` | `[cmd] fwdata.ok=off <o> len <n>` |
| `fwcommit` | `[cmd] fwcommit.ok=<path> size=<n> crc=<hex>` |
| `fwabort` | `[cmd] fwabort.ok` |
| `fdelete <path>` | `[cmd] fdelete.ok=<path>` |
| `flist <dir>` | `[cmd] flist.entry=<name> size=<n>` for each entry; ends with `[cmd] flist.done=<dir> entries=<n> truncated=<0\|1> max=64` |
| `fstat <path>` | `[cmd] fstat.ok=<path> size=<n> crc=<hex>` |
| `fread <path> <off> <len>` | `[cmd] fread.ok=<path> off=<o> len=<n> chunk=<n> crc=<hex>`, then raw bytes |
| `lget` | `[cmd] lget.present=<0\|1> entries=<n> schema=<n> len=<n> crc=<hex>`, then raw bytes when present |
| `lapply <len> <crc32>` | `[cmd] lapply.ok=applied <n> entries <n>` |
| `syncinfo` | `[cmd] syncinfo.fs_total=<n> fs_used=<n> fs_free=<n>`, `[cmd] syncinfo.manifest=<0\|1> entries=<n> schema=<n>`, `[cmd] syncinfo.id=<12 hex digits>`, `[cmd] syncinfo.lapply=<capability>`; ends with `[cmd] syncinfo.fw=<firmware-version>` |

## Letting a Fidget install updates over WiFi (test ring)

`upd allow-unsigned on` lets this Fidget install update images that have not been signed by Cyber Fidget. Update signing is still being developed, so for now no image is signed: until it lands, this is the switch that lets a Fidget install updates over WiFi at all, and it is meant for a small test ring. Other Fidgets show "Update it from the website for now" instead. The command can only be set through the USB cable; a network request cannot turn it on. The choice stays set across restarts and updates. Send `upd slot` to check: `unsig_ok=1` means allowed, and `unsig_ok=0` means off. Send `upd allow-unsigned off` to turn it off, then check again with `upd slot`. `upd slot` also shows the running and next-start update slots and does not change anything.

## Commands only in test builds

These commands require a firmware build with `CF_TEST_CLI`. A normal build replies `[err] unknown command: <command>` for a test-only verb. Some test commands change device state, stored settings, or power rails.

| Command and arguments | Reply format |
| --- | --- |
| `apps` | `[cmd] apps.<index>=<name>` for each compiled app |
| `app` | `[cmd] app.index=<index>`, `.name=<name>`, `.uptime_ms=<millis>` |
| `launch <name\|index>` or `launch <blob-id>` | `[cmd] launch.ok=<index>` or `[cmd] launch.ok=blob path=<path>` |
| `soak <app>` or `soak off` | `[cmd] soak=<app>` or `[cmd] soak=off` |
| `net` | `[cmd] net.mode=<mode>` and fields for that mode |
| `heapstat` | `[cmd] heapstat.free_int=<B> min_free_int=<B> largest_int=<B>` |
| `btstat` | `[cmd] btstat.controller=<state> bluedroid=<state> wifi_mode=<n> free_int=<B> min_free_int=<B> largest_int=<B>` |
| `tlsprobe [url]` | `[cmd] tlsprobe.started=1`, then `[cmd] tlsprobe.ok=<0\|1> state=<done\|failed\|timeout> err=<code> join_ms=<n> tls_ms=<n> get_ms=<n> http=<status> bytes=<n> heap_free_min=<B> largest_min=<B> heap_min_before=<B> heap_min_boot=<B> stack_size=<B> stack_hw=<B> url=<url>`; start failures use `[cmd] tlsprobe.error=<reason>` |
| `tlsalloc <psram\|internal>` | `[cmd] tlsalloc.ok=<mode> psram_free=<B>` |
| `mic` | `[cmd] mic.heap_free=...` diagnostic lines, ending with `[cmd] mic.released=1` |
| `wifi <ssid>\|<pass>` | `[cmd] wifi.saved=<ssid>` |
| `wasmstat` | `[cmd] wasmstat.*` runtime fields |
| `btn <index> press\|release\|tap` | `[cmd] btn.press=<index>`, `[cmd] btn.release=<index>`, or `[cmd] btn.tap=<index> release_in_ms=120` followed by a release |
| `sleep` | `[cmd] sleep=requested` |
| `prompt <n> [timeout_ms]` | `[cmd] prompt.open=<n> timeout_ms=<ms>`, later `[cmd] prompt.result=<index\|none>`; errors: `[err] prompt.usage=...`, `.busy=1`, or `.refused=not-menu` |
| `status` | `[cmd] status.bar=<line\|->`, `.badge=<0\|1>`, `.glyph=<state> age=<label\|-> checkin_age_s=<n\|-> cached=<0\|1>`, zero or more `.item=<kind> pri=<0-2> sticky=<0\|1> attn=<0\|1> late=<0\|1> cached=<0\|1> text=<text>`; ends with `.count=<n>` |
| `status post <kind> [late] [cached] [text]` | `[cmd] status.post=<kind> badge=<0\|1>` or `[err] status.post.refused=<kind>` |
| `status popup <kind> [late] [cached] [text]` | `[cmd] status.popup=<kind> open=1`, later `.popup.result=<accept\|ignore> kind=<kind>`; outside the menu `.popup=<kind> open=0 routed=bar` |
| `status clear [kind]` | `[cmd] status.clear=all` or `.clear=<kind> removed=<n>` |
| `status checkin <never\|seconds_ago> [cached]` | `[cmd] status.checkin=never glyph=never` or `.checkin=<seconds_ago> cached=<0\|1> glyph=<state>` |
| `rail aux on\|off` | `[cmd] rail.aux=<on\|off>` |
| `rail oled off\|on` | `[cmd] rail.oled=<off\|on> note=<note>`; after `off`, restart to restore the shared display and sensor bus |
| `gauge hibrt force\|auto` | `[cmd] gauge.hibrt=<force\|auto> hibernating=<0\|1>` |
| `gauge alert-min <V>` | `[cmd] gauge.alert_min_v=<readback-volts>` |
| `uvlo simulate <mV>` | `[cmd] uvlo.simulate=<mV> plausible=<0\|1> sleep_verdict=<shutdown\|resleep> runtime_verdict=<shutdown\|ok> sleep_threshold_mv=<mV> runtime_threshold_mv=<mV> debounce_ms=<ms>` |
| `cloud base <url>` | `[cmd] cloud.base=<ok\|error>` |
| `cloud token <credential>` | `[cmd] cloud.token=<ok\|error>`; the credential is never echoed |
| `cloud autoapply on\|off` | `[cmd] cloud.autoapply=<ok\|error>` |
| `cloud check` | Later: `[cmd] cloud.result=<ok\|none\|error> err=<code> applied=<batch\|-> offered=<fw\|-> next_ms=<n> heap_min=<B>` |
| `cloud interval <hours>` | `[cmd] cloud.interval=<ok\|error>` |
| `cloud due <hours>` | `[cmd] cloud.due=<ok\|error>` |
| `cloud guard <ms>` | `[cmd] cloud.guard=<ok\|error>` |
| `cloud press` | `[cmd] cloud.press=<ok\|error>` |
| `cloud ssid absent\|saved` | `[cmd] cloud.ssid=<absent\|saved\|error>` |
| `cloud btafterwifi allow\|block` | `[cmd] cloud.btafterwifi=<allow\|block\|error>` |
| `upd` | `[cmd] upd.key=<key> type=<str\|u8\|u32\|i32> value=<value>` per key; ends with `[cmd] upd.done=<count>` |
| `upd offer <version> [source]` | `[cmd] upd.offer=open version=<v> source=<source>` or `.offer=suppressed reason=<skipped\|not-newer\|invalid> version=<v>`; errors use `[err] upd.offer=<busy\|not-menu\|refused>` |
| `upd install <version>` | `[cmd] upd.install=restarting version=<v>` or `.install=refused reason=<unsigned\|version\|storage>` |
| `upd fault <name>` | `[cmd] upd.fault=<name\|error>` |
| `upd seen-clear` | `[cmd] upd.seen_clear=<count\|error>` |
| `link start` | `[cmd] link.code=<code>`, then `[cmd] link.state=<state>` lines; busy: `[cmd] link.state=error reason=busy` |
| `link ok\|no\|clear\|keep` | `[cmd] link.answer=<ok\|no\|clear\|keep>` |
| `link unlink` | `[cmd] link.state=unlinked` or `.state=error reason=<code>` |
| `link status` | `[cmd] link.status=linked:<yes\|no> account:<label\|-> fingerprint:<ok\|mismatch> previous:<yes\|no>` |
| `link forget` | `[cmd] link.forget=<ok\|error>` |

For the precise limits and side effects of a test command, consult the firmware's SerialCli documentation before using it. In particular, `upd fault` and `rail oled off` can deliberately interrupt normal operation.
