---
weight: 0
---
# param control

The `param` control binds to a device parameter, mixer parameter, or other special function, and displays feedback about the state of its target.
This feature aims to emulate the Button Bindings feature from the [ClyphX Pro Bindings](https://www.cxpman.com/manual/optional-accessories/#clyphx-pro-bindings) optional accessory.

## behaviour

The param control displays [different colors](#on_color-off_color) based on whether its target is considered "on" or "off".
For binary targets like [arm](#arm), this is straightforward.
For [adjustable properties](https://www.cxpman.com/manual/general-action-information/#multiple-devices), like a track's volume, the parameter is considered "off" if the parameter is at its **minimum** value, and "on" for any other value.

Without defining any [gestures](reference/command-reference/#gestures), the param control will toggle its mapped parameter from "on" to "off" on a press.
Binary targets will have their status inverted.
For adjustable properties, a parameter currently at its minimum value will be set to its maximum, and a parameter at any value above its minimum is set to its maximum.

You can disable this behaviour by setting [toggle_param](#toggle_param) to `false`.
Any defined gestures will be executed as normal.

## yaml schema

Inherits from [standard control](/reference/control-reference/z-control/#yaml-schema).

```yaml
binding: binding definition
on_color: color definition
off_color: color definition
disabled_color: color definition
toggle_param: boolean=true
# color: not implemented
```

### binding
`binding definition`

Follows the same format as [encoder mapping definitions](/reference/encoder-reference/#configuration).
All [encoder mapping targets](/reference/encoder-reference/#mapping-targets) are available to param controls, as well as the following additional options:

#### additional mapping targets

##### DEV

**Applies to**: Any device's bypass state.

**Example:** `"my track" / DEV(1)`

##### ARM

**Applies to**: Any track's arm state.

**Example:** `SEL/ARM`

##### MON `x`

**Applies to**: Any track's input monitoring state, where `x` is `in`, `auto`, or `off`.

**Example:** `SEL/MON IN`

##### MUTE

**Applies to**: Any track's mute state.

**Example:** `SEL/MUTE`

##### SOLO

**Applies to**: Any track's solo state.

**Example:** `SEL/SOLO`

##### XFADE `x`

**Applies to**: Any track's crossfader assignment, where `x` is `a`, `b`, or `off`.

**Example:** `SEL/XFADE A`


### on_color, off_color
`color definition`

Color definitions based on the [state](#behaviour) of the mapped parameter.

### disabled_color
`color definition`

Color definition when the control is disabled, e.g. after failing to find its target.

### toggle_param
`boolean=true`

If set to `false`, disables the [default behaviour](#behaviour) on control press.
