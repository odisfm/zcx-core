---
weight: -10
hide:
  - footer
---

# standard control

The below properties are enabled on the base [ZControl](/lessons/zcx-concepts#zcontrols) class which all other control types descend from. Unless otherwise specified, they behave the same way for all control types.

## yaml schema

These are options you can set on each control via its yaml definition. Some options will not be available in every context.

```yaml
type: string
color: string, int, ZColor
includes: list[string]
buttons: dict[ZControl]
gestures: dict[dict]
pad_group: string
vars: dict
repeat: boolean=false
externally_managed_light: boolean=false
template: string, list[string], null
props: dict[any]
threhshold: int=30
```

### type
`string='standard'`

Changing this property from the default `standard` will create a specialised ZControl. Allowed value is the name of any installed [control classes](/tutorials/getting-started/zcx-concepts#control-classes).

___
### color
`string | int | dict` 

The `base` color of the control. See [color reference]().

`string`
Any _named color_.

 `int`
The MIDI value to send to this control.

 `dict`
See [color reference](),

___
### includes
`list[string]`

_Only available on named control group definitions._

See [template reference](/template-reference/#named-controls).

___

### buttons
`dict[ZControl]`

_Only available on named control group definitions._

See [template reference](/template-reference/#overwriting-properties).

___
### pad_group
`dict[ZControl]`

_Only available on matrix control group definitions._

See [template reference](/template-reference/#matrix-controls).

___

### pads
`list[ZControl]`

_Only available on matrix control group definitions._

See [template reference](/template-reference/#matrix-controls).


___
### gestures
`dict[dict[command]]`

See [command reference](/command-reference#gestures).

___
### vars
`dict[dict[string]]`

See [template reference](/reference/template-reference#complex-expressions).

___
### repeat
`boolean=false`

Repeatedly trigger this control's `pressed` gesture (with modifiers) while it is held.

___
### externally_managed_light
`boolean=false`

Suppress most color change events that fire on this control, preventing colors set manually via the API from being overwritten.

___
### template
`string | list[string] | null`

The template(s) to apply to this control. See [template reference](/template-reference#control-templates).

`string`
Apply a single template.

`list[string]`
Apply each template consecutively. Properties that conflict will be overwritten from left to right.

`null`
Apply no template, including the `__global__` template.

___
### props
`dict[string | int]`

Any arbitrary data. Can be referenced from within template strings.

___
### threshold
`int=30`

Override the global velocity threshold, which by default is `30`. Triggers under this threshold will be ignored.


## properties

These are values attached to controls that can be referenced from within [template strings](/reference/template-reference#template-strings).

### position properties

#### index

Returns the **zero-indexed** position of a matrix control within its containing section. Returns 0 for non-matrix controls, or the control's [group_index](#group_index) if it belongs to a group.

#### Index
_with a capital `I`_

Returns [index](#index) + 1.

#### group_index

Returns the **zero-indexed** position of a control within its containing group.

#### group_Index
_with a capital `I`_

Returns [group_index](#group_index) + 1.

### location properties
_Only available on matrix controls._

#### x, x_flip
Returns the **zero-indexed** column of the control (**x**) or its mirrored position (**x_flip**), **relative to its containing section**.

#### y, y_flip
Returns the **zero-indexed** row of the control (**y**) or its mirrored position (**y_flip**), **relative to its containing section**.

#### global_x, global_x_flip
Returns the **zero-indexed** column of the control (**global_x**) or its mirrored position (**global_x_flip**), **relative to the entire matrix**.

#### global_y, global_y_flip
Returns the **zero-indexed** row of the control (**global_y**) or its mirrored position (**global_y_flip**), **relative to the entire matrix**.