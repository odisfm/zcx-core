# transport control

The `transport` control binds to a particular function of Live's transport, displaying feedback based on the state of the function.

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

### color
`ignored`

Feedback is based on whether the control's bound transport function is active.
