---
weight: -8
---
# param control

The `param` control binds to a device parameter, mixer parameter, or other special function, and displays feedback about the state of its target.
This feature aims to emulate the Button Bindings feature from the [ClyphX Pro Bindings](https://www.cxpman.com/manual/optional-accessories/#clyphx-pro-bindings) optional accessory.

Param controls can be bound to [all the targets that encoders can](../encoder.md#mapping-targets), as well as [some others](#additional-mapping-targets).

## behaviour

The param control displays [different colors](#on_color-off_color) based on whether its target is considered "on" or "off".
For binary targets like [arm](#arm), this is straightforward.
For [adjustable properties](https://www.cxpman.com/manual/general-action-information/#adjustable-properties), like a track's volume, the parameter is considered "off" if the parameter is at its **minimum** value, and "on" for any other value.
You can tweak this behaviour by setting a [midpoint](#midpoint).

Without defining any [gestures](../command.md#gestures), the param control will toggle its mapped parameter from "on" to "off" on a press.
Binary targets will have their status inverted.
For adjustable properties, a parameter currently at its minimum value will be set to its maximum, and a parameter at any value above its minimum is set to its minimum.

You can modify this behaviour via the [toggle_param](#toggle_param) option.
Any defined gestures will be executed as normal.

## yaml schema

Inherits from [standard control](standard.md#yaml-schema).

```yaml
binding: binding definition
on_color: color definition
off_color: color definition
disabled_color: color definition
toggle_param: true | false | "momentary"
midpoint: number
# color: not implemented
```

### binding
`binding definition`

Follows the same format as [encoder mapping definitions](../encoder.md#configuration).
All [encoder mapping targets](../encoder.md#mapping-targets) are available to param controls, as well as the following additional options:

#### additional mapping targets

##### DEV

**Applies to**: Any device's bypass state.

**Example:** `"my track" / DEV(1)`

---

##### DEV SEL

**Applies to**: The selection status of any device.

**Example:** `"my track" / DEV(1) SEL`

___

##### `track` / SEL

**Applies to**: The selection status of any track.

**Example:** `"my track" / SEL`

---

##### ARM

**Applies to**: Any track's arm state.

**Example:** `SEL/ARM`

---

##### MON `x`

**Applies to**: Any track's input monitoring state, where `x` is `in`, `auto`, or `off`.

**Example:** `SEL/MON IN`

---

##### MUTE

**Applies to**: Any track's mute state.

**Example:** `SEL/MUTE`

---

##### SOLO

**Applies to**: Any track's solo state.

**Example:** `SEL/SOLO`

---

##### XFADE `x`

**Applies to**: Any track's crossfader assignment, where `x` is `a`, `b`, or `off`.

**Example:** `SEL/XFADE A`

---

##### `track` / PLAY

**Applies to**: The playing status of the selected clip slot on the targeted track.

If a clip exists in the relevant clip slot, this control will be considered on if that clip is **not playing**.
If the relevant clip is already playing, or if no clip exists, the control will be considered off.

**Example:** `SEL/PLAY`

---

##### `track` / STOP

**Applies to**: The playing status the targeted track.

This control will be considered on if the targeted track has a playing clip slot.

**Example:** `SEL/STOP`

---

### on_color, off_color
`color definition`

Color definitions based on the [state](#behaviour) of the mapped parameter.

### disabled_color
`color definition`

Color definition when the control is disabled, e.g. after failing to find its target.

### toggle_param
`true | false | "momentary"`

If set to `momentary`, the [default behaviour](#behaviour) will execute on both press and release.

If set to `false`, the [default behaviour](#behaviour) will not execute unless invoked with the [do_toggle](#do_toggle) command.

### midpoint
`number`

A percentage between 0.0 and 100.0 to be used when [determining state](#behaviour).
A parameter above this value will be considered active.
With `midpoint: 0.0` the control will behave as normal.
With `midpoint: 100.0` the default behaviour will be inverted.


## properties

### next_pct, next_value

Returns the value that the parameter would be set to the next time it is toggled.
`next_pct` returns that value as a number between `0.0` and `100.0`, which can be used in a ClyphX Pro action list to [ramp the parameter](https://www.cxpman.com/manual/general-action-information/#ramping-parameters).
`next_value` returns a string value.

**Example usage:**
```yaml
binding: >
  "my cool track" / VOL
pressed: >
  "my cool track" / VOL RAMP 10 ${me.next_pct}% 
```

## special command types

### do_toggle

Manually trigger the [default toggle behaviour](#behaviour) from within a command bundle.

```yaml hl_lines="4 9"
my_control:
  type: param
  binding: SEL / DEV(1)
  toggle_param: false
  gestures:
    pressed:
      SEL / DEV(1) SEL
    pressed__shift:
      do_toggle: true
```

In this example, the control is bound to the bypass state of the first device on the selected track.
Without holding `shift`, pressing the control selects the device.
While holding `shift`, the device's bypass is toggled.

**Note:** For this command to be useful, [toggle_param](#toggle_param) must be set to `false`, otherwise every press will always toggle the parameter.

## Examples

### Minimal config

```yaml
my_control:
  type: param
  binding: >
    DEV(SEL) P1
```

See [binding](#binding) for available options.

### Mode-aware

```yaml
my_control:
  type: param
  binding:
    default: >
      "my track" / ARM
    __shift: >
      "my track" / MUTE
```
