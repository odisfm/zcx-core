---
weight: -2
---

# track control

The `track` control binds to a particular track in the Live set. An RGB-enabled button will attempt to display animated feedback representing the track's state (playing, recording, etc.). 

When the `track` option is configured, zcx will bind to the specified track on set load. The control's bound track can later be reassigned via the API, and the `track` option may be omitted to create an unbound control on set load.

!!! warning

    Currently, track controls only consider session view clips when determining playing status, not arrangement view clips.

## yaml schema

Inherits from [standard control](standard.md#yaml-schema).

```yaml
track: string, int
color: color definition
animate_while_stopped: boolean=false
```

## options

### track
`string | int`

The track name or number to bind to. Binding by number is generally only recommended for testing purposes.

___
### color
`color definition`

By default, the track control will attempt to create a palette of colors based on the color of the bound track. You may optionally pass a color option, and that color will be used as a base instead. **Note:** if an animated color is specified, only the 'a' color of the animation will be considered. See [color reference](../color.md).

---
### animate_while_stopped
`boolean=false`

When `true`, animations will stay active when the transport is stopped.

## properties

These are values attached to controls that can be referenced from within [template strings](../template.md#template-strings).

### track

Returns the name of the bound track.