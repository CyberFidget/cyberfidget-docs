# 3D Models

The 3D tab is Studio's tool for building wireframe models -- simple 3D shapes your app can spin and display on the Cyber Fidget's OLED screen, drawn as glowing line art like a classic vector arcade game.

!!! note "Early access"
    The 3D tab is a new feature we're still testing. It only appears in the tab strip for accounts we've turned it on for, and there's currently no self-service way to request it -- unlike the [Beta Access](../software/beta-access.md) features (firmware editing, compiling, and installing), which you can request from your account menu. If you don't see a **3D** button next to **Code** and **2D**, it isn't enabled for your account yet.

---

## What is a wireframe model?

A wireframe model is a 3D shape made of **points** (also called nodes, positioned in space) connected by **lines** (also called struts, straight lines between two points). There are no solid surfaces -- only the points and the lines between them. That's what lets the shape spin cleanly on a monochrome display: the device draws the lines as it would any other line, from whatever angle the model is currently facing.

---

## Opening the 3D tab

Click **3D** in Studio's tab strip (alongside **Generate**, **Code**, and **2D**) to open the model workspace. On a desktop or laptop, models use the same two buttons above the workspace as sprites do: **All files** and **Add art**. See [Your Sprite Library](your-sprite-library.md) for how they work. For models:

- **Add art > Build a 3D model** asks for a **Model name** and starts a blank model. **Add art > Import from a file** brings in a `.cfmesh.json`, `.obj` or `.stl` file.
- **All files > In this project** lists every model already in this project, under the heading **3D models**.
- **All files > My library** holds your account's saved models, under the heading **My Assets**. Sign in to use this; it's shared with your sprite library, holding up to 50 assets total between the two.
- **All files > Free starters** has a **Starter Models** section with three ready-made shapes (**SHIP**, **CUBE**, **PYRAMID**) to reshape instead of starting from nothing. Click one to add it to the project.

---

## Editing a model

The model stage in the middle of the workspace is an interactive 3D view. Three tools sit in the tool column to its left:

- **Move** -- drag the model to spin it; drag a point to reshape it; scroll to zoom the view in or out; click a line to select it.
- **Connect** -- click one point, then another, to draw a line between them (or remove one that's already there). Press Esc to cancel a pending connection.
- **Add point** -- click empty space to place a new point; click an existing line to split it, inserting a fresh point at its midpoint.

A **Mirror** toggle (it reads **Mirror: on** or **Mirror: off**) keeps the model symmetric left-to-right. With Mirror on, editing a point or line on one side updates its mirrored twin on the other side of the center line automatically -- handy for anything meant to look the same from both sides, like a ship or a face.

**Undo** and **Redo** buttons step back and forward through your edits (also available as Ctrl+Z, Ctrl+Shift+Z, and Ctrl+Y). Delete or Backspace, or the **Delete selection** button, removes whichever point or line is currently selected.

A model can hold up to 96 points and 160 lines. The **Model details** panel shows your current counts against those limits, along with the model's approximate size in bytes once installed on the device.

---

## The live preview

Next to the editor, the **Preview** panel (marked **live**) renders your model using the same math the device itself uses to draw it, so what you see in Studio is what your Cyber Fidget will show. A **Spin** toggle turns continuous rotation on or off, and a **Zoom** slider adjusts how large the preview appears.

---

## Saving and reusing models

Like drawings in the 2D panel, models keep their own version history:

- **Save version** stores a checkpoint, with an optional label.
- **History** opens the list of saved versions, each with a **Restore** option.

To reuse a model in other projects, choose **Save to My Assets** and give it a name. From then on, that model appears in **All files > My library** in any project -- clicking it there copies the model in, leaving the saved original untouched.

**Rename** on a saved model's card changes its name in the library. Its saved
versions are kept, and projects that already copied it are unaffected. See
[Your Sprite Library](your-sprite-library.md) for the full rules, which apply
to models and sprites alike.

---

## Using a model in an app

Once you have a model you like, select **Try it in an app**:

- If your project has no app code yet, Studio starts you from a small example app that shows the model spinning full-screen, switches you to the **Code** tab, and builds it so you can run it.
- If your project already has app code, Studio switches to the **Generate** tab with a request already filled in, asking to add this model to your existing app.

After you've saved a model, Studio also shows a one-line **Use in code** reference with a **Copy** button, for pasting into app code you're writing by hand.

For what to ask the App Builder for when generating an app around a 3D model, see [App Builder: generating apps with 3D models](../software/ota-builder.md#generating-apps-with-3d-models).
