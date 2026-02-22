---
title: APC40 mkII
---

## APC40 mk2 plugin

zcx for APC40 mk2 ships with a plugin to enhance the experience of the LED rings around the track and device knobs.
The plugin has several options, which can be configured via [preferences.yaml](../file/preferences.md#plugins).

### force_style

The LED rings can display in a few different modes:

- `single` style, where the LEDs light up in a narrow band
- `volume` style, were the LEDs light up all the way from the leftmost LED
- `pan` style, where the LEDs start from the centre of the knob
- `off`, where no LEDs light up

zcx will attempt to automatically set the relevant style based on the parameter each knob is controlling.
Alternatively, you may force each knob to use a particular style:

```yaml
plugins:
  apc_40_mk2:
    force_style:
      track_1: pan
      track_3: volume
      device_4: single
      device_8: off
```

### prefer_full_led

With this option, zcx will use the [volume style](#force_style) LED feedback instead of the `single` style.

```yaml
plugins:
  apc_40_mk2:
    prefer_full_led: true
```


## control names

### buttons

These are the names you must use in [named_controls.yaml](../../lessons/getting-started/zcx-concepts.md#named-controls-and-matrix-controls)

**Track section**:

- `stop_1` through `stop_8` and `stop_all` - the clip stop buttons
- `select_1` through `select_8` and `select_master` - the track select buttons
- `mute_1` through `mute_8` - the numbered buttons
- `cross_1` through `cross_8` - the buttons labelled `A|B`
- `solo_1` through `solo_8` - the solo buttons
- `arm_1` through `arm_8` - the arm buttons
- `scene_1` through `scene_5` - the scene launch buttons

**Transport section:**

- `pan` -  the button labelled `pan`
- `sends` - the button labelled `sends`
- `user` - the button labelled `user`
- `play` - the button labelled `play`
- `record` - the button labelled `record`
- `session` - the button labelled `session`
- `metronome` - the button labelled `metronome`
- `tap_tempo` - the button labelled `tap tempo`
- `nudge_down`, `nudge_up` - the buttons labelled `nudge -` and `nudge +`

**Device section:**

- `device_left`, `device_right` - the buttons labelled `device ←` and `device →`
- `bank_left`, `bank_right` - the buttons labelled `bank ←` and `bank →`
- `device_on` - the button labelled `dev. on/off`
- `device_lock` - the button labelled `dev. lock`
- `clip_device` - the button labelled `clip/dev. view`
- `detail` - the button labelled `detail view`
- `shift` - the button labelled `shift`
- `bank_lock` - the button labelled `bank`
- `dpad_up`, `dpad_right`, `dpad_down`, `dpad_left` - the directional buttons labelled `bank select`

### encoders

These are the names you must use in [encoders.yaml](../encoder.md)

- `fader_1` through `fader_9` - The nine faders
- `track_1` through `track_8` - The eight encoders above the faders
- `device_1` through `device_8` - The eight encoders to the right
- `tempo` - the knob labelled `tempo`
- `cue` - the knob labelled `cue`
- `crossfader` - the crossfader
