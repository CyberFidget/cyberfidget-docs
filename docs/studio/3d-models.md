# 3D Models

The 3D tab is Studio's tool for building wireframe models -- simple 3D shapes your app can spin and display on the Cyber Fidget's OLED screen, drawn as glowing line art like a classic vector arcade game.

!!! note "Early access"
    The 3D tab is a new feature we're still testing. It only appears in the tool rail for accounts we've turned it on for, and there's currently no self-service way to request it -- unlike the [Beta Access](../software/beta-access.md) features (firmware editing, compiling, and installing), which you can request from your account menu. If you don't see a **3D** button next to **Code** and **2D**, it isn't enabled for your account yet.

---

## What is a wireframe model?

A wireframe model is a 3D shape made of **nodes** (points positioned in space) connected by **struts** (straight lines between two nodes). There are no solid surfaces -- only the points and the lines between them. That's what lets the shape spin cleanly on a monochrome display: the device draws the struts as it would any other line, from whatever angle the model is currently facing.

---

## Opening the 3D tab

Click **3D** in Studio's tool rail (alongside **Generate**, **Code**, and **2D**) to open the model workspace. The sidebar offers three ways to start:

- **Project Files** -- every model already in this project, plus a **New model** button.
- **My Assets** -- your account's saved models. Sign in to use this; it's shared with your sprite library, holding up to 50 assets total between the two.
- **Starter Models** -- three ready-made shapes (**SHIP**, **CUBE**, **PYRAMID**) to reshape instead of starting from nothing.

---

## Editing a model

The model stage in the middle of the workspace is an interactive 3D view. Three tools sit above it:

- **Move** -- drag empty space to orbit around the model; drag a node to reshape it (its position updates the moment you release); scroll to zoom the view in or out; click a strut to select it.
- **Connect** -- click one node, then another, to draw a strut between them (or remove one that's already there). Press Esc to cancel a pending connection.
- **Add** -- click empty space to place a new node; click an existing strut to split it, inserting a fresh node at its midpoint.

A **Mirror** toggle keeps the model symmetric left-to-right. With Mirror on, editing a node or strut on one side updates its mirrored twin on the other side of the center line automatically -- handy for anything meant to look the same from both sides, like a ship or a face.

**Undo** and **Redo** buttons step back and forward through your edits (also available as Ctrl+Z, Ctrl+Shift+Z, and Ctrl+Y). Delete or Backspace removes whichever node or strut is currently selected.

A model can hold up to 96 nodes and 160 struts. The Model Stats panel shows your current counts against those limits, along with the model's approximate size in bytes once installed on the device.

---

## The live preview

Next to the editor, the **Preview - Device True** panel renders your model using the same math the device itself uses to draw it, so what you see in Studio is what your Cyber Fidget will show. A **Spin** toggle turns continuous rotation on or off, and a **Zoom** slider adjusts how large the preview appears.

---

## Saving and reusing models

Like drawings in the 2D panel, models keep their own version history:

- **Save version** stores a checkpoint, with an optional label.
- **History** opens the list of saved versions, each with a **Restore** option.

To reuse a model in other projects, choose **Save to My Assets** and give it a name. From then on, that model appears in the **My Assets** section of any project's 3D tab -- clicking it there copies the model in, leaving the saved original untouched.

---

## Using a model in an app

Once you have a model you like, select **Try it in an app**:

- If your project has no app code yet, Studio starts you from a small example app that shows the model spinning full-screen, and switches you to the **Code** tab so you can build from there.
- If your project already has app code, Studio switches to the **Generate** tab with a request already filled in, asking to add this model to your existing app.

After you've saved a model, Studio also shows a one-line **Use in code** reference with a **Copy** button, for pasting into app code you're writing by hand.

For what to ask the App Builder for when generating an app around a 3D model, see [App Builder: generating apps with 3D models](../software/ota-builder.md#generating-apps-with-3d-models).
