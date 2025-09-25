---
weight: -4
---

# transport control

The `transport` control binds to a particular function of Live's transport, displaying feedback based on the state of the function.

!!! Note
    Standard controls are already capable of controlling the transport, and transport controls still require you to manually define the action lists to fire. The only purpose of this control is to enable control feedback.

    See [command reference](../command.md#cxp).

## yaml schema

Inherits from [standard control](standard.md#yaml-schema).

```yaml
transport: string
# color: ignored
active_color: color definition
inactive_color: color definition
playing_active_color: color definition
playing_inactive_color: color definition
```

### transport
`string`

The name of the transport function to bind to. These functions are currently supported:

- `play`
- `session_record`
- `metronome`
- `loop`

### color
`ignored`

Feedback is based on whether the control's bound transport function is active.

### active_color, inactive_color

Provide a color definition that will be used when the bound transport function is active or inactive.
If either of these options are undefined, a default will be used.

### playing_active_color, playing_inactive_color

Similar to above, but this color will be used when the song is playing.

**Notes:**
- This is applicable to all transport functions, not just `play`
- If no `active_color` or `inactive_color` is defined, this option will be ignored.

