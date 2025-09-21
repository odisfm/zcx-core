# Layers and overlays

In the [getting started tutorial](getting-started/zcx-concepts.md) you learned about [modes](getting-started/zcx-concepts.md#modes) and [matrix pages](getting-started/zcx-concepts.md#pages).
We can use both these concepts to have buttons on our MIDI controller perform different [commands](../reference/command.md) depending on the context.

By using **layers** and **overlays**, we can create even more complex control surfaces.

## Matrix sections and layers

You previously learned that two matrix sections that appear on the same page [cannot share the same coordinates](getting-started/zcx-concepts.md#intersecting-sections).
By using layers, we can have two sections on the same page even if they conflict.

Take this example:
```yaml title="matrix_sections.yaml" hl_lines="12"
big_section:
  row_start: 0
  row_end: 7
  col_start: 0
  col_end: 7

half_section:
  row_start: 4
  row_end: 7
  col_start: 0
  col_end: 7
  layer: 1
```

```yaml title="pages.yaml"
pages:
  home_page:
    - big_section
    - half_section
  alt_page:
    - big_section
```

`big_section` has reserved the full matrix, and `half_section` has reserved the bottom half of the matrix.

In the definition for `half_section`, we have specified `layer: 1`.
Since no `layer` was specified for `big_section`, it uses the default matrix layer: 0.

Now when we enter `home_page`, we can see the top half of `big_section`, and below it `half_section`.
When we enter `alt_page`, `half_section` is dismissed, and in its place is the bottom of `big_section`, which was previously obscured.

So, a higher layer number means a higher priority.
It is also valid to give matrix sections a negative layer index, i.e `layer: -1`.

## Overlays

Overlays are like a combination of modes and pages, but specifically for [named controls](../lessons/getting-started/zcx-concepts.md#named-controls), which are not affected by the page system.

An overlay is a collection of named control definitions, just like in `named_controls.yaml`.
When we enable the overlay, we associate any number of buttons with alternative control definitions.
When we disable the overlay, we return to the default definitions in `named_controls.yaml`.

### Defining overlays

First, we must edit `overlays.yaml`.
You will find it in your config directory.
If it is missing, create it.

```yaml title="zcx/_config/overlays.yaml"
overlays:
  my_overlay: {}
```

If you are using a newer zcx demo config, there will be one or more overlays defined under the `overlays` key.
Each entry in `overlays` is a dict.
Above, we defined a new overlay called `my_overlay`, and gave it an empty definition (the `{}` means an empty dict/object).

We must now create a new yaml file for our overlay.
This file goes in the `overlays/` folder inside your config folder.
Create the file `overlays/<overlay name>.yaml`

```yaml title="zcx/_config/overlays/my_overlay.yaml"
my_button:
  gestures:
    pressed:
      msg: This is the overlay button!
```

The overlay file works just like `named_controls.yaml`.
We specify a button name, and provide a [control definition](../lessons/getting-started/zcx-concepts.md#control-definitions).

### Enabling overlays

When zcx loads, all overlays are disabled.
It's up to us to define a control that activates and deactivates the overlay:

```yaml hl_lines="6-13" title="named_controls.yaml"
my_button:
  gestures:
    pressed:
      msg: This is the base button.

scales:
  gestures:
    pressed:
      overlay:
        enable: my_overlay
    released:
      overlay:
        disable: my_overlay
```

Now, while the button `scales` is held the overlay `my_overlay` is active.
When `my_button` is pressed, it will show the message `This is the overlay button!`
When we leave `my_overlay` and press `my_button` again it will show `This is the base button.`

### Multiple overlays

You can define and enable any number of overlays at the same time.
However, if two overlays define the same control, which takes priority?

By default, when this conflict occurs zcx will resolve it like so:

Of all the overlays that define the same control, one overlay will win arbitrarily.
For the other overlays, the conflicting control will not be enabled.
For all controls that don't conflict, the overlays will apply as normal.

This behaviour is likely not what you want, so we can resolve it manually by specifying a **layer** for each overlay:

```yaml title="overlays.yaml"
overlays:
  my_overlay:
    layer: 1

  other_overlay:
    layer: 2
```

If `my_overlay` and `other_overlay` both define the same control, and they are both enabled, `other_overlay` will win as it has a higher layer number.
So layers here work similarly to [matrix layers](#matrix-sections-and-layers), with a key difference:

The default layer is 1, and an overlay's layer cannot be lower than 1.
The default named controls definition (in `named_controls.yaml`) can be considered as layer 0.

### Disabling controls with an overlay

When an overlay is enabled, you may wish to disable the existing functionality of some controls in `named_controls.yaml`.
This can be done by providing a minimal definition in your overlay file:

```yaml title="overlays/my_overlay.yaml"
scene_1:
  color: 0
```

When this overlay is enabled, `scene_1`s LED will turn off, and as no `gestures` key was provided, it will not respond to any gestures.

### Automations

#### on_enter, on_leave

You may define a [command bundle](../reference/command.md#command-bundles) that is executed when the overlay is enabled or disabled.

```yaml title="overlays.yaml"
overlays:
  my_overlay:
    on_enter:
      cxp: METRO ON
    on_leave:
      cxp: METRO OFF
```

#### pages_in, pages_out

You may define a list `pages_in`.
This is a list of page names or page numbers (zero-indexed).
When entering a page in this list, the overlay will automatically be enabled:

```yaml title="overlays.yaml"
overlays:
  my_overlay:
    pages_in:
      - home_page
      - my_cool_page
```

When `home_page` or `my_cool_page` is entered, `my_overlay` will be automatically enabled.
With a `pages_in` key, by default, the overlay will be disabled if we enter a page that **isn't** listed here.

We can override this behaviour with a `pages_out` key:

```yaml title="overlays.yaml" hl_lines="6-7"
overlays:
  my_overlay:
    pages_in:
      - home_page
      - my_cool_page
    pages_out:
      - my_cool_page
      - alt_page
```

`my_overlay` will now be enabled upon entering `home_page` or `my_cool_page`.
It will be disabled when **leaving** the pages `my_cool_page` or `alt_page`, but **not** `home_page`

You may define a `pages_out` without `pages_in`.

### Pitfalls

#### Design

It is entirely possible to create an overlay that cannot be escaped like so:

```yaml title="named_controls.yaml"
my_control:
  gestures:
    pressed:
      overlay:
        enable: my_overlay
    released:
      overlay:
        disable: my_overlay
```

```yaml title="overlays/my_overlay.yaml"
my_control:
  gestures: METRO ON
```

When `my_control` is pressed `my_overlay` will be enabled.
But `my_overlay` overrides `my_control`.
As we can never release the **default** `my_control`, we are now stuck in `my_overlay`.

zcx will **not** check for any scenario like the above, so you will need to carefully plan your overlays.

#### Control names

When getting a control by name, i.e. from the zcx [user action](zcx-user-action.md), you need to use a special name to get a control that is part of an overlay.

This name is just the base control name suffixed with the overlay name.
So with a button called `my_button` and an overlay called `my_overlay`, you would use the name `my_button_my_overlay`.

You can also refer to a control by its [alias](../reference/control/standard.md#alias).

#### Group names

The [names of control groups](../reference/template.md#group-templates) must be unique within `named_controls.yaml` and any overlay yaml files.
