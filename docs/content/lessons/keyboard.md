# Keyboard view

zcx can be configured to show a rudimentary melodic keyboard, as found on controllers like the Ableton Push.

## Limitations

- Keyboard feedback is limited to the notes you are currently playing via the zcx script; you will not see feedback for notes from other sources, like a playing clip or MIDI input from other controllers or tracks.
- Keyboard feedback will not distinguish whether the played notes are being recorded, i.e., they will not be red.
- Currently, the keyboard view is not designed for Drum Rack instruments. Better support for Drum Racks is planned for a future release.
- Currently, the lowest note of the keyboard is always the tonic of the current scale. A future release will emulate the "fixed" layout seen on Push.

## Configuration

The keyboard view is actually a specialized [matrix section](getting-started/zcx-concepts.md#matrix-sections).
To configure it, add a new section called `__keyboard` to your `matrix_sections.yaml`:

```yaml title="matrix_sections.yaml"
__keyboard:
  row_start: 0
  row_end: 7
  col_start: 0
  col_end: 7
```

There is no need to create the file `matrix_sections/__keyboard.yaml`.

Once the section is created, [add it to a page](getting-started/zcx-concepts.md#pages).

### MIDI channel

Notes from the keyboard are sent on a dedicated MIDI channel.
The default channel is 10, unless specified otherwise in the [hardware reference](../reference/hardware/index.md) for your controller.

You may change this with the [preferences.yaml](../reference/file/preferences.md#playable_channel) option.

!!! warning ""
    This preference is zero-indexed: the lowest channel is 0 and the highest 15.

!!! danger ""
    The chosen MIDI channel must be completely reserved for the keyboard: if your controller has one button that sends MIDI on channel 7, then channel 7 may not be used for the keyboard.

### Custom colors

You may set custom colors via the matrix section definition:

```yaml title="matrix_sections.yaml" hl_lines="6-10"
__keyboard:
  row_start: 0
  row_end: 7
  col_start: 0
  col_end: 7
  colors:
    pressed: play_green
    in_key: white
    out_key: off
    tonic: track
```

!!! tip ""
    `track` is a keyword referring to the color of the selected track.

!!! warning ""
    You may provide [named colors](../reference/color.md#name) or [MIDI values](../reference/color.md#midi-value), but not [animated colors](../reference/color.md#animated-colors).

### Initial octave

```yaml title="matrix_sections.yaml" hl_lines="6"
__keyboard:
  row_start: 0
  row_end: 7
  col_start: 0
  col_end: 7
  octave: 3
```

Set the initial octave of the keyboard.
With the default of `3`, and in the key of C, the lowest pad will play note C-1 (MIDI note 36).

## Melodic settings

### Scale

The keyboard view follows [Live's currently selected scale](https://help.ableton.com/hc/en-us/articles/11425083250972-Keys-and-Scales-in-Live-12-FAQ).
You may set the scale with ClyphX Pro's [SCL ROOT and SCL NAME actions](https://www.cxpman.com/action-reference/global-actions/#scl-root-x).

### Octave

You may set this via the `keyboard` [command](../reference/command.md#keyboard):

#### Absolute

```yaml hl_lines="4"
gestures:
  pressed:
    keyboard:
      octave: 5
```

Or via the [zcx user action](zcx-user-action.md#kb):

```ClyphXPro
ZCX <target script> KB OCT 4
```

#### Relative

```yaml hl_lines="4-5 8-9"
gestures:
  pressed:
    keyboard:
      octave:
        up: 1
  released:
    keyboard:
      octave:
        down: 1
```

Or via the [zcx user action](zcx-user-action.md#kb):

```ClyphXPro
ZCX <target script> KB OCT <
ZCX <target script> KB OCT >
ZCX <target script> KB OCT >2
```

### In-key / chromatic

You may set this via the `keyboard` [command](../reference/command.md#keyboard):

```yaml hl_lines="4"
gestures:
  pressed:
    keyboard:
      in_key: true
```

Valid options are `true`, `false`, or `toggle`.

```ClyphXPro
ZCX <target script> KB INKEY
ZCX <target script> KB INKEY ON
ZCX <target script> KB INKEY OFF
```

### Full velocity

When enabled, all notes will be sent at velocity 127.

You may set this via the `keyboard` [command](../reference/command.md#keyboard):

```yaml hl_lines="4"
gestures:
  pressed:
    keyboard:
      full_velo: true
```

Valid options are `true`, `false`, or `toggle`.

Or via the [zcx user action](zcx-user-action.md#kb):

```ClyphXPro
ZCX <target script> KB FULLVELO
ZCX <target script> KB FULLVELO ON
ZCX <target script> KB FULLVELO OFF
```

### Note repeat

You may set this via the `keyboard` [command](../reference/command.md#keyboard):

```yaml hl_lines="4"
gestures:
  pressed:
    keyboard:
      repeat_rate: off
```

Valid options are: `ON`, `OFF`, `1/4D`, `1/4`, `1/4T`, `1/8D`, `1/8`, `1/8T`, `1/16D`, `1/16`, `1/16T`, `1/32D`, `1/32`, `1/32T`, `1/64D`, `1/64`, `1/64T`.

!!! note ""
    `ON` will activate the last repeat rate set, or `1/4` if no rate previously set.

Or via the [zcx user action](zcx-user-action.md#kb):

```ClyphXPro
ZCX <target script> KB RPT
ZCX <target script> KB RPT ON
ZCX <target script> KB RPT OFF
ZCX <target script> KB RPT 1/16
```


## keyboard control type

You may use the [keyboard control](../reference/control/keyboard.md) to get feedback about the state of the keyboard.
