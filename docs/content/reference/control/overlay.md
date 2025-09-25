---
weight: -5
---

# overlay control

The `overlay` control is identical to the `standard` control, except it has a required `overlay` option. 
This control's LED feedback will reflect whether its bound [overlay](../../lessons/overlays-layers.md) is currently active.
As such, the `color` option is ignored in favor of [active color](#active_color) and [inactive color](#inactive_color)

!!! Note
    Standard controls are already capable of changing overlays, and overlay controls still require you to manually define the overlay change commands. 
    The only purpose of this control is to enable LED feedback.

    See [command reference](../command.md#overlay).


## yaml schema

Inherits from [standard control](standard.md#yaml-schema).

```yaml
overlay: string, int
active_color: color definition
inactive_color: color definition
# color: not implemented
```

### overlay
`string`

The name of the overlay this control is bound to.

See the [overlays lesson](../../lessons/overlays-layers.md).

___
### color
`not implemented`

Use [active color](#active_color) **and** [inactive color](#inactive_color).

### active_color
`color definition`

Define a color that will display when this control's bound page is active.

### inactive_color
`color definition`

Inverse of [active color](#active_color).

## properties

These are values attached to controls that can be referenced from within [template strings](../template.md#template-strings).

#### page

Returns the **zero-indexed** page number of this control's bound page.

#### Page
_with a capital `P`_

Returns `page` + 1.

#### page_name

Returns the name of the bound page.

#### is_active

Returns a boolean representing if the bound page is in view.
