# Page changer

If you have more than a couple [matrix pages](../lessons/getting-started/zcx-concepts.md#pages), you probably want to dedicate a group of buttons as a page changer, letting you switch to any page instantly.
Each [demo config](../lessons/getting-started/demo-tour/index.md) has a page changer already, but in this lesson we'll learn how to build one from scratch and customise it.

## Instructions

In this example we'll dedicate eight [named controls](../lessons/getting-started/zcx-concepts.md#named-controls) to the changer. but you may use any number of controls.
Instead of named controls, you may use a [matrix section](../lessons/getting-started/zcx-concepts.md#matrix-sections) with a [section template](../reference/template.md#section-templates), but make sure the section appears on every page!

### Create the group

We'll start by [grouping](../reference/template.md#group-templates) our eight controls.
If you have less than eight pages, you may choose to use fewer controls.
Alternatively, leave it at eight, and when you add a page in the future, there will already be a button assigned to it.

```yaml title="named_controls.yaml"
__page_changer:
  includes: [state_1, state_2, state_3, state_4, state_5, state_6, state_7, state_8]
```
!!! tip ""
    These control names come from the Ableton Push.
    If you're unsure which names to use, check the [hardware reference](../reference/hardware/index.md).    

### Assign the pages

To get LED feedback about the active page, we'll set `#!yaml type: page` to make these controls [page controls](../reference/control/page.md).

Every page control has a mandatory `page` option, so we'll use a [template string](../reference/template.md#template-strings) to set that dynamically:

```yaml title="named_controls.yaml" hl_lines="3-4"
__page_changer:
  includes: [state_1, state_2, state_3, state_4, state_5, state_6, state_7, state_8]
  type: page
  page: ${me.index}
```

You'll see stuff like `#!yaml page: ${me.index}` all the time.
This just means that `state_1` will be `page: 0`, `state_2` will be `page: 1`, and so on (pages are zero-indexed).
If we didn't use templates here, we'd have to type out the page for each control.

### Assign gestures

Ok, now each control is assigned to a page, but pressing the control doesn't do anything.
That's because we still need to set the [gestures](../reference/command.md#gestures):

```yaml title="named_controls.yaml" hl_lines="5-7"
__page_changer:
  includes: [state_1, state_2, state_3, state_4, state_5, state_6, state_7, state_8]
  type: page
  page: ${me.index}
  gestures:
    pressed:
      page: ${me.index}
```

By using the [page command](../reference/command.md#page), our controls are now functional!

#### Peeking at pages

With a small addition to our gestures, we can hold a page control to "peek" at its page, and then release it to return to whatever page we were on before:

```yaml title="named_controls.yaml" hl_lines="8-9"
__page_changer:
  includes: [state_1, state_2, state_3, state_4, state_5, state_6, state_7, state_8]
  type: page
  page: ${me.index}
  gestures:
    pressed:
      page: ${me.index}
    released_delayed:
      page: last
```

### Assigning colors

We can customise the changer by setting the options [active_color](../reference/control/page.md#active_color) and [inactive_color](../reference/control/page.md#inactive_color):

```yaml title="named_controls.yaml" hl_lines="10-11"
__page_changer:
  includes: [state_1, state_2, state_3, state_4, state_5, state_6, state_7, state_8]
  type: page
  page: ${me.index}
  gestures:
    pressed:
      page: ${me.index}
    released_delayed:
      page: last
  active_color: white
  inactive_color: dark_grey
```

#### Individual colors

By [overriding the group definition](../reference/template.md#overwriting-options), we can set a particular color for some or all of the controls:

```yaml title="named_controls.yaml" hl_lines="5-9"
__page_changer:
    # ... config as above
    active_color: white
    inactive_color: dark_grey
    controls:
      state_1:
        inactive_color: pink
      state_6:
        inactive_color: red
    # etc...
```


## Final output

### Named controls version

```yaml title="named_controls.yaml"
__page_changer:
  includes: [state_1, state_2, state_3, state_4, state_5, state_6, state_7, state_8]
  type: page
  page: ${me.index}
  gestures:
    pressed:
      page: ${me.index}
    released_delayed:
      page: last
  active_color: white
  inactive_color: dark_grey
```

### Matrix section version

```yaml title="matrix_sections.yaml"
page_changer_section:
  row_start: 0 # the top matrix row
  row_end: 0
  col_start: 0
  col_end: 7
  template:
      type: page
      page: ${me.index}
      gestures:
        pressed:
          page: ${me.index}
        released_delayed:
          page: last
      active_color: white
      inactive_color: dark_grey
```

_No need to create `matrix_sections/page_changer_section.yaml`_
