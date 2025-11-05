# Ramped momentary fx template

By using the [param control](../reference/control/param.md) we can bind a device parameter to a button.
However, the param control toggles the parameter instantly between its minimum and maximum values, which isn't very musical.

Let's see how we can use a param control to smoothly [ramp](https://www.cxpman.com/manual/general-action-information/#ramping-parameters) the parameter, and save it as a template to use it many times in our config without repeating the same definition.

## Goal

Our final template will accept these arguments:

- the parameter to control
- the minimum and maximum values it should have
- the time it should take to ramp between the min and max values
    - optionally, we will be able to set a different speed for ramping up and ramping down

The control will be momentary; when pressed it will ramp up, and when released it will ramp down.

## Instructions

First, create a [control template](../reference/template.md#control-templates).
We'll use the name `fx_ramp` here, but it can be called whatever you like.
Make it of `type: param` with `binding: NONE`:

```yaml title="control_templates.yaml"
fx_ramp:
  type: param
  binding: NONE
```

For testing purposes, let's create a control that inherits from this template.
We'll use a [named control](../lessons/getting-started/zcx-concepts.md#named-controls) here, but you may use a [matrix control](../lessons/getting-started/zcx-concepts.md#matrix-controls) too:

```yaml title="named_controls.yaml"
play:
  template: fx_ramp
```

<br>

To make our template accept arguments, we'll make use of [template strings](../reference/template.md#template-strings) and [complex expressions](../reference/template.md#complex-expressions):

```yaml title="control_templates.yaml" hl_lines="3-5"
fx_ramp:
  type: param
  binding: ${me.props.bind_target}
  props:
    bind_target: NONE
```
```yaml title="named_controls.yaml" hl_lines="3-5"
play:
  template: fx_ramp
  props:
    bind_target: >
      "my track" / DEV("my device") P1
```

You can imagine the output so far like:

```yaml
play:
  type: param
  binding: >
     "my track" / DEV("my device") P1
```

Now, we need to disable the [default behaviour](../reference/control/param.md#behaviour) of the param control, so we can supply our own logic.

```yaml title="control_templates.yaml" hl_lines="4 7-11"
fx_ramp:
  type: param
  binding: ${me.props.bind_target}
  toggle_param: false
  props:
    bind_target: NONE
  gestures:
    pressed: >
      ${me.props.bind_target} RAMPS 1B 100%
    released: >
      ${me.props.bind_target} RAMPS 1B 0%
```

Now, a press would do the ClyphX Pro action list:

```ClyphX_Pro
"my track" / DEV("my device") P1 RAMPS 1B 100%
```

Ramping the first parameter on `my device` to max over one bar.
The `released` gesture does the opposite.

<br>

We want to replace these default values, `RAMPS 1B` and `100%` with our own values.
We can do that with props as well:

```yaml title="control_templates.yaml" hl_lines="7 8 9 12 14"
fx_ramp:
  type: param
  binding: ${me.props.bind_target}
  toggle_param: false
  props:
    bind_target: NONE
    ramp: RAMPS 1B
    min: 0
    max: 100
  gestures:
    pressed: >
      ${me.props.bind_target} ${me.props.ramp} ${me.props.max}%
    released: >
      ${me.props.bind_target} ${me.props.ramp} ${me.props.min}%
```

Let's override the template and make the parameter ramp to half over two beats:
```yaml title="named_controls.yaml" hl_lines="6-7"
play:
  template: fx_ramp
  props:
    bind_target: >
      "my track" / DEV("my device") P1
    max: 50
    ramp: RAMP 2
```

Now we have:
```yaml
gestures:
  pressed: >
    "my track" / DEV("my device") P1 RAMP 2 50%
  released: >
    "my track" / DEV("my device") P1 RAMP 2 0%
```

### Going further

#### Different speeds

We can use a different speed for ramp up and ramp down:

```yaml title="control_templates.yaml" hl_lines="8 9 14 16"
fx_ramp:
  type: param
  binding: ${me.props.bind_target}
  toggle_param: false
  props:
    bind_target: NONE
    ramp: RAMPS 1B
    ramp_down: null
    ramp_up: null
    min: 0
    max: 100
  gestures:
    pressed: >
      ${me.props.bind_target} ${me.props.ramp_up or me.props.ramp} ${me.props.max}%
    released: >
      ${me.props.bind_target} ${me.props.ramp_down or me.props.ramp} ${me.props.min}%
```
```yaml title="named_controls.yaml" hl_lines="8"
play:
  template: fx_ramp
  props:
    bind_target: >
      "my track" / DEV("my device") P1
    max: 50
    ramp: RAMP 2
    ramp_down: RAMPS 2B
```

This `${me.props.ramp_up or me.props.ramp}` means that if we don't provide a `ramp_up` or `ramp_down` prop, we use the default, `RAMPS 1B`, which is defined on the template.
This gives us the gestures:

```yaml
gestures:
  pressed: >
    "my track" / DEV("my device") P1 RAMP 2 50%
  released: >
    "my track" / DEV("my device") P1 RAMPS 2B 0%
```

#### Animated colors

As we're creating a template, why don't we set some colors:

```yaml title="control_templates.yaml" hl_lines="12-18"
fx_ramp:
  type: param
  binding: ${me.props.bind_target}
  toggle_param: false
  props:
    bind_target: NONE
    ramp: RAMPS 1B
    ramp_down: null
    ramp_up: null
    min: 0
    max: 100
    color: red
    blink_color: white
  off_color: ${me.props.color}
  on_color:
    blink:
      a: ${me.props.color}
      b: ${me.props.blink_color}
  gestures:
    pressed: >
      ${me.props.bind_target} ${me.props.ramp_up or me.props.ramp} ${me.props.max}%
    released: >
      ${me.props.bind_target} ${me.props.ramp_down or me.props.ramp} ${me.props.min}%
```
```yaml title="named_controls.yaml" hl_lines="9"
play:
  template: fx_ramp
  props:
    bind_target: >
      "my track" / DEV("my device") P1
    max: 64
    ramp: RAMP 2
    ramp_down: RAMPS 2B
    color: purple
```

Without setting anything on `play`, the LED will be red when the parameter is at 0, but blink red and white when above 0.
Because we did `color: purple`, it will be purple rather than red.
We could also do `blink_color: blue` to blink purple and blue.

We should probably set the control's [midpoint](../reference/control/param.md#midpoint) so the LED feedback is more relevant:

```yaml title="control_templates.yaml" hl_lines="2"
fx_ramp:
  midpoint: ${me.props.min + 1}
  ...
```

### Toggle control

This template can be easily modified to a toggle control by using the [pseq command](../reference/command.md#pseq-rpseq):
```yaml
fx_ramp:  
  # ... existing settings
  gestures:
    pressed:
      pseq:
        - ${me.props.bind_target} ${me.props.ramp_up or me.props.ramp} ${me.props.max}%
        - ${me.props.bind_target} ${me.props.ramp_down or me.props.ramp} ${me.props.min}%
```

## Final output

```yaml title="control_templates.yaml"
fx_ramp:
  type: param
  binding: ${me.props.bind_target}
  midpoint: ${me.props.min + 1}
  toggle_param: false
  props:
    bind_target: NONE
    ramp: RAMPS 1B
    ramp_down: null
    ramp_up: null
    min: 0
    max: 100
    color: red
    blink_color: white
  off_color: ${me.props.color}
  on_color:
    blink:
      a: ${me.props.color}
      b: ${me.props.blink_color}
  gestures:
    pressed: >
      ${me.props.bind_target} ${me.props.ramp_up or me.props.ramp} ${me.props.max}%
    released: >
      ${me.props.bind_target} ${me.props.ramp_down or me.props.ramp} ${me.props.min}%
```
```yaml title="named_controls.yaml"
play:
  template: fx_ramp
  props:
    bind_target: >
      "my track" / DEV("my device") P1
    max: 64
    ramp: RAMP 2
    ramp_down: RAMPS 2B
    color: purple
```
