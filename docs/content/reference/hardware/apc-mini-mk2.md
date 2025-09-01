# APC Mini mk2

## Limitations

zcx should not be used alongside the factory control surface script.
You should [disable the factory control surface](https://help.ableton.com/hc/en-us/articles/209774285-Using-Control-Surfaces) before attempting to use zcx.

## Color support

Support for [animated colors](../color.md#animated-colors) is limited with this hardware.
When defining an animated color, only the `a` value is used.

### Dim LEDs

For some reason, in the APC's default mode the LEDs are quite dim. If the default brightness is acceptable, then no action is required.

There is a workaround, but it requires the use of external software such as [Bome MIDI Translator](https://www.bome.com/products/miditranslator), [MidiPipe](https://midipipe.en.softonic.com/mac), [MidiFire](https://audeonic.com/midifire/), or others.

First, you will need to edit a hardware-specific file in your installation.
The file is `_zcx_apc_mini_mk2/hardware/specs.yaml`.

```yaml hl_lines="13"
hardware_name: Akai APC Mini mk2

global_midi_channel: 0

button_matrix:
  msg_type: note
  id_start: 0
  id_end: 63
  feedback: rgb
  momentary: true
  width: 8
  playable: false
  channel: 6
```

By adding `channel: 6` to `button_matrix`, zcx will send LED feedback on channel 7, which the APC displays at full brightness. Unfortunately, zcx will also _listen_ for MIDI on channel 7, while your hardware will still send on channel 1. This means your matrix controls won't work.

!!! warning
    When upgrading your zcx installation to a new version, your changes to any files in `hardware/` will be lost. You will have to edit this file with every upgrade.

To work around this, using your aforementioned MIDI software, create a virtual port that takes input from your APC. 
Then you will need to filter the matrix controls, and change their channel to 7 (or 6 if your software deals in zero-indexed MIDI channels). 
The matrix controls are notes 0-63 (inclusive) on channel 1. You should then output this modified MIDI data on a virtual output port.

You should consult the documentation of your chosen software for instructions on achieving the above.

Once you have a virtual port, set this port as the **Input** of your script in Live's MIDI preferences. zcx should now function as normal.

## control names

### buttons

These are the names you must use in [named_controls.yaml](../../lessons/getting-started/zcx-concepts.md#named-controls-and-matrix-controls)

- `volume` - The button labelled `volume`
- `pan` -  The button labelled `pan`
- `send` - The button labelled `send`
- `device` - The button labelled `device`
- `up` - The button with the 🔼 symbol
- `down` - The button with the 🔽 symbol
- `left` - The button with the ◀️ symbol
- `right` - The button with the ▶️ symbol
- `shift` - The button labelled `shift`
- `scene_1` through `scene_8` - The scene launch buttons

### encoders

These are the names you must use in [encoders.yaml](../encoder.md)

- `fader_1` through `fader_9` - The nine faders.