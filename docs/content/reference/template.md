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

A property is some value that is associated with a particular control. You can see the properties associated with each control in the [control reference](control/standard.md#properties).

We can see from the control reference that `me.Index` refers to this control's [position](control/standard.md#index) with its containing [section](../lessons/getting-started/zcx-concepts.md#matrix-sections).

### basic expressions

We can even execute simple Python expressions within the braces:

```yaml
gestures:
  presssed: PLAY ${me.Index + 8}  # PLAY 9
```

!!! note

    To read about how zcx handles user-supplied expressions safely, see [this lesson](../lessons/python-context.md).

### complex expressions

There may be times when then value you want to fill is impractical or impossible to write inside the braces. In this case you can use the `vars` option in your yaml config.

`vars` is a dict, where each key is the name of a variable, and each value is an expression. 
The variable will be assigned to the result of that expression. 
We can then reference that variable within a template string. For instance:

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

This is a [control template](#control-templates) that, when [applied to a matrix section](#whole-section-groups), will produce the following output:

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
    - If you want to declare a var that is just a string, without evaluating anything, you must do: `my_var: str("this is a string")`.

#### using props

An alternative to using a `vars` dict is to define a `props` dict:

```yaml
my_control:
  props:
    foo: some string
    bar: ${me.index}
    misc:
      pi: 3.14159
```

Key differences between `vars` and `props`:

- If props contain template strings, they will be evaluated only once when zcx loads and then cached.
    - Props using template strings may not reference other props (though they may reference vars)
- Props are referenced like `${me.props.foo}`, rather than just `${foo}` like you would for a var
    - You may nest other dicts in props, and access it with dot notation, e.g. `${me.props.misc.pi}` 
- You can declare a prop as a static string like `my_prop: my string` without wrapping the string in `str()`
- As props are pre-computed, they do not require computation of the entire vars dict every time they are referenced

### template locals

The following variables and functions can be accessed within template strings.

##### `zcx`

Provides access to a `ZcxApi` object. See [the source code](https://github.com/odisfm/zcx-core/blob/main/app/api_manager.py) for available properties and methods,

##### `song`

Provides access to the Live set's [song object](https://docs.cycling74.com/apiref/lom/song/).

##### `print(message: str)`

Allows you to write to the log. Mostly useful with [Python commands](command.md#python).

##### `msg(message: str)`

Briefly displays a message in the Live UI, like with the [msg command](command.md#msg).

##### `cxp_var(variable_name: str)`

Retrieves the current value of a [ClyphX Pro variable](https://www.cxpman.com/manual/core-concepts/#variables) if that variable is defined, or the Python `None` if it is not defined.
`variable_name` is the name of the ClyphX variable **without** the enclosing `%`s.

##### `this_cs`

Returns the name of this zcx script.

##### `sel_track`

Returns the name of the selected track.
Must be enclosed in double-quotes for use in a ClyphX Pro action list.

##### `ring`

Allows references to the enclosed tracks and scenes of the zcx [session ring](../lessons/session-ring.md#referencing-the-ring-from-template-strings).

- `ring.tracks[idx]` - get the name of the track at that column of the ring
- `ring.scenes[idx]` - get the zero-indexed scene number of the scene at that row of the ring
- `ring.height`, `ring.width` - get the height or width of the ring

##### `matrix`

Get information about the [matrix](../lessons/getting-started/zcx-concepts.md#matrix-controls) and its [pages](../lessons/getting-started/zcx-concepts.md#pages)

- `matrix.height`, `matrix.width` - get the height or width of the matrix
- `matrix.page` - the zero-indexed number of the current page
- `matrix.page_count` - the number of matrix pages
- `matrix.all_pages` - a list of page names (in order)
- `matrix.num_controls` - height * width

##### `modes`

Get information about [modes](../lessons/getting-started/zcx-concepts.md#modes)

- `modes.all` - a list of all mode names (active and inactive)
- `modes.active` - a list of active mode names
- `modes.state` - a dict, mapping mode name to boolean for active/inactive

##### `overlays`

Get information about [overlays](../lessons/overlays-layers.md#overlays)

- `overlays.all` - a list of overlay names (active and inactive)
- `overlays.active` - a list of active overlay names

## group templates

zcx allows you to define any arbitrary selection of controls as a **group** of controls. By grouping controls, we can apply a common configuration across all of them.

The syntax for defining a group is different for [named controls](../lessons/getting-started/zcx-concepts.md#named-controls) and [controls that are part of the matrix](../lessons/getting-started/zcx-concepts.md#matrix-controls).


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
    Do not confuse [matrix sections](../lessons/getting-started/zcx-concepts.md#matrix-sections) with groups.

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

Each of these dashes is a blank or 'null' entry in this list. By looking at `controls`, we can see that four controls belong to this group. Like [above](#overwriting-options), we are able to overwrite or extend individual group members:

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

#### whole-section groups

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

#### section templates

An alternative to [the above method](#whole-section-groups) is to define a template inside [matrix_sections.yaml](file/matrix-sections.md). To do so, add a `template` key:

```yaml hl_lines="6-7"
my_section:
  col_start: 0
  col_end: 7
  row_start: 0
  row_end: 7
  template:
    color: red
```

When supplying a section template, it is possible to omit the usual file `matrix_sections/<section name>.yaml`.
You may still choose to supply both.

### encoder groups

Encoders can be grouped just like button controls.
The main difference is that we use the key `encoders` for our overrides:

```yaml
__enc_row:
  includes: [enc_1, enc_2, enc_3, enc_4]
  binding: >
    ring(${me.index}) / VOL
  encoders:
    enc_2:
      binding:
        __shift: >
          "my cool track" / PAN
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
