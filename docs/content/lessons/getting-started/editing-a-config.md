---
weight: 4
hide:
  - footer
---

# editing a config

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non semper ligula. Maecenas lobortis mi non eros elementum, non convallis justo rutrum. Proin imperdiet massa maximus, hendrerit turpis a, accumsan augue. Vivamus lacinia luctus felis, vel auctor lorem. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Nam quis est ligula. Nunc vitae venenatis erat. Suspendisse congue ligula nisi, non lobortis elit venenatis sagittis. Etiam imperdiet ac metus a finibus. Suspendisse ex purus, ultrices sed ligula eu, sollicitudin varius purus. Proin sapien mi, vestibulum a accumsan sit amet, molestie nec sem. Ut eget efficitur lacus. Aenean ultrices, odio vel suscipit ullamcorper, tortor massa lobortis mi, ut pulvinar odio diam vitae magna.


!!! tip
    Use the VS Code shortcut `Cmd/Ctrl + /` to quickly comment or un-comment the selected line of yaml.
    Use this shortcut with multiple lines highlighted to affect all of them at once.


## ungrouping controls

The demo config will have several control group definitions:

```yaml title="named_controls.yaml"
__scene_controls:
  includes:
    [scene_1, scene_2, scene_3, scene_4]
  color:
    palette: coral
  gestures:
    pressed: >
      SCENE ${ring.scenes[me.Index]}
    pressed__shift: >
      SCENE ${ring.scenes[me.Index + me.group_count]}
    pressed__select: >
      SCENE SEL ${ring.scenes[me.Index]}
    pressed__shift__select: >
      SCENE SEL ${ring.scenes[me.Index + me.group_count]}

#scene_1:
#  color: 127
#  gestures:
#    pressed: DUMMY

#scene_2:
#  color: 127
#  gestures:
#    pressed: DUMMY

#scene_3:
#  color: 127
#  gestures:
#    pressed: DUMMY

#scene_4:
#  color: 127
#  gestures:
#    pressed: DUMMY
```

The key `__scene_controls` is a group definition that includes `scene_1` through `scene_4`.
To remove this group definition and define each control separately, first comment out (or delete) the group definition:

```yaml title="named_controls.yaml"
#__scene_controls:
#  includes:
#    [scene_1, scene_2, scene_3, scene_4]
#  color:
#    palette: coral
#  gestures:
#    pressed: >
#      SCENE ${ring.scenes[me.Index]}
#    pressed__shift: >
#      SCENE ${ring.scenes[me.Index + me.group_count]}
#    pressed__select: >
#      SCENE SEL ${ring.scenes[me.Index]}
#    pressed__shift__select: >
#      SCENE SEL ${ring.scenes[me.Index + me.group_count]}
```

Under each group definition is a definition for each group member that has been commented out.
Simply un-comment these definitions and start defining your controls.

```yaml title="named_controls.yaml"
scene_1:
  color: 127
  gestures:
    pressed: DUMMY

scene_2:
  color: 127
  gestures:
    pressed: DUMMY

scene_3:
  color: 127
  gestures:
    pressed: DUMMY

scene_4:
  color: 127
  gestures:
    pressed: DUMMY
```

## defining matrix sections and pages

### defining the sections

Let's define a new matrix page with two sections.
The first section will take up the top half of the matrix, and the second section the bottom half.
This example assumes an 8x8 matrix.

```yaml title="matrix_sections.yaml"
#       0  □ □ □ □ □ □ □ □
#       1  □ □ □ □ □ □ □ □
#       2  □ □ □ □ □ □ □ □
#       3  □ □ □ □ □ □ □ □
#       4  □ □ □ □ □ □ □ □
#       5  □ □ □ □ □ □ □ □
#       6  □ □ □ □ □ □ □ □
#       7  □ □ □ □ □ □ □ □
#          0 1 2 3 4 5 6 7
#

blank_section:
  row_start: 0
  row_end: 7
  col_start: 0
  col_end: 7

# ... more matrix sections
```

Looking at the graphic at the top of `matrix_sections.yaml`, we can see the top half starts spans from column 0 to 7, and from row 0 to 3.
Let's make a new section called `example_top_half` with these boundaries.

