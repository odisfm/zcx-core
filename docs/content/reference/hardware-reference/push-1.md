# Push 1

# Display plugin

zcx for Push 1 ships with a plugin that enables display output.
Each line of the display will be used for a specific purpose:

### encoder mappings

Displays the name of the parameter that the main encoder above it (`enc_1` - `enc_8`) is currently bound to.

### encoder values

Displays the current value of the aforementioned parameter.

### message

A reserved space, which can be written to from the [zcx user action](/lessons/zcx-user-action#msg).

### ring_tracks

Displays the name of the first 8 tracks highlighted by the [session ring](/lessons/session-ring)

---

You can specify on which line each readout appears via [preferences.yaml](/reference/configuration-files/preferences#plugins).

```yaml
plugins:
  push_1_display:
    encoder_mappings: 1
    encoder_values: 2
    message: 3
    ring_tracks: 4
```
