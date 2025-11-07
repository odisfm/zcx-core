# Percussive parameter control

In this recipe, we'll create a [page](../lessons/getting-started/zcx-concepts.md#pages) that lets us control 64 parameters at once, depending on how hard we strike the control.

We'll target the first eight parameters of the first device of the tracks inside the [session ring](../lessons/session-ring.md).

## Instructions

First, create the [matrix section](../lessons/getting-started/zcx-concepts.md#matrix-sections).
In this example, we'll make it 8x8 and call it `velocity_params`, but you can make it any size and choose any name.

```yaml title="matrix_sections.yaml"
velocity_params:
  row_start: 0
  row_end: 7
  col_start: 0
  col_end: 7
```

Create the file `matrix_sections/velocity_params.yaml`.
We'll use a [whole-section group](../reference/template.md#whole-section-groups) for this recipe, so create it like so:

```yaml title="matrix_sections/velocity_params.yaml"
pad_group: velocity_params
```

For LED feedback, we'll use the [param control](../reference/control/param.md).
The param control has a mandatory [binding](../reference/control/param.md#binding) option: the parameter we want to control.

```yaml title="matrix_sections/velocity_params.yaml" hl_lines="2-3"
pad_group: velocity_params
type: param
binding: RING(${me.x}) / DEV(1) B1 P${me.Y}
```

Inside the `RING()` part, we're using a [template string](../reference/template.md#template-strings) and referencing each control's [x property](../reference/control/standard.md#x-x_flip) to associate each column with each track of the session ring.
We're using the [Y property](../reference/control/standard.md#y-y_flip) to associate each row with a parameter on the first device of that track.

Because we're targeting the session ring, we use a [special syntax](../reference/encoder.md#targeting-the-session-ring) combined with the [Bb Pp](../reference/encoder.md#devd-bb-pp) parameter.

<br>

This works, but it will only toggle each parameter between its minimum and maximum.

```yaml title="matrix_sections/velocity_params.yaml" hl_lines="4-8"
pad_group: velocity_params
type: param
binding: RING(${me.x}) / DEV(1) B1 P${me.Y}
toggle_param: false
midpoint: 50.0
gestures:
  pressed: >
    "${ring.tracks[me.x]}" / DEV(1) B1 P${me.Y} ${me.velps}%
```

We have set [toggle_param](../reference/control/param.md#toggle_param) to `false`, disabling the [default behaviour](../reference/control/param.md#behaviour) of the param control.
We've also set a [midpoint](../reference/control/param.md#midpoint) of `50.0`, meaning the control will be colored when the parameter is at its middle value or higher, and grey when below.

By using the [velps property](../reference/control/standard.md#velps), we are capturing the velocity of the last press, scaled according to the control's [threshold](../reference/control/standard.md#threshold).

Striking the row third from the top with average force will produce an output like:

`"my track" / DEV(1) B1 P3 56.3%`

### Ramping

We can easily add another gesture to [ramp](https://www.cxpman.com/manual/general-action-information/#ramping-parameters) the parameter over a number of beats.
Let's change the `pressed` gesture to `released_immediately`, and add a `pressed_delayed` gesture, giving us different actions for a short and long press:

```yaml title="matrix_sections/velocity_params.yaml" hl_lines="7 9-11"
pad_group: velocity_params
type: param
binding: RING(${me.x}) / DEV(1) B1 P${me.Y}
toggle_param: false
midpoint: 50.0
gestures:
  released_immediately: >
    "${ring.tracks[me.x]}" / DEV(1) B1 P${me.Y} ${me.velps}%
  pressed_delayed: >
    "${ring.tracks[me.x]}" / DEV(1) B1 P${me.Y} RAMPS 1B ${me.velps}%
```

Now, after a long press, the parameter will ramp to the target velocity over one bar.

## Final output

```yaml title="matrix_sections.yaml"
velocity_params:
  row_start: 0
  row_end: 7
  col_start: 0
  col_end: 7
```

```yaml title="matrix_sections/velocity_params.yaml"
pad_group: velocity_params
type: param
binding: RING(${me.x}) / DEV(1) B1 P${me.Y}
toggle_param: false
midpoint: 50.0
gestures:
  released_immediately: >
    "${ring.tracks[me.x]}" / DEV(1) B1 P${me.Y} ${me.velps}%
  pressed_delayed: >
    "${ring.tracks[me.x]}" / DEV(1) B1 P${me.Y} RAMPS 1B ${me.velps}%
```
