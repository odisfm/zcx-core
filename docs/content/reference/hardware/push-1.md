# Push 1 

## Limitations

- The touchstrip continuous input cannot be used by zcx, but will function as normal if `track` is enabled for this script in Live's MIDI preferences. The touchstrip sends an on/off message on press and release, which is available as a named control called `touchstrip`.
- The touchstrip cannot be toggled between pitchbend and modulation mode from within zcx. You must enter Live mode and press the touchstrip while holding `select`.

## Display plugin

zcx for Push 1 ships with a plugin that enables display output.
Each line of the display will be used for a specific purpose:

### encoder mappings

Displays the name of the parameter that the main encoder above it (`enc_1` - `enc_8`) is currently bound to.

### encoder values

Displays the current value of the aforementioned parameter.

### message

A reserved space, which can be written to from the [zcx user action](../../lessons/zcx-user-action.md#msg).

### ring_tracks

Displays the name of the first 8 tracks highlighted by the [session ring](../../lessons/session-ring.md)

### selected

Displays the selected track, device, and scene.
If the scene is named, the name will be shown.
If the scene is an [X-Scene](https://www.cxpman.com/manual/core-concepts/#x-scenes), the scene name (action list) will not be shown, unless there is text within the [identifier](https://www.cxpman.com/manual/core-concepts/#identifiers), e.g. an X-Scene with the name `[my cool scene] METRO` will display `my cool scene`.

---

You can specify on which line each readout appears via [preferences.yaml](../file/preferences.md#plugins).

```yaml
plugins:
  push_1_display:
    encoder_mappings: 1
    encoder_values: 2
    message: 3
    ring_tracks: 4
```

### additional options

#### prefer_track_name

```yaml
prefer_track_name: true
```

With the default of `true`, when an encoder is mapped to a track's volume fader, the [encoder mapping segment](#encoder-mappings) will display the track's name.
With `false`, the parameter will be shown as `Volume`

#### use_graphics

```yaml
use_graphics: true
```

With the default of `true`, certain mapped parameters will show a graphical representation of the parameter's value.
With `false`, you will see the normal textual representation.

## control names

### buttons

These are the names you must use in [named_controls.yaml](../../lessons/getting-started/zcx-concepts.md#named-controls-and-matrix-controls)

**Left side**

- `tap_tempo` - the button labelled `tap tempo`
- `metronome` - the button labelled `metronome`
- `undo` - the button labelled `undo`
- `delete` - the button labelled `delete`
- `double` - the button labelled `double`
- `quantize` - the button labelled `quantize`
- `fixed_length` - the button labelled `fixed length`
- `automation` - the button labelled `automation`
- `duplicate` - the button labelled `duplicate`
- `new` - the button labelled `new`
- `record` - the button with the red ⏺️ symbol
- `play` - the button with the green ▶️ symbol
- `touchstrip` - the press/release status of the touchstrip

**Surrounding display**

- `enc_1_touch` through `enc_8_touch`, `enc_master_touch`, `enc_swing_touch`, `enc_tempo_touch` - the encoders are touch sensitive and work with zcx gestures
- `select_1` through `select_8` - the top row of buttons below the display
- `state_1` through `state_8` - the bottom row of buttons below the display

**Right side**

- `master` - the button labelled `master`
- `stop` - the button labelled `stop`
- `scene_1` through `scene_8` - the scene launch buttons
- `volume` - the button labelled `volume`
- `track` - the button labelled `track`
- `device` - the button labelled `device`
- `pan_send` - the button labelled `pan & send`
- `clip` - the button labelled `clip`
- `browse` - the button labelled `browse`
- `in` - the button with the ➡️ symbol
- `out` - the button with the ⬅️ symbol
- `mute` - the button labelled `mute`
- `solo` - the button labelled `solo`
- `scales` - the button labelled `scales`
- `repeat` - the button labelled `repeat`
- `accent` - the button labelled `accent`
- `octave_up` - the button labelled `octave up`
- `octave_down` - the button labelled `octave down`
- `add_effect` - the button labelled `add effect`
- `add_track` - the button labelled `add track`
- `note` - the button labelled `note`
- `session` - the button labelled `session`
- `select` - the button labelled `select`
- `shift` - the button labelled `shift`
- `dpad_up`, `dpad_right`, `dpad_left` and `dpad_down` - the arrow buttons

### encoders

These are the names you must use in [encoders.yaml](../encoder.md)

- `enc_1` through `enc_8` - the eight encoders above the display
- `enc_master` - the encoder to the right of `enc_8`
- `tempo` - the encoder above the `undo` button
- `swing` - the encoder above the touchstrip

## Colors

The matrix and `state` buttons have [RGB](../color.md#rgb-controls) feedback.

The `scene` and `select` buttons have [BiLed](../color.md#biled-controls) feedback.

All other controls [basic](../color.md#basic-controls) feedback.
