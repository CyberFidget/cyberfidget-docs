# Firmware update manifest

The website serves an **update manifest** - a JavaScript Object Notation
(JSON) document identifying one app-only firmware image for Cyber Fidget.
This page describes the response available today from
`/update/firmware.php?manifest=1`. Over-the-air (OTA) installation over
a wireless network is currently limited to Fidgets opted in over USB for
the [test ring](serial-commands.md#letting-a-fidget-install-updates-over-wifi-test-ring).
Product controls use "update"; "manifest" is the technical name for the document.

The release process attaches `firmware.bin` and `release-info.json` to a
GitHub release. The website validates both assets and returns a manifest
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

A successful response is JSON. All fields below are emitted by the current
website endpoint.

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
identifiers, update times, and sizes. Re-uploading an asset under the same
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
