zcx contains several features for applying a common definition across multiple controls, or for dynamically configuring a control based on factors such as its position in a group.

## control templates

```yaml title="control_templates.yaml"
__global__:
  color: 127

hold_warning:
  gestures:
    released_immediately: >
      MSG "You must hold this control to trigger it!"
```
```yaml hl_lines="3 7 8"
play:
  template: hold_warning
  # color: 127    __global__ property, overwritten
  color: green
  gestures:
    pressed_delayed: SETPLAY
    released_immediately: > # added from `hold_warning` template
      MSG "You must hold this control to trigger it!"
```

In `control_templates.yaml`, you may create a control definition that is available for any control to inherit from. Any properties defined on the template will be inherited on the child control. In the case of a conflict (the template and child define the same property), the child will overwrite the template.

There is also a special template called `__global__`. This definition will apply to every control in your zcx script. You can optionally prevent a control from inheriting from `__global__` like so:

```yaml
my_control:
  template: null
```

## group templates

zcx allows you to define any arbitrary selection of controls as a **group** of controls. By grouping controls, we can apply a common configuration across all of them.

The syntax for defining a group is different for [named controls](/tutorials/getting-started/zcx-concepts/#named-controls) and [controls that are part of the matrix](/tutorials/getting-started/zcx-concepts/#matrix-controls).


### named controls
```yaml title="named_controls.yaml"
__scene_group:
  includes: [scene_1, scene_2, scene_3, scene_4]
  color: red
  buttons:
    -
    -
    - color: blue
  gestures:
    pressed: SCENE ${me.group_Index}
```

For named controls, we create a new entry that starts with a double underscore (`__`). What follows the `__` is the group name, in this case `scene_group`. This group name is up to you.

The `includes` key is a list of controls that belong to this group. Each member of the group will inherit all properties defined on the group. In this case each control in the group will launch a scene, [relative to its position in that group](#template-strings).

#### overwriting properties

We can override some or all of the group's properties for each member. This is done via the `buttons` key:

```yaml
buttons:
    -
    -
    - color: blue
```

`buttons` is a list of control definitions. The first two items on the list are totally blank, meaning that no properties will be overwritten. The third entry specifies `color: blue`, which will overwrite the group's `color: red`, but it will **not** overwrite the scene launch action. We do not have to add an entry for the fourth control, as we are not overwriting the group definition.

### matrix controls

As matrix controls do not have names, the syntax used to group them is slightly different.

!!! note "Groups vs Sections"
    Do not confuse [matrix sections](tutorials/getting-started/zcx-concepts/#matrix-sections) with groups.

    Every matrix control inherently belongs to a matrix section. Groups can be used within a section, or ignored entirely.

Look at the config for hypothetical matrix section `actions_right.yaml`:

```yaml title="actions_right.yaml"
-
  color: yellow
  gestures:
    pressed: SEL / MUTE
-
  color: blue
  gestures:
    pressed: SEL / SOLO
-
  pad_group: my_pad_group
  color: purple
  gestures:
    pressed: ${me.group_Index} / SEL
  pads:
    -
    -
    -
    -

```

Here we have defined the first two controls in this section individually.

The third entry in the section has the key `pad_group`. This indicates that we're looking at the definition for a group named `my_pad_group` within this section

!!! note
    It is not required that `pad_group` be the first key in a group definition, though it is recommended for clarity.

    You are not required to give a pad group a name. It can be left nameless like so:
    ```yaml
    - 
      pad_group:
      color: purple
      ...
    ```

The `pads` key is required. This is a list, and every item in the list represents another member of the group. [As above](#overwriting-properties
), we can leave an entry empty to fully inherit from the group, or we can override certain properties on a particular group member.

## template strings
