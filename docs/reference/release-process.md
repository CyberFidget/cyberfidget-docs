# How Cyber Fidget firmware releases work

This page explains the project's versioning philosophy and release flow
-- useful if you're a contributor (so you know what's expected of you, or
not), a user choosing which firmware to install, or someone trying to
understand why a binary you have reports a particular version.

For the firmware-side technical reference (banner format, serial CLI,
runtime APIs), see [Firmware version](firmware-version.md).

## Versioning philosophy

### Semantic versioning, decided by humans

Cyber Fidget firmware uses [SemVer 2.0.0](https://semver.org/) and the
release manager makes the bump decision (major / minor / patch) by hand
based on the actual semantic impact of changes since the last release.
There's no commit-message-driven auto-bump (yet).

**Why this matters to you**:

- If you're an **app author** writing apps for The Archives: the
  `min_firmware: 1.4.2` field on your app pins against a real semver
  contract. A `1.4.x` device will run any app that requires `>=1.4.0`;
  a `1.3.x` device won't.
- If you're a **firmware contributor**: you don't need to think about
  versioning when opening a PR. Just describe the impact in your PR
  description (bug fix? feature? breaking change?) and the release
  manager will fold that into the next bump decision.
- If you're an **end user**: the version number you see on your device
  means something specific. `1.4.2 → 1.4.3` is a patch (bug fixes); `1.4
  → 1.5` is a minor (new features, backward-compatible); `1.x → 2.0` is
  a major (breaking changes).

### Bump-on-release, not bump-per-commit

The version number embedded in the firmware advances **only when a
release is cut**. Between releases, dev/CI builds report the upcoming
release version with a `+commit-hash` suffix that uniquely identifies
the build:

- A clean release: `1.2.0+abc1234`
- A CI build of someone's PR after the 1.2.0 release: `1.2.1+def5678`
  (the version has been pre-bumped to the next-patch target so dev
  builds advertise where they're heading)
- A local dirty build: `1.2.1+abc1234.dirty`

This is the firmware-industry default -- it matches how ESP-IDF, Arduino,
Raspberry Pi firmware, and Postgres all version themselves. Versions
mean something; commit hashes uniquely identify what was actually built.

## Release tiers

In order of significance (and audience):

| Tier | Tag shape | Audience | When to use it |
|------|-----------|----------|----------------|
| **Stable** *(also called "GA" or "General Availability" in enterprise contexts)* | `v1.2.0` | Everyone (default channel) | "Confident this is ready" |
| **Release Candidate (RC)** | `v1.2.0-rc1`, `-rc2` | Bleeding-edge opt-in users | "Feature-complete, want eyes before promoting to Stable" |
| **Beta** | `v1.2.0-beta`, `-beta.2` | Wider tester pool | "Feature-mostly-complete, may still tweak" |
| **Alpha** | `v1.2.0-alpha`, `-alpha.2` | Internal / insiders | "Early; expect churn" |

The default release channel is **Stable only**. You'll see Stable
releases on the GitHub Releases page without any special opt-in. RCs
and below are marked as "Pre-release" by GitHub and are intended for
users who explicitly want to test upcoming features and report issues.

Below RC sit non-release builds (nightly, CI, local dev) -- those are
internal development scaffolding and aren't normally distributed. See
the [build-types section in the firmware-version reference](firmware-version.md#build-types)
for what these mean in serial output.

## Where releases live

- **Stable + Pre-release artifacts**: GitHub Releases page on the firmware repo
  ([github.com/CyberFidget/cyberfidget-firmware/releases](https://github.com/CyberFidget/cyberfidget-firmware/releases))
- **Latest Stable** is the release at the top with no "Pre-release" tag
- **To opt into prereleases**: scroll past the top Stable release; RCs
  and betas appear immediately below, marked with a yellow "Pre-release"
  badge
- **App Builder firmware selector** (when implemented per T-003): defaults
  to "Latest Stable" with a checkbox for "Include pre-release builds"

## For contributors: what you need to do (and what you don't)

If you're submitting a PR to the firmware repo:

**Don't**:
- Don't edit `version.txt`. The release manager owns it; touching it in
  a PR will get pushback during review.
- Don't push tags. Tag creation is release-manager territory.
- Don't worry about which version your PR will land in. The release
  manager folds it into whichever release happens next.

**Do**:
- Note your change's semver impact in the PR description (bug fix /
  feature / breaking). The release manager uses this when deciding the
  next bump.
- Test against a CI build of your own PR. Every commit you push to a PR
  branch triggers a CI build with a unique identifying string --
  something like `fw=1.2.1+yourhash type=ci-dev`. Flash that build, see
  the matching banner on the device, run your tests. The build summary
  printed during compile and the device's boot banner will report the
  same string character-for-character; if they don't match, something's
  wrong (stale cache, wrong serial port, partial flash) -- investigate
  before continuing.

That's the whole contributor flow. You never touch the release machinery.

## For release managers: how releases get cut

Two paths exist, both supported. Use whichever you prefer.

### Path A - manual via `git tag`

```bash
# Bump version
$EDITOR cyberfidget-firmware/version.txt    # 1.1.0 → 1.2.0
git add cyberfidget-firmware/version.txt
git commit -m "chore(release): bump to 1.2.0"
git push origin main

# Tag and push
git tag v1.2.0           # or v1.2.0-rc1 for an RC
git push origin v1.2.0   # ditto

# CI does the rest (build → release artifact attached to GitHub Release)

# (For Stable only) post-release bump so dev builds advertise the upcoming version
$EDITOR cyberfidget-firmware/version.txt    # 1.2.0 → 1.2.1
git add cyberfidget-firmware/version.txt
git commit -m "chore: post-release bump to 1.2.1"
git push origin main
```

CI asserts that the tag matches `version.txt` before doing any compile
work. If they disagree, the build aborts with a clear error in ~1 second.

### Path B - workflow_dispatch (when implemented per T-005)

Instead of typing commands:

1. Open [github.com/CyberFidget/cyberfidget-firmware/actions](https://github.com/CyberFidget/cyberfidget-firmware/actions)
2. Click "Release (interactive)" in the left sidebar
3. Click "Run workflow"
4. Fill in:
   - **Version**: `1.2.0`
   - **Prerelease**: `release` (for Stable), or `rc` / `alpha` / `beta`
   - **Iteration**: leave empty for auto-pick (e.g., next `rc<N>`), or specify
   - **Post-release bump**: `patch` (default) / `minor` / `major` / `skip`
5. Click "Run workflow"

The workflow does the version.txt bump, commit, tag creation, tag push,
build, release artifact upload, and (for Stable) post-release bump -- all in
one shot. Manual `git tag` from Path A continues to work in parallel.

## Why we chose these specific workflows

A few decisions worth making explicit:

- **Human-managed semver, not auto-increment**: firmware versions are a
  contract that user-apps depend on. Contracts need human judgment about
  what's breaking. We can revisit Conventional-Commits-driven automation
  later if contributor count grows enough to make commit-message
  discipline pay off.
- **Bump-on-release, not bump-per-commit**: shipped firmware is a
  contract; thousands of "versions" with no semantic meaning would be
  noise. Commit hashes already disambiguate dev builds.
- **Stable gets a post-release bump; RC doesn't**: an RC series
  iterates toward a single Stable target, so version.txt stays put
  through `rc1`, `rc2`, `rc3`. After Stable ships, advancing
  version.txt keeps subsequent dev builds from advertising the
  just-shipped version.
- **Both manual and workflow-dispatch release paths**: optionality has
  near-zero cost. Manual is faster for emergency hotfixes; workflow-
  dispatch is friendlier for the standard ritual and harder to forget
  the post-release bump.
- **Default release channel is Stable-only**: most users want stability.
  RC/beta/alpha exist but are opt-in.
- **Downgrade is supported**: if you flash an older firmware over a
  newer one, the device wipes settings and proceeds. We don't refuse
  downgrades -- sometimes you want to roll back.

## See also

- [Firmware version reference](firmware-version.md) - banner format,
  serial CLI commands, runtime APIs, FAQ for common gotchas
- [Open Source](../product/open-source.md) - repository links and
  licenses
