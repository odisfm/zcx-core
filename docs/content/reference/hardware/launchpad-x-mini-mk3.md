---
title: Launchpad X / Launchpad Mini mk3
---

## Setup notes

- In Live's MIDI settings, `Launchpad (MIDI Out/In)` should be selected as the Input/Output of the zcx script.
- it is possible to use the factory Launchpad script alongside zcx, and change between the scripts by using the [zcx user action](../../lessons/zcx-user-action.md#hw_mode).
  - After changing to zcx mode, it may be necessary to [refresh](../../lessons/zcx-user-action.md#refresh) the script's feedback.
- If you are using Launchpad custom modes alongside zcx, the custom mode controls should not use MIDI channel 1.

## Color support

When defining [pulse colors](../color.md#animated-colors), only the `a` value is used.

Only one speed is supported for animated colors, so any `speed` option will be ignored.

## control names

### buttons

These are the names you must use in [named_controls.yaml](../../lessons/getting-started/zcx-concepts.md#named-controls-and-matrix-controls)

- `nav_up` - the button with the 🔼 symbol
- `nav_down` - the button with the 🔽 symbol
- `nav_left` - the button with the ◀️ symbol
- `nav_right` - the button with the ▶️ symbol
- `scene_1` - through `scene_8` - the scene launch buttons
  - `novation` - the illuminated Novation logo in the top right corner. It's not actually a button, so won't respond to gestures, but apart from that it can be treated like any other control to display feedback.
- `session` - the button labelled `session`

**Launchpad mini mk3 only:**

- `drums` - the button labelled `drums`
- `keys` - the button labelled `keys`
- `user` - the button labelled `user`

**Launchpad X only:**

- `note` - the button labelled `note`
- `custom` - the button labelled `custom`
- `capture` - the button labelled `capture MIDI`
