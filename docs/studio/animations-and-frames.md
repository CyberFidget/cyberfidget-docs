# Animations and frames

A frame is one picture in a sequence. An animation is a named sequence of frames for an action, such as `walk` or `jump`.

On desktop and laptop, the timeline sits under the canvas and scrolls sideways. On a phone today it wraps beneath the right-panel content, after Preview, Layers and saving controls. Phone placement will change.

| Control | What it does | Shortcut | Touch equivalent |
|---|---|---|---|
| Add animation | Create a named animation group. | None | Tap Add animation and enter its name. |
| Animation Play | Loop just that group's frames. | None | Tap Play in the group header. |
| Animation Rename | Change the animation's name. | None | Tap its **...** menu, then Rename. |
| Delete animation | Remove the named group; review the dialog's choice about its frames. | None | Tap its **...** menu, then Delete animation and confirm. |
| + Frame | Copy the current frame into a new frame; within a group it adds to that animation. | None | Tap + Frame in the timeline or group header. |
| Frame thumbnail | Select the picture to edit. | Alt+Up / Alt+Down steps to previous / next frame | Tap the thumbnail. |
| Frame Duplicate | Make another copy of that frame. | None | Tap the frame's menu, then Duplicate. |
| Frame Delete | Remove that frame using its menu. | None | Tap the frame's menu, then Delete. |
| Frame reorder | Change the order of pictures in the sequence. | None | Drag a frame card to another position. |
| Previous / next frame | Step through pictures; the frame n / N readout shows position and total. | Alt+Up / Alt+Down | Tap the timeline navigation buttons. |

Use the visible frame-menu button on a phone. A long-press frame menu is not part of this increment. Separate **Go to frame** and **Duplicate Frame** controls are hidden: thumbnails and frame menus provide these operations.

## Groups and warnings

The grouped strip appears for sprites with two or more animations or the character type. One-animation sprites keep a plain frame strip. A **shared** badge means one frame belongs to more than one animation; **Unassigned** holds frames outside any group. A shared frame's menu can make an independent copy when you need to change only one animation.

Warnings identify animations the app's code expects but that have no frames. Add frames to that animation or change the code's requested name. Warnings are readouts, with no shortcut or touch command. Zero-duration frames can also cause build warnings because they would not be visible.

Set timing with [Preview and Speed](preview.md). See [Animation names](animation-states.md) for the relationship to app code.

<!-- Screenshot: named animation groups, shared badge, warning and frame menu. -->
