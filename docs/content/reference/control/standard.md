---
weight: -10
hide:
  - footer
---

# standard control

The below options are available on the base [ZControl](../../lessons/getting-started/zcx-concepts.md#zcontrols) class which all other control types descend from. Unless otherwise specified, they behave the same way for all control types.

## yaml schema

These are options you can set on each control via its yaml definition. Some options will not be available in every context.

```yaml
type: string
alias: string
color: color definition
hold_color: color definition
includes: list[string]
buttons: dict[ZControl]
gestures: dict[dict]
pad_group: string
vars: dict
repeat: boolean=false
template: string, list[string], null
props: dict[any]
threshold: int=30
cascade: false | "down" | "up" = false
release_on_ext: bool = true
```

### type
`string='standard'`

Changing this option from the default `standard` will create a specialised ZControl. Allowed value is the name of any installed [control classes](index.md).

___

### alias
`string`

Allows you to provide a name for a matrix control, or an alternate name for a named control, which can later be used to target this control via the zcx API, e.g. [the zcx user action](../../lessons/zcx-user-action.md).

___

### color
`color definition` 

The base color of the control. See [color reference](../color.md).

---

### hold_color
`color definition`

By providing a `hold_color` option, the control will use this color while it is held, and return to its [base color](#color) when released.
This will override the default blinking animation on control presses.

___
### includes
`list[string]`

_Only available on named control group definitions._

See [template reference](../template.md#named-controls).

___
### pad_group
`string | null`

_Only available on matrix control group definitions._

See [template reference](../template.md#matrix-controls).

___

### controls
`list[ZControl] | dict[ZControl]`

Used in a [group control definition](../template.md#group-templates) to override properties on one or more ZControls in the group.
Accepts a list for a [group of matrix controls](../template.md#matrix-controls) or a dict for a [group of named controls](../template.md#named-controls).

___
### gestures
`dict[dict[command]]`

See [command reference](../command.md#gestures).

___
### vars
`dict[dict[string]]`

See [template reference](../template.md#complex-expressions).

___
### repeat
`boolean=false`

Repeatedly trigger this control's `pressed` gesture (with modifiers) while it is held.

---
### suppress_animations
`boolean=false`

Prevent LED animations from firing on this control.

___
### template
`string | list[string] | null`

The template(s) to apply to this control. See [template reference](../template.md#control-templates).

`string`
Apply a single template.

`list[string]`
Apply each template consecutively. Options that conflict will be overwritten from left to right.

`null`
Apply no template, including the `__global__` template.

___
### props
`dict[string | int]`

Any arbitrary data. Can be referenced from within [template strings](../template.md#template-strings).

___
### threshold
`int=30`

Override the global velocity threshold, which by default is `30`. Triggers under this threshold will be ignored.

___
### cascade
`false | "down" | "up" = false`

Configures the control's behaviour when [multiple command bundles match the performed gesture](../command.md#multiple-matching-gestures).
The default of `false` executes only one matching command bundle per gesture.

---
### release_on_exit
`bool = true`

Concerns the scenario where a control leaves view while being held, e.g. you are holding a matrix control and change to a page that doesn't feature that control.

With the default of `true`, the control will fire its `released` gesture.
Additionally, it will fire its `released_delayed` gesture if the control had been held a short while, or the `released_immediately` gesture if it had not.

If set to `false`, none of the above will happen.

## properties

These are values attached to controls that can be referenced from within [template strings](../template.md#template-strings).

### obj

Returns a reference to the [actual Python object](https://github.com/odisfm/zcx-core/blob/main/app/z_control.py) for the control.

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

#### group_count

Returns the number of controls in this group.

### location properties
_Only available on matrix controls._

Use a capital `X` or `Y` to retrieve a one-indexed value.

#### x, x_flip
Returns the **zero-indexed** column of the control (**x**) or its mirrored position (**x_flip**), **relative to its containing section**.

#### y, y_flip
Returns the **zero-indexed** row of the control (**y**) or its mirrored position (**y_flip**), **relative to its containing section**.

#### global_x, global_x_flip
Returns the **zero-indexed** column of the control (**global_x**) or its mirrored position (**global_x_flip**), **relative to the entire matrix**.

#### global_y, global_y_flip
Returns the **zero-indexed** row of the control (**global_y**) or its mirrored position (**global_y_flip**), **relative to the entire matrix**.

### section properties
_Only available on matrix controls._

#### section.height, section.width

Returns the height or width of this control's containing [matrix section](../../lessons/getting-started/zcx-concepts.md#matrix-sections).

#### section.name

Returns the name of this control's containing [matrix section](../../lessons/getting-started/zcx-concepts.md#matrix-sections).

#### section.obj

Returns the [Python object](https://github.com/odisfm/zcx-core/blob/main/app/pad_section.py) of the section.

#### section.count

Returns the number of controls in the section.

### velocity properties

The following properties are based on the last velocity at which a control was struck. This value will **not** reset to 0 when the control is released.

#### vel

Returns the last velocity as an integer (between 0-127).

#### velp

Returns the last velocity as a percentage (float).

To use this percentage in a ClyphX action list, you will need to manually add the % sign, e.g:

`SEL / VOL ${me.velp}%`

#### velps

Returns the last velocity as a percentage, but **scaled** according to the control's [threshold](#threshold).

E.g., if a control has a threshold of `30`, a press with a velocity of `30` will return `0.0`.

## Examples

### Minimal config

```yaml
my_control:
  color: red
  gestures:
    pressed: METRO
```

### Short press and long press

```yaml
my_control:
  color: red
  gestures:
    released_immediately: SRECFIX 4
    pressed_delayed: SREC
```


