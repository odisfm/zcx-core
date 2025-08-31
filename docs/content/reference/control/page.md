---
weight: -7
---

# page control

The `page` control is identical to the `standard` control, except it has a required `page` option. This control's LED feedback will reflect whether its bound page is currently active. As such, the `color` option is ignored in favor of [active color](#active_color) and [inactive color](#inactive_color)

!!! Note
    Standard controls are already capable of changing pages, and page controls still require you to manually define the page change commands. The only purpose of this control is to enable control feedback.

    See [command reference](../command.md#page).


## yaml schema

Inherits from [standard control](standard.md#yaml-schema).

```yaml
page: string, int
active_color: color definition
inactive_color: color definition
# color: not implemented
```

### page
`string | int`

The page name or number this control is bound to. Passing a string value means that the binding is resistant to page order changes, while passing an int may be suitable for a dedicated 'page row'.

**Note:** page numbers are always zero-indexed.

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