```yaml title="matrix_sections.yaml" hl_lines="1-5"
example_top_half:
  row_start: 0
  row_end: 3
  col_start: 0
  col_end: 7

blank_section:
  row_start: 0
  row_end: 7
  col_start: 0
  col_end: 7

# ... more matrix sections
```

Now add `example_bottom_half`:

```yaml title="matrix_sections.yaml" hl_lines="7-11"
example_top_half:
  row_start: 0
  row_end: 3
  col_start: 0
  col_end: 7

example_bottom_half:
  row_start: 4
  row_end: 7
  col_start: 0
  col_end: 7

```

You will need to create the files `example_top_half.yaml` and `example_bottom_half.yaml` inside the `matrix_sections/` folder:

``` hl_lines="6-7"
zcx/
├─ _config/
│  ├─ matrix_sections/
│  │  ├─ actions_top_left.yaml
│  │  ├─ actions_top_right.yaml
│  │  ├─ example_bottom_half.yaml
│  │  ├─ example_top_half.yaml
│  │  ├─ track_section.yaml
│  ├─ matrix_sections.yaml/
```

As each section contains 32 controls, zcx will expect each section yaml file to be a [list](reading-zcx-configurations.md#lists) of 32 control definitions.
Creating this list manually is quite tedious, so use the [matrix skeleton generator](../../resources/matrix-gen.md) to generate a skeleton 4 rows tall and 8 columns wide.
After generating the config use the :material-content-copy: in the output field to copy the yaml and paste it into your new yaml files.

```yaml title="matrix_sections/example_top_half.yaml"
# !! row 1
# col 1
- 
  color: 95
  type: standard
  gestures:
    released_immediately: DUMMY
    pressed_delayed: DUMMY

# col 2
- 
  color: 51
  type: standard
  gestures:
    released_immediately: DUMMY
    pressed_delayed: DUMMY

# col 3
- 
  color: 71
  type: standard
  gestures:
    released_immediately: DUMMY
    pressed_delayed: DUMMY
# and so on...
```

### placing them on a new page

We will place these new sections on a new page called `my_new_page`:

```yaml title="pages.yaml" hl_lines="15-17"
pages:
  home_page:
    - actions_left
    - actions_right
    - nav
    - actions_small
    - ring_tracks
  session_view_page:
    - select_control
    - nav
    - __session_view
    - ring_tracks
  blank_page:
    - blank_section
  my_new_page:
    - example_top_half
    - example_bottom half
```

In `pages.yaml`, add a new key to the [object](reading-zcx-configurations.md#objects) called `pages`.
This key should be called `my_new_page`, and its value should be a list of each section that appears on this page.

## adding a new mode

### defining the mode

Adding a new mode is easy.
First, add the name of your mode to the list in `modes.yaml`.
We'll call this new mode `my_mode`.

```yaml title="modes.yaml" hl_lines="3"
- shift
- select
- my_mode
```

We probably want to assign a control to this mode so we can turn it on and off.
In `named_controls.yaml`, create a new control definition.
Each demo config will have at least a couple of commented out definitions, so we can use one of those:

```yaml title="named_controls.yaml"
#scales:
#  gestures:
#    pressed: DUMMY
```

Un-comment this definition.
Change the `pressed` gesture so that it fires the `mode_on` command:

```yaml title="named_controls.yaml" hl_lines="3-4"
scales:
  gestures:
    pressed:
      mode_on: my_mode
```

Now add a `released` gestures with the `mode_off` command:

```yaml title="named_controls.yaml" hl_lines="5-6"
scales:
  gestures:
    pressed:
      mode_on: my_mode
    released:
      mode_off: my_mode
```

Now while the control `scales` is held, the mode `my_mode` is on.

### defining new gestures

We now need to make a control respond to this gesture.
Let's modify an existing control:

```yaml title="named_controls.yaml" hl_lines="4"
undo:
  gestures:
    pressed: UNDO
    pressed__my_mode: REDO
```

Now when the control `undo` is pressed it will fire the action list `UNDO`, or `REDO` if `my_mode` is enabled.
