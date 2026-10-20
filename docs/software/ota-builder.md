# App Builder

After this page you can start a project, build it and try it in the emulator.

The App Builder is the [studio](https://cyberfidget.com/create/), a browser-based tool for writing, generating and testing Cyber Fidget apps. There is nothing for you to install.

---

## What it does

1. **Write or generate** a C++ app using the code editor or code generator.
2. **REBUILD & RUN** in the welcome panel, or **REBUILD** in the emulator panel, compiles your code and starts the app emulator, a copy of the device in your browser.
3. **Try the controls** with on-screen buttons, the slider, tilt, lights and sound.
4. **SEND TO MY FIDGET** stages the app. Open **MY FIDGET** to install your changes on a connected device. A [linked Fidget](link-your-fidget.md) can also collect changes over WiFi.

---

## Getting started

1. Go to [cyberfidget.com/create/](https://cyberfidget.com/create/) and press **+ Create an app**.
2. Choose **Code from Blank Template**, enter an App Name, and press **Create**.
3. Edit the `.cpp` file on the **CODE** tab.
4. Press **REBUILD & RUN** in the welcome panel, or **REBUILD** in the emulator panel. On a phone, use the **TEST** tab.
5. Try your app in the emulator. To install it, use **SEND TO MY FIDGET**, then **MY FIDGET**.

The [first-app guide](../getting-started/first-app.md) walks through each step. Its browser build does not require GitHub sign-in. The separate **Compile** action in the status bar is not needed for these examples.

---

## Naming your app

Your app has a name you choose and a name your code uses, and they are
allowed to be different.

**The studio asks what you want to call it before it writes any code.** The
question is part of starting an app, and generating
code waits until you have answered it. That is on purpose: the name you
choose is what your code gets called, so choosing it first saves you
hunting down a placeholder name afterwards.

Use at least one letter or number. Anything else is fair game -- spaces,
capitals, whatever reads best -- and the studio works out a sensible name for
the code from it. The dialog shows the Code Name that the studio derives from your chosen name.

**The name you choose** is the one shown at the top of the studio, on your
project card, and in the NAME box in Settings. It is also the label that
appears in the menu on your Cyber Fidget.

**To rename it, double-click the name at the top of the studio.** Type the name you want and press Enter. Press Escape, or click away, to cancel.
Renaming from the NAME box in Settings does the same thing -- the two stay
in step, and so does everywhere else the name appears.

**The name your code uses** is shown as **Code name**, under *Device menu
details* in Settings. You cannot type into it, because it is read straight
out of your app's code: whatever your code calls itself is what appears
there. To change it, change the name in your code and this follows.

Renaming your app does not rewrite your code. That is deliberate -- if you
wrote your app by hand, a rename that quietly renamed things inside
it would be editing your work without asking.

---

## When generating does not work

**A failed generate keeps your prompt.** The message offers **Retry** to send the same request again and **Copy prompt** to take the text elsewhere, so you never have to retype it.

**Drafts are kept in this browser** until a generate succeeds, so closing the tab or reloading does not lose a request you were still writing.

**An empty reply is explained.** If the model sends back no code, the studio says why when it can -- for example, the model used its whole budget thinking before it wrote anything. Try again, or pick a different model.

### Choosing a model

The studio recommends these models (a model is the code generator a provider runs; bigger ones are slower and more capable):

| Provider | Recommended models |
| --- | --- |
| Anthropic | Claude Opus 5.5, Claude Sonnet 5, Claude Haiku 4.5 |
| OpenAI | GPT-6 Astra, GPT-6 Sol, GPT-6 Luna |
| Google | Gemini 3.1 Pro, Gemini 3.8 Flash, Gemini 3.5 Flash Lite |

If you use your own provider key (an API key from Anthropic, OpenAI, or Google), **More models from your key** lists every model that key can use, fetched live from the provider, with the recommended ones first.

---

## Build, restart and send

| Action | What it does |
|--------|-------------|
| **REBUILD & RUN** / **REBUILD** | Welcome action / panel button: compiles your code, then runs it in the emulator |
| **<< RESTART** | Starts the built app again without compiling |
| **SEND TO MY FIDGET** | Adds your app to the changes waiting for your device |

Compilation turns code into a runnable app. The studio can build on your computer or use the build server, depending on its build settings and availability. When building on your computer is available, the first build downloads about 23 MB of build tools. It takes longer while the studio fetches what it needs; later builds on the computer can take a few seconds. If the computer cannot build, the studio uses its build server; allow more time. The emulator runs the result. Editing code does not change the running copy until you rebuild.

!!! warning "Keep private information out of code"
    Builds on your computer keep your code on your computer. If the studio uses the build server instead, that build is public. Keep personal information and secrets out of your code either way.

Builds sent to the build server have a daily limit. Builds done on your own computer do not count toward it.

---

## Emulator features

The browser emulator gives your app:

- **Display** - A 128 x 64 screen with the case covering about 8 pixels at each corner.
- **Buttons** - Six on-screen buttons, or keyboard shortcuts `Q/E/A/D/Z/C`.
- **Slider** - A draggable control with the same position ranges as the device.
- **LEDs** - Four lights with red, green, blue and white channels.
- **Audio** - Tones, notes and sequences; browser playback has volume and mute controls.
- **Tilt** - Mouse input on desktop, or device orientation where the browser supports it.

The emulator has no microphone input. Test microphone apps on a Cyber Fidget. The **Console** panel shows build and run messages. Studio apps cannot use `Serial.println()`; show your own diagnostic values on the app's screen. For details, see [Browser Emulator](emulator.md).

---

## App lifecycle

To light the LEDs blue while the app runs, add this fragment into the **Code from Blank Template** starter. The four arguments are red, green, blue and white brightness, from 0 to 255. Keep its button setup and cleanup, including `setColorsOff()` in `begin()` and `end()`.

```cpp
// Insert inside update(), just above display.display();
setDeterminedColorsAll(0, 0, 64, 0);
```

`begin()` runs once on opening, `update()` runs about 50 times per second, and `end()` runs on leaving. The starter already shows the screen at the end of `update()` and uses the bottom-left button to return to the menu.

See [How an App Works](../concepts/app-lifecycle.md) for the lifecycle and [Concepts](../concepts/index.md) for buttons, the screen, audio, lights, the slider and motion sensing.

---

## Generating apps with 3D models

Besides flat pixel art, the studio can generate wireframe models -- 3D shapes made of nodes and straight-line struts that spin on the display, drawn like a classic vector arcade game. See [3D Models](../studio/3d-models.md) for what a wireframe model is and how to build one by hand in the studio's 3D tab.

**What to ask for:** describe the shape as three-dimensional, rotating, or a wireframe, and the studio generates a model instead of flat art -- for example, "a spinning wireframe crystal" or "a 3D ship that flies across the screen." Ask for flat art (a character, an icon, a background) and you'll get a sprite instead.

**Spinning or facing a direction:** a generated model can turn in two ways. It can spin continuously in place, like a rotating trophy. Or its facing can follow your app's own logic -- for example, a ship that banks and turns to face the direction it's moving, the way a paper airplane leans into a turn, driven by whatever your app already tracks (steering input, velocity, and so on).

**Using a model you already built in the studio:** open the model in the [3D tab](../studio/3d-models.md#using-a-model-in-an-app) and choose **Try it in an app** -- it either starts you off with a small example app showing the model spinning, or, if your project already has app code, switches to Generate with a request already filled in to add that model to your app.

---

## See also

- [Code generator](code-generator.md) -- The optional Generate tab: make, change or explain an app from a description
- [Free use, credits and privacy](credits.md) -- What the code generator costs and what is sent where
- [3D Models](../studio/3d-models.md) -- Build wireframe models in the studio's 3D tab
- [Browser Emulator](emulator.md) -- Detailed emulator guide, controls, and troubleshooting
- [Apps](apps.md) -- Built-in app catalog and how to add your own
- [Concepts](../concepts/index.md) -- Framework reference for all hardware features
