# Keyboard control

The keyboard control displays LED feedback concerning the state of the [keyboard view](../../lessons/keyboard.md), as well as Live's [scale mode](https://help.ableton.com/hc/en-us/articles/11425083250972-Keys-and-Scales-in-Live-12-FAQ).

!!! Note
    Standard controls are already capable of interacting with the keyboard view, and the keyboard control still requires you to manually define any commands.
    The only purpose of this control is to enable LED feedback.

    [See more](../../lessons/keyboard.md#melodic-settings).

## yaml schema

Inherits from [standard control](standard.md#yaml-schema).

```yaml
function: string, dict
active_color: color definition
inactive_color: color definition
# color: not implemented
```

### function
`string, dict`

This is the condition that will determine if the control is [active](#active_color) or [inactive](#inactive_color).

#### repeat_rate
```yaml
function:
  repeat_rate: 1/4
```
```yaml
function:
  repeat_rate: on
```

Reflect the keyboard's [note repeat rate](../../lessons/keyboard.md#note-repeat).

#### in_key
```yaml
function: in_key
```

Reflect if they keyboard is using [in key](../../lessons/keyboard.md#in-key-chromatic) mode.

#### full_velo
```yaml
function: full_velo
```

Reflect if they keyboard is using [full velocity](../../lessons/keyboard.md#full-velocity) mode.

#### octave_down, octave_up
```yaml
function: octave_down
```

Reflect if the [keyboard's octave](../../lessons/keyboard.md#octave) is at its lowest or highest: if the octave is at its lowest, `function: octave_down` would be inactive.

#### scale

Reflects the root and/or scale name of Live's scale mode.

```yaml
function:
  scale:
    root: F
```
```yaml
function:
  scale:
    name: lydian augmented
```
```yaml
function:
  scale:
    root: C
    name: major
```

For either `root` or `name` you may provide an integer.
For `root`, C is 0 and B is 11.
For `name`, the order follows the order of scales in the Live GUI.

In either case you may provide an integer greater than the number of options and your choice will be "wrapped" to a valid one.
E.g. providing `12` for `root` will result in C, as will `24`.

### color
`not implemented`

Use [active color](#active_color) **and** [inactive color](#inactive_color).

### active_color
`color definition`

Define a color that will display when this control's bound page is active.

### inactive_color
`color definition`

Inverse of [active color](#active_color).
