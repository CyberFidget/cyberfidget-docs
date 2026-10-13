# Animations and frames

A frame is one picture in a sequence. An animation is a named sequence of frames for an action, such as `walk` or `jump`.

On desktop and laptop, the timeline sits under the canvas and scrolls sideways. On a phone it wraps beneath the right-panel content, after Preview, Layers and saving controls.

| Control | What it does | Shortcut | Touch equivalent |
|---|---|---|---|
| Add animation | Create a named animation. | None | Tap Add animation, type a name in the **Animation name** field, then tap **Create**. |
| Animation Play | Loop just that group's frames. | None | Tap Play in the group header. |
| Animation Rename | Change the animation's name. | None | Tap its **☰** menu, then Rename. |
| Delete animation | Remove the named animation. A dialog asks you to confirm; deleting an animation does not delete its frames. Frames used only by that animation move to **Unassigned**, or back to the single row if it was the last animation. | None | Tap its **☰** menu, then **Delete animation**, then **Delete animation** again in the dialog (or **Cancel**). |
| + Frame | In an animation group, copy that animation's last frame into the group; in a timeline without animation headers, copy the current frame. | None | Tap + Frame in the timeline or group header. |
| Frame thumbnail | Select the picture to edit. | Alt+Up / Alt+Down steps to previous / next frame | Tap the thumbnail. |
| Frame Duplicate | Make another copy of that frame. | None | In a timeline with animation groups, tap **☰ > Duplicate** on a frame inside an animation (an **Unassigned** frame has no Duplicate; add it to an animation first). In a timeline without animation headers, tap **+ Frame**, which copies the current frame. |
| Frame Delete | Remove that frame from the sprite and from every animation that uses it. This can leave an animation with no frames. | None | In a timeline with animation groups, tap **☰ > Delete**; in a timeline without animation headers, tap the inline **Delete** button. |
| Remove from this animation | Take the frame out of that animation without deleting it. The last frame in an animation cannot be removed this way; use **Delete** to remove a frame completely. A sprite always keeps at least one frame, so **Delete** has no effect on its only frame. | None | Tap the frame's **☰** menu, then **Remove from this animation**. |
| Add to animation... | Add the frame to another animation. This item appears when there is another animation the frame could join, including for an **Unassigned** frame when at least one animation exists. | None | Tap the frame's **☰** menu, then **Add to animation...**, then choose the animation. |
| Make independent | On a frame with a **shared** badge, make a separate copy for this animation so changes to it do not affect the other animations. | None | Tap the frame's **☰** menu, then **Make independent**. |
| Rename a frame | Change the frame's name. | None | Double-click the frame name, or double-tap it on a touch screen. |
| Previous / next frame | Step through pictures; the frame n / N readout shows position and total. | Alt+Up / Alt+Down | Tap the timeline navigation buttons. |

Animation and frame menus use **☰** buttons; a screen reader announces each one as **Actions for ...** followed by the name. On a phone, tap the visible menu button in a timeline with animation groups, or the inline **Delete** buttons in a timeline without animation headers. Use thumbnails to select frames, and the frame menu, **+ Frame** or the inline buttons to duplicate or delete them.

## Groups and warnings

The timeline has two layouts. With animation groups, each animation has a header (its name, **Play**, **+ Frame** and a **☰** menu) with its frames beneath, and every frame has a **☰** menu. Without them, the timeline is one row of frames with an inline **Delete** button on each and no animation headers. Creating an animation switches to groups, and character sprites use groups whenever they have an animation. Deleting the last animation returns to the single row and keeps its frames there; when other animations remain, frames used only by the deleted animation move to **Unassigned**. A **shared** badge means one frame belongs to more than one animation; **Unassigned** holds frames outside any animation. A shared frame's menu offers **Make independent** when you need to change only one animation.

Warnings identify animations the app's code expects but that have no frames. Add frames to that animation or change the code's requested name. Warnings are readouts, with no shortcut or touch command. In an animation with more than one frame, a zero-duration frame also causes a warning when you build the app (Studio's step that turns your project, including its art, into a runnable app), because it would not be visible.

Set timing with [Preview and Speed](preview.md). See [Animation names](animation-states.md) for the relationship to app code.

<!-- Screenshot: named animation groups, shared badge, warning and frame menu. -->
