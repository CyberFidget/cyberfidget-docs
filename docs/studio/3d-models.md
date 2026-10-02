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

## Importing a model file

If you already have a 3D model from another program, you can bring it in instead of rebuilding it by hand. Studio reads two common 3D file types, in addition to its own `.cfmesh.json` files:

- **OBJ** (`.obj`) -- a Wavefront OBJ file, a plain-text format that lists a model's vertices and then the faces or lines that join them.
- **STL** (`.stl`) -- a triangle-list file, the format most 3D printing programs use. Both the binary and the text versions of STL work.

A *vertex* is a corner point of a 3D model; it becomes a node in Studio. A *mesh* is the whole network of vertices and faces. Most 3D programs build faces out of *triangles*, three-cornered flat patches.

!!! note "Arrives with the next website update"
    Importing OBJ and STL files is coming with the next website update. Until then, **Add from file** only opens Studio's own model files.

### How to import

1. Open the **3D** tab and expand **Project Files** in the sidebar.
2. Choose **Add from file** (next to **New model** and **Save to file**).
3. Pick your `.obj` or `.stl` file.

Studio adds the model to the open project and selects it, and the status line reads **Model added from file.** Your other models are left alone. The model is named after the file, without the `.obj` or `.stl` ending.

### What happens to the model

A wireframe model has no solid surfaces, so Studio keeps the outline and throws the rest away:

- **Faces become lines.** Each edge of each face becomes a strut, and the face itself is dropped. OBJ line (`l`) entries come in as struts directly. Colours, textures, and surface-smoothing data are ignored.
- **Hidden diagonals are removed.** Triangle-built models split every flat face into triangles, which would draw a diagonal across each one. Where two triangles lie in the same flat plane, Studio removes the line between them, so a cube made of 12 triangles comes in as the 12 lines of a cube rather than 18. A dot that you placed on purpose along a straight run is kept.
- **Duplicate points are merged.** Points at the same position (STL files store each triangle's corners separately) are joined into one node.
- **The model is centred and scaled to fit.** Studio centres it and resizes it so its longest direction fills the model grid, with every node snapped to a whole-number grid position. The original size is not kept. Nodes that land on the same grid spot after snapping are merged.

### Limits

The device can hold up to 96 nodes and 160 struts per model, and Studio checks the limits after the diagonals are removed and the points merged. If a file is over, Studio refuses it and shows one of these messages:

| Message | What it means |
|---|---|
| **This model has N dots - Cyber Fidget models max out at 96. Try a low-poly version.** | After cleanup the model still has more than 96 nodes. |
| **This model has N lines - Cyber Fidget models max out at 160. Try a low-poly version.** | After cleanup the model still has more than 160 struts. |
| **This file is N MB - Studio can only open model files up to 25 MB. Try a low-poly version.** | The file is larger than 25 MB. Studio refuses it before reading it. |
| **This model has N triangles - too detailed to bring in. Try a low-poly version.** | (STL only) The file has more than 20,000 triangles. A model that fits the device needs only a few hundred, so Studio does not try to process a huge one. |
| **This model has an unreadable part on line N. Try saving it again.** | (OBJ only) A line of the file is malformed or points at a vertex that does not exist. Re-export it from your 3D program. |
| **This file looks damaged. Try saving it again.** | (STL only) The file is truncated or its contents are invalid. |
| **This file is empty. Choose a model file.** | (STL only) The file has no content. |
| **This file is not a model Studio can open.** | (STL only) The file is text but is not an STL file. |
| **This model has no lines to import. Try a model with connected dots.** | The file has points but nothing joining them, so there is nothing to draw. |

### Tips

- **Start low-poly.** Aim for a few dozen vertices. Most 3D programs have a way to reduce detail. In Blender, add a **Decimate** modifier (*decimate* means to cut a mesh down to fewer triangles while keeping its overall shape), or choose a low-poly version of the model when you export.
- **Use simple shapes.** Models with flat faces, such as boxes, ships, and buildings, come out cleanest. Smooth curved models need many triangles to look round, so they usually go over the limit.
- **Combine meshes first.** If your scene has several separate objects, join them into one mesh before exporting, or export just the part you want.
- **If you're over the limit,** simplify in your 3D program and import again, or import a simpler version and add detail by hand with the **Add** and **Connect** tools. You can also edit an imported model like any other.
- **Keep the original.** Importing makes a copy in Studio; your OBJ or STL file is not changed.

---

## Saving and reusing models

Like drawings in the 2D panel, models keep their own version history:

- **Save version** stores a checkpoint, with an optional label.
- **History** opens the list of saved versions, each with a **Restore** option.

To reuse a model in other projects, choose **Save to My Assets** and give it a name. From then on, that model appears in the **My Assets** section of any project's 3D tab -- clicking it there copies the model in, leaving the saved original untouched.

**Rename** on a saved model's row changes its name in the library. Its saved
versions are kept, and projects that already copied it are unaffected. See
[Your Sprite Library](your-sprite-library.md) for the full rules, which apply
to models and sprites alike.

---

## Using a model in an app

Once you have a model you like, select **Try it in an app**:

- If your project has no app code yet, Studio starts you from a small example app that shows the model spinning full-screen, and switches you to the **Code** tab so you can build from there.
- If your project already has app code, Studio switches to the **Generate** tab with a request already filled in, asking to add this model to your existing app.

After you've saved a model, Studio also shows a one-line **Use in code** reference with a **Copy** button, for pasting into app code you're writing by hand.

For what to ask the App Builder for when generating an app around a 3D model, see [App Builder: generating apps with 3D models](../software/ota-builder.md#generating-apps-with-3d-models).
