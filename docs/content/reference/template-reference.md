---
weight: -9
---

# Template reference

zcx contains several features for applying a common definition across multiple controls, or for dynamically configuring a control based on factors such as its position in a group.

## template strings

In many parts of a control's config, you can use a special syntax to dynamically insert values into a string, such as an action list:

```yaml hl_lines="4 8 12" title="matrix_sections/very_small_section.yaml"
-
  color: red
  gestures:
    pressed: PLAY ${me.Index}
-
  color: green
  gestures:
    pressed: PLAY ${me.Index}
-
  color: blue
  gestures:
    pressed: PLAY ${me.Index}
```

The key part is `${me.Index}`. In zcx, when you see part of a string enclosed with a leading `${` and a trailing `}`, you are looking at a **template string**. zcx will dynamically evaluate this string **each time** the control is pressed.

The example above would evaluate to:

```
PLAY 1
PLAY 2
PLAY 3
```

Let's break down what's happening here.

- `${` — indicates the start of an expression
- `me` — is the individual control in which a template string appears
- `Index` — this is a **property** that belongs to this control
- `}` — indicates the end of an expression

As you may notice, zcx template strings behave similarly to [Variables in ClyphX Pro](https://cxpman.com/manual/core-concepts#variables).

### what is a property?

A property is some value that is associated with a particular control. You can see the properties associated with each control in the [control reference](/reference/control-reference/z-control#properties).

We can see from the control reference that `me.Index` refers to this control's [position](/reference/control-reference/z-control/#index_1) with its containing [section](/tutorials/getting-started/zcx-concepts#matrix-sections).

### basic expressions

We can even execute simple Python expressions within the braces:

```yaml
gestures:
  presssed: PLAY ${me.Index + 8}  # PLAY 9
```

### complex expressions

There may be times when then value you want to fill is impractical or impossible to write inside the braces. In this case you can use the `vars` option in your yaml config.

`vars` is a dict, where each key is a variable, and each value is an expression. The variable will be assigned to the result of that expression. We can then reference that variable within a template string. For instance:

```yaml
my_control:
  vars:
    foo: 1 + 1
  gestures:
    pressed:
      msg: The value of foo is ${foo} # "The value of foo is 2"
```

In ClyphX terms, you can imagine the above as: 

`%foo% = 1 + 1 ; msg "The value of foo is %foo%"`

Or in Python as:

```python
def button_pressed():
    foo = 1 + 1
    print(f'The value of foo is {foo}')
```

That was a very basic example to illustrate the concept. This example better explains a use case:

```yaml title="control_templates.yaml"
drum_pad_section:
  vars:
    offset: 8
    clips_per: 2
    clip_1a: (me.index * clips_per) + 1 + offset
    clip_1b: (clip_1a + clips_per) - 1
  gestures:
    released_immediately: >
      "beats" / PLAY RND${clip_1a}-${clip_1b}
```

This is a [control template](#control-templates) that, when [applied to a matrix section](#whole-section-templates), will produce the following ouput:

```
pad 1: "beats" / PLAY RND9-10
pad 2: "beats" / PLAY RND11-12
pad 3: "beats" / PLAY RND13-14
...
```

And later, we can easily expand this config to add extra functionality:

```yaml hl_lines="5 8 9 13 14"
drum_pad_section: 
  vars:
    offset: 8
    clips_per: 2
    shift_offset: 32
    clip_1a: (me.index * clips_per) + 1 + offset
    clip_1b: (clip_1a + clips_per) - 1
    clip_2a: clip_1a + shift_offset
    clip_2b: clip_2b + shift_offset
  gestures:
    released_immediately: >
      "beats" / PLAY RND${clip_1a}-${clip_1b}
    released_immediately__shift: >
      "beats" / PLAY RND${clip_2a}-${clip_2b}
```

``` hl_lines="2 4"
pad 1: "beats" / PLAY RND9-10
pad 1 (with shift): "beats" / PLAY RND41-42
pad 2: "beats" / PLAY RND11-12
pad 2 (with shift): "beats" / PLAY RND43-44
```

!!! note "Notes"
    - Variables defined in `vars` are calculated anew every time they are required, i.e. they do not persist between presses of a control.
    - You cannot reference ClyphX Pro variables from **inside an expression**, e.g. `PLAY ${ %my_num% + 10 }`, but you **can** combine zcx templating with [ClyphX variables](https://www.cxpman.com/manual/core-concepts/#variables), e.g. `%my_track% / PLAY ${me.Index}` 

## group templates

zcx allows you to define any arbitrary selection of controls as a **group** of controls. By grouping controls, we can apply a common configuration across all of them.

The syntax for defining a group is different for [named controls](/tutorials/getting-started/zcx-concepts/#named-controls) and [controls that are part of the matrix](/tutorials/getting-started/zcx-concepts/#matrix-controls).


### named controls
```yaml title="named_controls.yaml"
__scene_group:
  includes: [scene_1, scene_2, scene_3, scene_4]
  color: red
  controls:
    scene_2:
      color: blue
  gestures:
    pressed: SCENE ${me.group_Index}
```

For named controls, we create a new entry that starts with a double underscore (`__`). What follows the `__` is the group name, in this case `scene_group`. This group name is up to you.

The `includes` key is a list of controls that belong to this group. Each member of the group will inherit all options defined on the group. In this case each control in the group will launch a scene, [relative to its position in that group](#template-strings).

#### overwriting options

We can overwrite some or all of the group's options for each member. This is done via the `controls` key:

```yaml
controls:
  scene_2:
    color: blue
```

`controls` is a dict of control definitions. Each key of `controls` is the name of a control in this group. In this `scene_2` key we can overwrite part or all of the group definition. We can also add options that weren't defined on the group:
```yaml hl_lines="4"
controls:
  scene_2:
    color: blue
    repeat: true
```

### matrix controls

As matrix controls do not have names, the syntax used to group them is slightly different.

!!! note "Groups vs Sections"
    Do not confuse [matrix sections](/tutorials/getting-started/zcx-concepts/#matrix-sections) with groups.

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
  controls:
    -
    -
    -
    -
-   
  color: pink
  gestures:
    pressed_delayed: METRO

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

The `controls` key is required. This is a list, and every item in the list represents another member of the group:
```yaml
controls:
  -
  -
  -
  -

```

Each of these dashes is a blank or 'null' entry in this list. By looking at `controls`, we can see that four controls belong to this group. Like [above](/reference/template-reference/#overwriting-options), we are able to overwrite or extend individual group members:

```yaml
controls:
  -
  -
  - color: green
  -

```

Now all controls in this group will take the group definition, except the third control, which will be purple.

This is a representation of how zcx processes this section under the hood:

```yaml hl_lines="19"
-
  color: yellow
  gestures:
    pressed: SEL / MUTE
-
  color: blue
  gestures:
    pressed: SEL / SOLO
# group definition is expanded
-
  color: purple
  gestures:
    pressed: 1 / SEL
-
  color: purple
  gestures:
    pressed: 2 / SEL
-
  color: green  # this option was overwritten
  gestures:
    pressed: 3 / SEL
-
  color: purple
  gestures:
    pressed: 4 / SEL
# group definition ends
-   
  color: pink
  gestures:
    pressed_delayed: METRO
```

#### whole-section templates

It is possible to define an entire matrix section with one group definition. To do this, the yaml file for the section should contain a single dict, instead of the usual list:

```yaml title="big_section.yaml"
pad_group:
color: pink
gestures:
  pressed: CLIP PLAY ${me.Index}
```

This template will be applied for every control in the section. You can imagine the expanded output like this:

```yaml
-
  color: pink
  gestures:
    pressed: CLIP PLAY 1
-
  color: pink
  gestures:
    pressed: CLIP PLAY 2
-
  color: pink
  gestures:
    pressed: CLIP PLAY 3
...
```

## control templates
In `control_templates.yaml`, you may create a control definition that is available for any control to inherit from. Any options defined on the template will be inherited on the child control. In the case of a conflict (the template and child define the same option), the child will overwrite the template.

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
  # color: 127    __global__ option, overwritten
  color: green
  gestures:
    pressed_delayed: SETPLAY
    released_immediately: > # added from `hold_warning` template
      MSG "You must hold this control to trigger it!"
```

There is also a special template called `__global__`. This definition will apply to every control in your zcx script. You can optionally prevent a control from inheriting from `__global__` like so:

```yaml
my_control:
  template: null
```

### multiple inheritance

You can apply multiple templates sequentially to a control, like so:

```yaml
my_control:
  template: [foo, bar, baz]
```

```yaml title="control_templates.yaml"
__global__:
  color: 127

foo:
  color: red
  gestures:
    pressed: msg "I was pressed!"

bar:
  color: blue
  gestures:
    released: msg "I was released!"
  
baz:
  color: pink
```

This config will result in this control:

```yaml
my_control:
  color: pink
  gestures:
    pressed: msg "I was pressed!"
    released: msg "I was released!"
```

Notice that all four templates defined a `color` option.

When using multiple templates, zcx merges the template definitions from left to right, in the same order you define them in.
When the same option is defined on multiple templates, and the difference is irreconcilable, the **rightmost** template wins.
In this case, the control is `pink`.

`foo` and `bar` both have a `gestures` key, but the gestures defined within are compatible, and so `my_control` gets both the `pressed` and `released` gesture.
