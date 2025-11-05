---
weight: -100
---

# Pad faders

Let's see how we can recreate a feature from the Launchpad series, where a column of pads acts as a fader for a track's volume or a device parameter.


## Volume faders
### Instructions

First, let's set the pad faders up to control the volume of the eight tracks inside the [session ring](../lessons/session-ring.md).

Create a new [matrix section](../lessons/getting-started/zcx-concepts.md#matrix-sections).
We'll make it 8x8 and call it `pad_faders`:

```yaml title="matrix_sections.yaml"
pad_faders:
  row_start: 0
  row_end: 7
  col_start: 0
  col_end: 7
```

Create the file `matrix_sections/pad_faders.yaml`.
We'll use a [whole-section group](../reference/template.md#whole-section-groups) for this recipe, so create it like so:

```yaml title="matrix_sections/pad_faders.yaml"
pad_group: pad_faders
```

For LED feedback, we'll use the [param control](../reference/control/param.md).
The param control has a mandatory [binding](../reference/control/param.md#binding) option: the parameter we want to control.

In this case, our target is the track's volume.
Because we're targeting the session ring, we use a [special syntax](../reference/encoder.md#targeting-the-session-ring) combined with the [VOL](../reference/encoder.md#vol) parameter.

```yaml title="matrix_sections/pad_faders.yaml" hl_lines="2-4"
pad_group: pad_faders
type: param
binding: >
  RING(${me.x}) / VOL
```

Inside the `RING()` part, we're using a [template string](../reference/template.md#template-strings) and referencing each control's [x property](../reference/control/standard.md#x-x_flip) to associate each column with each track of the session ring.

<br>

The [default behaviour](../reference/control/param.md#behaviour) of the param control won't do what we need for this recipe; we'll need to set a [custom midpoint](../reference/control/param.md#midpoint) so that each control sets the parameter according to its [y-position](../reference/control/standard.md#y-y_flip):

```yaml title="matrix_sections/pad_faders.yaml" hl_lines="5-7"
pad_group: pad_faders
type: param
binding: >
  RING(${me.x}) / VOL
vars:
  my_midpoint: round((100 / 8) * me.y_flip, 1)
midpoint: ${my_midpoint}
```

We're declaring a [var](../reference/template.md#complex-expressions), `my_midpoint`, that associates each control with a percentage according to its y-position.
We're using a cheeky [magic number](https://en.wikipedia.org/wiki/Magic_number_(programming)), `8`, because the matrix is 8 rows tall.
Instead of `me.y`, we're using `me.y_flip` so that higher rows produce higher values: the bottom row sets the parameter to `0%`, the next to `12.5%`, and so on 'til `100%` at the top.

But this still isn't quite there.
We'll need to disable the param control's default behaviour with `toggle_param: false`, and set the parameter with a ClyphX Pro action list, using a [different syntax](../lessons/session-ring.md/#dynamic-track-controls) to target ring tracks:

```yaml title="matrix_sections/pad_faders.yaml" hl_lines="8 11"
pad_group: pad_faders
type: param
binding: >
  RING(${me.x}) / VOL
vars:
  my_midpoint: round((100 / 8) * me.y_flip, 1)
midpoint: ${my_midpoint}
toggle_param: false
gestures:
  pressed: >
    "${ring.tracks[me.x]}" / VOL ${my_midpoint}%
```

This will evaluate to something like `"my cool track" / VOL 50%`.
Don't forget to include the `%` sign manually!

Optionally, we can specify an [on_color and off_color](../reference/control/param.md#on_color-off_color) to customise our faders:

```yaml
on_color: purple
off_color: off
```

And that's it!

#### Ramping

As a bonus, we can use ClyphX Pro's [ramp feature](https://www.cxpman.com/manual/general-action-information/#ramping-parameters) to gradually move the parameter over time.
Let's change the `pressed` gesture to `released_immediately`, and add a `pressed_delayed` gesture, giving us different actions for a short and long press:

```yaml title="matrix_sections/pad_faders.yaml" hl_lines="12 14-15"
pad_group: pad_faders
type: param
binding: >
  RING(${me.x}) / VOL
vars:
  my_midpoint: round((100 / 8) * me.y_flip, 1)
midpoint: ${my_midpoint}
on_color: purple
off_color: off
toggle_param: false
gestures:
  released_immediately: >
    "${ring.tracks[me.x]}" / VOL ${my_midpoint}%
  pressed_delayed: >
    "${ring.tracks[me.x]}" / VOL RAMPS 1B ${my_midpoint}%
```

Now, after a long press, the parameter will ramp over one bar.

### Final output

```yaml title="matrix_sections.yaml"
pad_faders:
  row_start: 0
  row_end: 7
  col_start: 0
  col_end: 7
```

```yaml title="matrix_sections/pad_faders.yaml"
pad_group: pad_faders
type: param
binding: >
  RING(${me.x}) / VOL
vars:
  my_midpoint: round((100 / 8) * me.y_flip, 1)
midpoint: ${my_midpoint}
on_color: purple
off_color: off
toggle_param: false
gestures:
  released_immediately: >
    "${ring.tracks[me.x]}" / VOL ${my_midpoint}%
  pressed_delayed: >
    "${ring.tracks[me.x]}" / VOL RAMPS 1B ${my_midpoint}%
```

## Device parameter faders

Let's adapt the above recipe to instead control device parameters.
We'll have our eight columns control the first eight parameters of the selected device:

```yaml title="matrix_sections/pad_faders.yaml" hl_lines="4 13 15"
pad_group: pad_faders
type: param
binding: >
  SEL / DEV(SEL) B1 P${me.X}
vars:
  my_midpoint: round((100 / 8) * me.y_flip, 1)
midpoint: ${my_midpoint}
on_color: purple
off_color: off
toggle_param: false
gestures:
  released_immediately: >
    SEL / DEV(SEL) B1 P${me.X} ${my_midpoint}%
  pressed_delayed: >
    SEL / DEV(SEL) B1 P${me.X} RAMPS 1B ${my_midpoint}%
```

!!! warning "small x and Big X"
    Above, we used `me.x` to return a [zero-indexed](https://en.wikipedia.org/wiki/Zero-based_numbering) value necessary for zcx.
    Here, we are using `me.X`, as ClyphX Pro expects a one-indexed value.

The only required change is swapping the `VOL` target for a [best-of-bank parameter target](../reference/encoder.md#devd-bb-pp).

### Adding a device chooser

It would be nice if we could move between the devices on our track.
By adding some more controls we can do just that.

Let's dedicate buttons `scene_1` through `scene_8` to a device chooser:

```yaml title="named_controls.yaml"
__device_chooser:
  includes:
    [scene_1, scene_2, scene_3, scene_4, scene_5, scene_6, scene_7, scene_8]
  type: param
  binding: >
    SEL / DEV(${me.Index}) SEL
```

Now our scene buttons will select the first through eighth device on the selected track.
As our pad faders are already targeting the selected device, we now have control over the first eight parameters on the first eight devices.

!!! tip 
    This device chooser would work well as an [overlay](../lessons/overlays-layers.md#overlays).

As a bonus, let's make it so a double-click toggle's the device's bypass:

```yaml title="named_controls.yaml" hl_lines="8-9"
__device_chooser:
  includes:
    [scene_1, scene_2, scene_3, scene_4, scene_5, scene_6, scene_7, scene_8]
  type: param
  binding: >
    SEL / DEV(${me.Index}) SEL
  gestures:
    double_clicked: >
      SEL / DEV(${me.Index})
```

### Final output

```yaml title="matrix_sections.yaml"
pad_faders:
  row_start: 0
  row_end: 7
  col_start: 0
  col_end: 7
```

```yaml title="matrix_sections/pad_faders.yaml"
pad_group: pad_faders
type: param
binding: >
  SEL / DEV(SEL) B1 P${me.X}
vars:
  my_midpoint: round((100 / 8) * me.y_flip, 1)
midpoint: ${my_midpoint}
on_color: purple
off_color: off
toggle_param: false
gestures:
  released_immediately: >
    SEL / DEV(SEL) B1 P${me.X} ${my_midpoint}%
  pressed_delayed: >
    SEL / DEV(SEL) B1 P${me.X} RAMPS 1B ${my_midpoint}%
```

```yaml title="named_controls.yaml"
__device_chooser:
  includes:
    [scene_1, scene_2, scene_3, scene_4, scene_5, scene_6, scene_7, scene_8]
  type: param
  binding: >
    SEL / DEV(${me.Index}) SEL
  gestures:
    double_clicked: >
      SEL / DEV(${me.Index})
```
