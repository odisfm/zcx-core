# Push 1 

## Display plugin

zcx for Push 1 ships with a plugin that enables display output.
Each line of the display will be used for a specific purpose:

### encoder mappings

Displays the name of the parameter that the main encoder above it (`enc_1` - `enc_8`) is currently bound to.

### encoder values

Displays the current value of the aforementioned parameter.

### message

A reserved space, which can be written to from the [zcx user action](../../lessons/zcx-user-action.md#msg).

### ring_tracks

Displays the name of the first 8 tracks highlighted by the [session ring](../../lessons/session-ring.md)

### selected

Displays the selected track and scene. If the scene is named, the name will be shown. If the scene is an [X-Scene](https://www.cxpman.com/manual/core-concepts/#x-scenes), the scene name (action list) will not be shown, unless there is text within the [identifier](https://www.cxpman.com/manual/core-concepts/#identifiers), e.g. an X-Scene with the name `[my cool scene] METRO` will display `my cool scene`.

---

You can specify on which line each readout appears via [preferences.yaml](../configuration-files/preferences.md#plugins).

```yaml
plugins:
  push_1_display:
    encoder_mappings: 1
    encoder_values: 2
    message: 3
    ring_tracks: 4
```

### additional options

#### prefer_track_name

```yaml
prefer_track_name: true
```

With the default of `true`, when an encoder is mapped to a track's volume fader, the [encoder mapping segment](#encoder-mappings) will display the track's name.
With `false`, the parameter will be shown as `Volume`

#### use_graphics

```yaml
use_graphics: true
```

With the default of `true`, certain mapped parameters will show a graphical representation of the parameter's value.
With `false`, you will see the normal textual representation.

