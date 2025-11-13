---
weight: -6
---

# mode control

The `mode` control binds to a particular [mode](../../lessons/getting-started/zcx-concepts.md#modes) in zcx and displays feedback indicating whether that mode is currently active

!!! Note
    Standard controls are already capable of changing modes, and mode controls still require you to manually define the mode change commands. 
    The only purpose of this control is to enable LED feedback.

    See [command reference](../command.md#mode_on-mode_off-mode).

## yaml schema

Inherits from [standard control](standard.md#yaml-schema).

```yaml
mode: string
# color: ignored
active_color: color definition
inactive_color: color definition
```

### mode
`string`

The mode to bind to.

### active_color, inactive_color
`color definition`

The color when the control's mode is active or inactive.

___
### color
`ignored`

Feedback is based on whether the control's bound mode is active.

## Examples

### Momentary

```yaml
my_control:
  type: mode
  mode: shift
  gestures:
    pressed:
      mode_on: shift
    released:
      mode_off: shift
```

### With latch

```yaml
my_control:
  type: mode
  mode: shift
  gestures:
    pressed:
      mode_on: shift
    released:
      mode_off: shift
    double_clicked:
      mode_on: shift
```

Double-click to keep the mode on then short press to turn it off again.

### Toggle

```yaml
my_control:
  type: mode
  mode: shift
  gestures:
    pressed:
      mode: shift
```

### Custom colors

```yaml
my_control:
  type: mode
  mode: shift
  active_color: green
  inactive_color: white
  gestures:
    pressed:
      mode_on: shift
    released:
      mode_off: shift
```
