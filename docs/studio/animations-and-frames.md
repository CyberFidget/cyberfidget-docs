# Animations and frames

A frame is one picture in a sequence. An animation is a named sequence of frames for an action, such as `walk` or `jump`.

On desktop and laptop, the timeline sits under the canvas and scrolls sideways. On a phone today it wraps beneath the right-panel content, after Preview, Layers and saving controls. Phone placement will change.

| Control | What it does | Shortcut | Touch equivalent |
|---|---|---|---|
| Add animation | Create a named animation group. | None | Tap Add animation and enter its name. |
| Animation Play | Loop just that group's frames. | None | Tap Play in the group header. |
| Animation Rename | Change the animation's name. | None | Tap its **☰** menu, then Rename. |
| Delete animation | Remove the named group; review the dialog's choice about its frames. | None | Tap its **☰** menu, then Delete animation and confirm. |
| + Frame | In a group, copy that animation's last frame into the group; in the plain strip, copy the current frame. | None | Tap + Frame in the timeline or group header. |
| Frame thumbnail | Select the picture to edit. | Alt+Up / Alt+Down steps to previous / next frame | Tap the thumbnail. |
| Frame Duplicate | Make another copy of that frame. | None | In the grouped strip, tap **☰ > Duplicate**; in the plain strip, tap the inline **Duplicate** button (available only when one animation exists). |
| Frame Delete | Remove that frame. | None | In the grouped strip, tap **☰ > Delete**; in the plain strip, tap the inline **Delete** button. |
| Previous / next frame | Step through pictures; the frame n / N readout shows position and total. | Alt+Up / Alt+Down | Tap the timeline navigation buttons. |

Animation and grouped-frame menus use **☰** buttons with accessible names beginning **Actions for ...**. On a phone, tap the visible menu button in the grouped strip or the inline buttons in the plain strip. A long-press frame menu is not part of this increment. Separate **Go to frame** and **Duplicate Frame** controls are hidden: use thumbnails to select frames and the grouped menu or inline buttons to duplicate or delete.

## Groups and warnings

The grouped strip appears for sprites with two or more animations or the character type. One-animation sprites keep a plain frame strip. A **shared** badge means one frame belongs to more than one animation; **Unassigned** holds frames outside any group. A shared frame's menu can make an independent copy when you need to change only one animation.

Warnings identify animations the app's code expects but that have no frames. Add frames to that animation or change the code's requested name. Warnings are readouts, with no shortcut or touch command. Zero-duration frames can also cause build warnings because they would not be visible.

Set timing with [Preview and Speed](preview.md). See [Animation names](animation-states.md) for the relationship to app code.

<!-- Screenshot: named animation groups, shared badge, warning and frame menu. -->
