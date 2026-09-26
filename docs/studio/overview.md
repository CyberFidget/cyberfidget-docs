# Studio Overview

Studio is where you make things for your Cyber Fidget -- apps, artwork, and 3D models. It opens at [cyberfidget.com/create/](https://cyberfidget.com/create/).

This page is a map of the surface. Each tool has its own page, linked at the bottom.

---

## Starting something

Studio opens on a landing page with one starting point: **Create an app**. Describe what you want, and the code generator builds a working first version you can run and edit straight away.

Below it, **Draw a screensaver** opens [Quick Draw](#quick-draw) if you would rather just doodle than write an app, and **Open a project file** loads a project you previously saved to your computer.

Further down, **My Stuff** lists the projects you already have. Choosing one opens it. The landing page is replaced by the workspace -- you see one or the other, never both.

---

## The workspace tabs

Once a project is open, a strip of tabs switches between the tools. On a desktop they run down the left edge; on a phone they sit along the bottom.

| Tab | What it is for |
|-----|----------------|
| **Generate** | Describe a change in plain language and have it written for you. |
| **Code** | The full editor, with the screen, buttons, lights, and sound available. |
| **2D** | Draw and animate sprites. |
| **3D** | Build wireframe models. Appears only if it is enabled for your account. |
| **Test** | Run the app in the emulator. |

**< Studio** at the top left closes the project and returns you to the landing page. Your work is saved as you go.

---

## Quick Draw

Quick Draw is a stripped-back drawing surface for making a screensaver without touching code. It gives you a brush, an eraser, and undo -- and deliberately nothing else.

You can reach it two ways:

- From the Studio landing page: **Draw a screensaver**, just below the **Create an app** card.
- Directly, at [cyberfidget.com/create/quick-draw/](https://cyberfidget.com/create/quick-draw/).

When you want more than three tools, **more tools >** carries the same drawing into the full 2D editor, where the rest of this section applies.

!!! tip "Quick Draw and the 2D panel are not the same thing"
    Quick Draw is intentionally tiny, so there is nothing to learn before you
    start drawing. The **2D** tab is the full editor -- layers, frames,
    animation states, and version history. Starting in one and moving to the
    other is the expected path, not a detour.

---

## Where your work is kept

Where a project is saved depends on whether you are signed in.

- **Signed in:** projects are saved to your account as you work, so they follow you to any computer or browser where you sign in. A copy is also kept in the browser you are using. The top bar says **saved to your account** and when; if the account save fails (for example, you are offline), it says **saved on this browser** and your work is kept there until the next save reaches your account.
- **Signed out:** projects are saved only in the browser you are using. The top bar says **saved on this browser**. They are not visible from another computer or browser, and clearing the browser's site data removes them. To keep a copy, [save the project to a file](../software/import-export.md#keep-a-whole-project).

The first time you sign in on a browser (or sign in with a different account), Studio opens the project you last worked on with that account.

If the browser holds projects you made while signed out, Studio offers to move them when you sign in: **Move N projects saved on this browser to your account? Your browser copies will stay here.** Choose **MOVE TO MY ACCOUNT** to save them to your account, or **NOT NOW** to keep them in this browser only; either way you are not asked again. Projects you have not moved stay in this browser, even while you are signed in. If some cannot be moved, Studio says so and offers **TRY AGAIN**; your work stays saved in the browser.

An account holds up to 30 projects and 10 MB in total. When it is full, saving says **Your saved projects are full.** Your account also keeps earlier versions of each project. If you work on the same project on two devices and your save replaces a newer one made on the other device, Studio says **A newer save from another device was replaced. Its version is in this project's history.**

Signing out hides your account projects in that browser; they come back when you sign in again. Deleting an account project deletes it from your account and from the browser.

Signing in also adds **My Assets**, an account-level library of sprites and models you can reuse across projects -- see [Your Sprite Library](your-sprite-library.md).

Taking something out of a library copies it into your project. Editing that copy never changes the original.

---

## Where to go next

- [Drawing and Version History](drawing-and-versions.md) -- saving checkpoints and restoring earlier work
- [Your Sprite Library](your-sprite-library.md) -- Project Files, My Assets, and Starter Sprites
- [Animation States](animation-states.md) -- giving a sprite more than one action
- [3D Models](3d-models.md) -- building and using wireframe models
