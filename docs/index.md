# Cyber Fidget Docs

**Cyber Fidget is a pocket-sized aluminum gadget with a screen, buttons, lights, a speaker and a slider that you can play with, and program to do new things.**

<video src="assets/media/emulator-catcher.webm" poster="assets/media/emulator-catcher.png" autoplay loop muted playsinline width="240"></video>

*A small game made in the browser, running in the emulator (an on-screen copy of the device). The slider moves the paddle; catch the dots.*

## Where do you want to start?

<div class="grid cards cf-doors" markdown>

-   **New here? See what it is**

    ---

    What it is, what's inside, and what it can do, in a few minutes.

    [Product overview](product/overview.md) | [Explore what it can do](getting-started/explore.md)

-   **Got a kit? Put it together and turn it on**

    ---

    About 15 minutes with a small screwdriver. Then find your way around the built-in apps.

    [Assembly guide](getting-started/assembly/guide.md) | [Turn it on](getting-started/overview.md#2-turn-it-on-and-find-your-way-around) | [Built-in apps](software/apps.md)

-   **Make your first app**

    ---

    Write code in your browser and watch it run. Nothing to install, no device needed until the last step.

    [Build your first app](getting-started/first-app.md) | [Make a game, step by step](getting-started/make-a-game.md) | [Function reference](reference/functions.md)

-   **Make art for apps**

    ---

    Draw sprites (small pictures for characters and objects), animate them, or build 3D models, in the studio on cyberfidget.com.

    [Studio overview](studio/overview.md) | [Animations](studio/animations-and-frames.md) | [3D models](studio/3d-models.md) | [Import Aseprite art](software/import-export.md)

-   **Teaching or building with kids?**

    ---

    The browser path needs no installs and no device, and the tutorials say up front what you will be able to do. A teacher guide is not available.

    [Build your first app](getting-started/first-app.md) | [Explore what it can do](getting-started/explore.md) | [Contact us](https://cyberfidget.com/contact.php)

-   **Help build Cyber Fidget**

    ---

    The firmware and these docs are open source. Fix a page, add an example, or work on the firmware.

    [Contribute](contribute/contribute.md) | [Open source and licenses](product/open-source.md) | [Firmware development](firmware/index.md)

</div>

## What's on this site

Every tab at the top, in one line each:

- **[Product](product/overview.md)**: what Cyber Fidget is, battery and charging, accessories, open-source licenses.
- **[Getting started](getting-started/overview.md)**: assemble it, explore what it can do, build your first app, make a game step by step.
- **[Make apps](concepts/index.md)**: one page per part (screen, buttons, sound, lights, slider, motion, sprites, 3D models), plus the function reference and the emulator.
- **[Your Fidget](software/apps.md)**: built-in apps, voice notes, phone companion, keeping and sharing your work, updates, linking your Fidget to your account.
- **[Hardware](hardware/specs.md)**: specs, part numbers and the pinout (which chip pin does what).
- **[Studio](studio/overview.md)**: the drawing, animation and 3D tools on cyberfidget.com.
- **[Reference](reference/glossary.md)**: the glossary of terms and the commands you can send over a USB cable.
- **[Contributors](contribute/contribute.md)**: how to help, firmware internals, releases.

Hover over an underlined term, such as OLED or LED, to see what it means, or open the [Glossary](reference/glossary.md).

## Quick links

- **Buy / Pre-order:** [cyberfidget.com/buy.html](https://cyberfidget.com/buy.html)
- **Main site:** [cyberfidget.com](https://cyberfidget.com)
- **The studio (make apps and art):** [cyberfidget.com/create/](https://cyberfidget.com/create/)
- **Firmware updates:** [cyberfidget.com/update/](https://cyberfidget.com/update/)
- **Contact:** [cyberfidget.com/contact.php](https://cyberfidget.com/contact.php)

## At a glance

A machined-aluminum, pocket-sized gadget built for play, tinkering, and experimentation. Designed and assembled in Michigan.

It ships as a kit: no soldering, just screws. 2.2 x 1.6 x 0.8 in, about 68 g. Inside: an ESP32 chip with Wi-Fi and Bluetooth, a 0.96" OLED screen, 6 buttons, a slider, 4 RGBW LEDs, a speaker, a microphone, a motion sensor, a microSD card slot, and USB-C.

See the [Product overview](product/overview.md) for the full picture, or [Hardware specs](hardware/specs.md) for part numbers and dimensions.

!!! success "No device? No problem."
    You can run real Cyber Fidget apps in your browser. Write or generate an app in the [studio](https://cyberfidget.com/create/), press **REBUILD & RUN** in the welcome panel (or **REBUILD** in the emulator panel), and it runs in an on-screen emulator with the same buttons, slider, screen and lights. See the [Browser Emulator](software/emulator.md) guide.

!!! note "Want to work on the firmware itself?"
    Most people never need this. The [Arduino route](getting-started/first-flash-arduino.md) installs firmware from your own toolchain, and the [firmware on GitHub](https://github.com/cyberfidget/cyberfidget-firmware) has the full source, the app functions and the emulator.
