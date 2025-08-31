---
weight: -1
---
# ring_track control

A version of the [track control](track.md) that dynamically binds to the track at a particular index of the [session ring](../../lessons/session-ring.md).
An RGB-enabled button will attempt to display animated feedback representing the track's state (playing, recording, etc.). 


!!! warning

    Currently, track controls only consider session view clips when determining playing status, not arrangement view clips.

## yaml schema

Inherits from [track control](track.md#yaml-schema).

```yaml
ring_index: int
```

## options

### ring_index
`int`

The zero-indexed column number of the session ring track to bind to.
