# Push 2

## Limitations

### Display

zcx will not make any use of Push 2's display.
However, it is possible to keep the default display function active in zcx mode.
If the preference [initial_hw_mode](../file/preferences.md#initial_hw_mode) is set to `zcx`, when zcx loads the screen will stay active.
However, if you enter Live mode, and then use Push 2's `User` button to re-enter zcx mode, the display will be disabled.
If instead, you re-enter zcx mode via the [zcx user action](../../lessons/zcx-user-action.md#hw_mode), the screen will stay active.

Because of this confusing behaviour, `initial_hw_mode` defaults to `live`.

### Other

- The touchstrip continuous input cannot be used by zcx, but will function as normal if `track` is enabled for this script in Live's MIDI preferences. The touchstrip sends an on/off message on press and release, which is available as a named control called `touchstrip`.
- The touchstrip cannot be toggled between pitchbend and modulation mode from within zcx. You must enter Live mode and press the touchstrip while holding `select`.

## control names

### buttons

These are the names you must use in [named_controls.yaml](../../lessons/getting-started/zcx-concepts.md#named-controls-and-matrix-controls)

**Left side**

- `tap_tempo` - the button labelled `tap tempo`
- `metronome` - the button labelled `metronome`
- `delete` - the button labelled `delete`
- `undo` - the button labelled `undo`
- `double` - the button labelled `double`
- `mute` - the button labelled `mute`
- `solo` - the button labelled `solo`
- `stop_clip` - the button labelled `stop clip`
- `convert` - the button labelled `convert`
- `double_loop` - the button labelled `double loop`
- `quantize` - the button labelled `quantize`
- `duplicate` - the button labelled `duplicate`
- `new` - the button labelled `new`
- `fixed_length` - the button labelled `fixed length`
- `automate` - the button labelled `automate`
- `record` - the button with the  ⏺️ symbol
- `play` - the button with the  ▶️ symbol
- `touchstrip` - the press/release status of the touchstrip

**Surrounding display**

- `enc_1_touch` through `enc_8_touch`, `enc_swing_touch`, `enc_tempo_touch`, `enc_master_touch` - the encoders at the top of Push 2 are touch sensitive and work with zcx gestures.
- `state_1` through `state_8` - the row of buttons above the display
- `select_1` through `select_8` - the row of buttons below the display

**Right side**

- `add_device` - the button labelled `add device`
- `add_track` - the button labelled `add track`
- `device` - the button labelled `device`
- `mix` - the button labelled `mix`
- `browse` - the button labelled `browse`
- `clip` - the button labelled `clip`
- `master` - the button labelled `master`
- `scene_1` through `scene_8` - the scene launch buttons
- `dpad_up`, `dpad_right`, `dpad_left` and `dpad_down` - the unlabelled arrow buttons
- `repeat` - the button labelled `repeat`
- `accent` - the button labelled `accent`
- `scales` - the button labelled `scale`
- `layout` - the button labelled `layout`
- `note` - the button labelled `note`
- `session` - the button labelled `session`
- `octave_up` - the button labelled `octave up ⌃`
- `octave_down` - the button labelled `octave ⌄`
- `page_prev` - the button labelled `page ˂`
- `page_next` - the button labelled `page ˃`

- `shift` - the button labelled `shift`
- `select` - the button labelled `select`

### encoders

These are the names you must use in [encoders.yaml](../encoder.md)

- `enc_1` through `enc_8` - the eight encoders above the display
- `enc_master` - the encoder in the top right corner
- `tempo` - the encoder above the `tap tempo` button
- `swing` - the encoder above the `metronome` button
