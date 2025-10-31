---
weight: -6
---

# mode control

The `mode` control binds to a particular [mode](../../lessons/getting-started/zcx-concepts.md#modes) in zcx and displays feedback indicating whether that mode is currently active

!!! Note
    Standard controls are already capable of changing modes, and mode controls still require you to manually define the mode change commands. 
    The only purpose of this control is to enable LED feedback.

    See [command reference](../command.md#mode).

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
