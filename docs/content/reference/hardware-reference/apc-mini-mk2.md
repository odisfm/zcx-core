# Akai APC Mini mk2

## Limitations

### Animated colors

Support for [animated colors](../color-reference.md#animated-colors) is limited with this hardware.
See [issues on GitHub](https://github.com/odisfm/zcx-core/issues?q=is%3Aissue%20state%3Aopen%20label%3Aapc_mini_mk2) for details.

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
