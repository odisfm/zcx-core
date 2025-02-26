---
hide:
  - footer
---

# standard control

The below properties are enabled on the base [ZControl](/lessons/zcx-concepts#zcontrols) class which all other control types descend from. Unless otherwise specified, they behave the same way for all control types.

## yaml schema

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

See [grouped controls reference]().

___

### buttons
`dict[ZControl]`

See [grouped controls reference]().

___
### pad_group
`dict[ZControl]`

See [grouped controls reference]().

___
### gestures
`dict[dict[command]]`

See [command reference]().

___
### vars
`dict[dict[string]]`

See [command reference]().

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

The template(s) to apply to this control. See [template reference]().

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
