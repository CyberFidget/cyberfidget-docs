# Firmware update manifest

The website serves an **update manifest** - a JavaScript Object Notation
(JSON) document identifying one app-only firmware image for Cyber Fidget.
This page describes the response available today from
`/update/firmware.php?manifest=1`. Over-the-air (OTA) installation over
a wireless network is currently limited to Fidgets opted in over USB for
the [test ring](serial-commands.md#letting-a-fidget-install-updates-over-wifi-test-ring).
Product controls use "update"; "manifest" is the technical name for the document.

The release process attaches `firmware.bin` and `release-info.json` to a
GitHub release, and, when the release is signed, `firmware.bin.sig` and
`firmware.bin.sig.keyid` (see [Signature fields](#signature-fields)). The
website validates the assets and returns a manifest
whose `url` points back to the website's `?app=1` binary route. This is
separate from the site's older merged-image install manifest at `?parts=1`.

## Request and selection

`GET /update/firmware.php?manifest=1` selects the newest published,
non-draft stable release in the official
`CyberFidget/cyberfidget-firmware` repository. These optional query
parameters change the selection:

| Parameter | Shipped behavior |
|-----------|------------------|
| `repo=owner/name` | Select a public GitHub repository. Omit for the official repository. Other hosts and arbitrary manifest URLs are not accepted. |
| `channel=stable` or `channel=rc` | Select the stable channel by default, or allow prereleases with `rc`. The response reports the selected release's actual channel. |
| `tag=...` | Select a specific published tag. If `channel` is also supplied, it must match that release's channel. |

For a fork, `source` identifies the chosen repository. The website fetches
fork releases without its official-repository token. Fork fetches share a
budget of 20 GitHub requests per 10 minutes; exhausted requests return status
429 with `Retry-After`. A cache hit does not consume that fetch budget.

## Response fields

A successful response is JSON. The website emits every field below except
`sig` and `key_id`, which appear only for a signed release.

| Field | Type | Meaning |
|-------|------|---------|
| `version` | string | Version from `release-info.json`, required to match the selected GitHub tag without its leading `v`. |
| `size` | integer | Byte length of the app-only `firmware.bin` served by `url`. |
| `sha256` | string | Lowercase Secure Hash Algorithm 256-bit (SHA-256) digest of those exact binary bytes. |
| `url` | string | Site-relative Uniform Resource Locator (URL) under `/update/firmware.php?app=1...` for the selected app image. It carries the tag, repository, channel, release identifier, and digest. |
| `hw.min_rev` | string | Inclusive minimum board revision. |
| `hw.max_rev` | string | Inclusive maximum board revision. |
| `channel` | string | `stable` for a normal release or `rc` for a GitHub prerelease. |
| `source` | string | `official` or `fork:owner/name`, naming the selected repository. |
| `release_id` | integer | Positive GitHub release identifier. |
| `released_at` | string | GitHub publication time in Coordinated Universal Time, formatted `YYYY-MM-DDTHH:MM:SSZ`. |
| `sig` | string, optional | Digital signature of the exact `firmware.bin`, as base64 text. Present only together with `key_id`. |
| `key_id` | string, optional | Name of the key that made `sig`. Present only together with `sig`. |

`hw` is an object containing `min_rev` and `max_rev`. Board revisions use
`major.minor` decimal components, such as `1.2`; compare each component
numerically. The firmware's compatibility check treats both bounds as
inclusive and rejects malformed or inverted ranges.

## Example

The values below are **illustrative placeholders**, not a released build.
The shape and query parameters match the response constructed by the site.

```json
{
  "version": "1.2.3",
  "size": 1234567,
  "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "url": "/update/firmware.php?app=1&tag=v1.2.3&repo=CyberFidget%2Fcyberfidget-firmware&channel=stable&release_id=123456789&sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "hw": { "min_rev": "1.2", "max_rev": "1.2" },
  "channel": "stable",
  "source": "official",
  "release_id": 123456789,
  "released_at": "2026-01-01T00:00:00Z"
}
```

## Signature fields

`sig` and `key_id` are optional, but they are a pair: a manifest carries both
or neither. A manifest with neither describes an **unsigned** image.

| Field | Rules |
|-------|-------|
| `sig` | An Elliptic Curve Digital Signature Algorithm (ECDSA) signature made with a P-256 key over the SHA-256 digest of the exact `firmware.bin` bytes (what `openssl dgst -sha256 -sign` produces). The signature is in its Distinguished Encoding Rules (DER) form, 8 to 78 bytes, written as standard padded base64 text on one line: at most 104 characters, using `A-Z`, `a-z`, `0-9`, `+`, `/` and `=` padding only at the end. |
| `key_id` | 1 to 31 characters, each a lowercase letter, digit or hyphen (for example `cf-release-1`). It names which of the public keys built into the firmware should check `sig`. |

The website takes both values from two release assets published next to
`firmware.bin`:

| Release asset | Contents |
|---------------|----------|
| `firmware.bin.sig` | The `sig` text exactly: base64, no line break, at most 104 bytes. |
| `firmware.bin.sig.keyid` | The `key_id` text exactly, no line break, at most 31 bytes. |

The website checks that the base64 text is canonical, that it decodes to a
well-formed DER signature, that each asset's size equals its text length,
and that the key id matches the rules above. It does not check the signature
itself; the Fidget does. If a release has only one of the two assets, the
website refuses to answer with status 502 and **The update files are
incomplete.** If either asset breaks a rule, it answers 502 with **The update
verification files are invalid.** It never serves one field without the
other. Both assets' identifiers and update times join the cache key, so
replacing a signature asset is picked up.

What the Fidget does with them:

| Manifest | Fidget |
|----------|--------|
| Neither field | Treated as unsigned. It installs over WiFi only on a Fidget opted in over USB with `upd allow-unsigned on` (see [Serial commands](serial-commands.md#letting-a-fidget-install-updates-over-wifi-test-ring)). |
| Only one field, or a field that breaks the rules | The whole manifest is invalid. The offer is withdrawn and nothing is downloaded. |
| Both fields, `key_id` not built into this firmware | Refused, even with the USB opt-in. At a check-in the version is withdrawn rather than offered; at installation the Fidget shows **This update could not be verified. Nothing changed.** |
| Both fields, known `key_id` | The Fidget downloads the image, checks its length and SHA-256 against the manifest, then checks `sig` against that digest with the named public key, before it switches to the new image. A signature that does not match gives **This update could not be verified. Nothing changed.**; a matching one installs without the USB opt-in. |

A version refused for its signature is remembered, so it is not offered
automatically again on that Fidget. Release firmware has no official public
keys built in yet, so today every `key_id` is unknown to a release build.
Test builds (with `CF_TEST_CLI`) also know a throwaway test key,
`test-only-1`, which release builds always refuse.

## Validation and download

The release build checks `firmware.bin` against a 3,276,800-byte threshold,
leaving 65,536 bytes free in each 3,342,336-byte app slot. It writes
`release-info.json` with `version`, `flash_mode`, `app_size`, `app_sha256`,
and `hw.min_rev`/`hw.max_rev`. The website requires both release assets,
caps the binary at 3,342,336 bytes and the metadata at 65,536 bytes,
checks the downloaded image length and SHA-256 against the metadata, and
checks that the metadata version matches the selected tag. The metadata's
`flash_mode` must be quad input/output (`qio`) or dual input/output (`dio`). The cache key includes the repository,
tag, channel, release identifier, publication time, and both assets'
identifiers, update times, and sizes, plus the signature assets' identifiers
and update times when present. Re-uploading an asset under the same
tag therefore produces a different cache identity.

The website applies the slot-size cap to fork assets too; the stricter
65,536-byte release margin is a gate in the official release build, not a
separate website check. The endpoint does not check compatibility of a
fork's app interface beyond the image metadata and hardware range.

The website accepts release-asset URLs only under
`https://github.com/<selected owner>/<selected repo>/releases/download/`.
The manifest's download URL is served from the Cyber Fidget website, not
directly from GitHub. Its `release_id` and `sha256` query values bind the
download to the manifest: if the selected release or bytes change before
download, the site returns status 409 so the client can request a fresh
manifest. A tool should fetch the returned `url` from the same site, check
that the byte count equals `size`, calculate SHA-256 over the downloaded
bytes and compare it to `sha256`, and refuse an image if its device's board
revision is outside `hw.min_rev` through `hw.max_rev` or the range is
invalid. Do not install an image when any check fails.

## Planned, not yet served

The current endpoint has no arbitrary-URL manifest source and does not
provide a device linking, source acknowledgment, or update-prompt field.
Those behaviors cannot be inferred from this response. See the
[Updates guide](../software/updates.md) for the current installation choices.
