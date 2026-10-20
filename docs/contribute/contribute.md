# Contribute

<div class="cf-hero" markdown>
<div class="cf-hero__media" markdown>

![An empty aluminum case front and a backplate, with the triangle pattern machined into the backplate, held in an open hand](../assets/product/case-and-backplate.webp){ width="240" height="360" }

</div>
<div class="cf-hero__text" markdown>

<p class="cf-hero__lead"><strong>The firmware and these docs are open source. Help make them better.</strong></p>

After this page you know what kinds of changes we welcome, how to write them, and where each one goes.

[Firmware on GitHub](https://github.com/cyberfidget/cyberfidget-firmware){ .md-button .md-button--primary }
[Docs on GitHub](https://github.com/cyberfidget/cyberfidget-docs){ .md-button }

</div>
</div>

We welcome pull requests (proposed changes, sent through GitHub) for:

<div class="grid cards" markdown>

-   **Docs**

    ---

    Typos, examples, screenshots. Every page of this site lives in the docs repository.

    [cyberfidget-docs](https://github.com/cyberfidget/cyberfidget-docs) | [How to Make Guides](Cyber-Fidget-Guide-Studio.md)

-   **New apps and demos**

    ---

    Apps built into the firmware, and small demos that show off one part of the device.

    [Firmware development](../firmware/index.md) | [Built-in apps](../software/apps.md)

-   **HAL improvements**

    ---

    The HAL (Hardware Abstraction Layer) is the set of functions apps use to reach the screen, buttons, sound, lights and sensors.

    [Function reference](../reference/functions.md) | [Emulator Dev Guide](emulator-dev.md)

-   **Releases and internals**

    ---

    How firmware versions are numbered and released, and how the bigger parts of the firmware work.

    [Release process](../reference/release-process.md) | [Music Player architecture](../firmware/music-player.md)

</div>

## Guidelines

- Keep the home page acronym-light; expand on first use.
- Use short sections, code blocks, and screenshots.
- Add a brief "Tested on hardware rev X" note.

---

## Repositories

All public repos are listed on the [Open Source](../product/open-source.md) page, including links and license details.

Key repos for contributors:

- [cyberfidget-firmware](https://github.com/cyberfidget/cyberfidget-firmware) -- Main firmware and WASM emulator source
- [cyberfidget-docs](https://github.com/cyberfidget/cyberfidget-docs) -- This documentation site (submit doc pull requests here)
