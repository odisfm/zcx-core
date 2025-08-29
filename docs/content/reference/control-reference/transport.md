---
weight: -7
---

# transport control

The `transport` control binds to a particular function of Live's transport, displaying feedback based on the state of the function.

!!! Note
    Standard controls are already capable of controlling the transport, and transport controls still require you to manually define the action lists to fire. The only purpose of this control is to enable control feedback.

    See [command reference](/reference/command-reference#cxp).

## yaml schema

Inherits from [standard control](/reference/control-reference/z-control/#yaml-schema).

```yaml
transport: string
# color: ignored
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
