

# mode control

The `mode` control binds to a particular [mode](/tutorials/getting-started/zcx-concepts/#modes) in zcx and displays feedback indicating whether that mode is currently active

## yaml schema

Inherits from [standard control](/reference/control-reference/z-control/#yaml-schema).

```yaml
mode: string
# color: ignored
```

### mode
`string`

The mode to bind to.

___
### color
`ignored`

Feedback is based on whether the control's bound mode is active.
