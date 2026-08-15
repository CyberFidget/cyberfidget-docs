# Keeping and sharing your work

When you choose **Add from file** for a sprite or model, Studio adds the file to the project you already have open and selects it. It never replaces or overwrites the asset you were working on.

Studio can save either one asset or a whole project to a file on your computer. Use these files to keep a backup, move work to another computer, send work to someone else, or bring someone else's work into Studio.

The files use JavaScript Object Notation (JSON), a structured text format for storing data. Each Studio file has a more specific filename ending so Studio can identify what it contains.

---

## Keep one sprite or model

Save one asset when you want to keep or share that sprite or model without the rest of the project.

In the 2D workspace, **Save to file** and **Add from file** sit together in the **Sprite file** group. There is a second **Add from file** button in the project file list, next to **New sprite**, so you can bring a sprite in from wherever you are working. Saving names the file after the sprite and gives it the `.cfsprite.json` ending.

In the 3D workspace, **Save to file** and **Add from file** are next to the **New model** control. Saving names the file after the model and gives it the `.cfmesh.json` ending.

Either **Add from file** button does the same thing: Studio adds the sprite or model to the open project and selects it, and the asset you were working on stays in the project unchanged.

Author and licence information in the file stays exactly as it was. If the file does not contain that information, Studio leaves the fields blank for you to fill in instead of guessing.

---

## Keep a whole project

Save the whole project when you want a complete backup or want to continue the same app on another computer.

Open **App Settings** and choose **Save project to file**. Studio writes one `.cfapp.json` file containing the project's code, sprites, models, captures, and settings.

If the project has been built, the built app travels inside the project file so it can run immediately after opening. If that built copy is no longer available, Studio saves the project without it and tells you. Open the file and build the app again.

Studio refuses to save a very large project into a file that the browser would struggle to reopen.

---

## Open a whole project

Go to the **Create** launcher and choose **Open a project file** beside the list of projects. Opening a project file is how you start from that file, so this control is on the launcher rather than inside the editor.

Studio always creates a new project alongside the projects you already have. It never replaces an existing project.

---

## What survives, and what can be missing

- A sprite or model keeps the author and licence information stored in its file. Missing information remains blank.
- A whole-project file keeps the code, sprites, models, captures, and settings.
- A built app is included when its built copy is available. If it is unavailable, the rest of the project is still saved, and you must build the app again after opening it.
- A damaged sprite or model file, or one made by a newer version of Studio, is refused with a plain explanation. Nothing in the open project changes.

---

## Files and the Cyber Fidget

You cannot pull files back off a Cyber Fidget in the browser. Work travels onto the device, but retrieving it is not available.

Do not copy `.cfsprite.json` or `.cfmesh.json` files onto the device. Studio builds a project's art into the app itself, and installing the app carries its art with it.

Apps live in the device's internal storage, and the companion page is built into its firmware. The memory card holds music, voice recordings, the companion's speech-recognition payload, and any optional companion page override. It does not hold apps, and apps do not load their art from it.
