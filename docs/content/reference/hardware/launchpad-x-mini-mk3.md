# Launchpad mini mk3 / Launchpad X

## Color support

When defining [pulse colors](../color.md#animated-colors), only the `a` value is used.

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
