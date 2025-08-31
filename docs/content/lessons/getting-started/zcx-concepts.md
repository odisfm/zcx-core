---
weight: 2
---

# zcx concepts

zcx uses a lot of jargon. Here is a quick guide to the most important concepts.

## ZControls

Roughly equivalent to an [X or G control from ClyphX Pro](https://www.cxpman.com/manual/using-midi-controllers/). 
You define ZControls in your configuration files and when you press them they trigger action lists or some other functionality.

### control definitions

```yaml
record:
  color: red
  gestures:
    pressed: SRECFIX 8
```

A control definition is a [yaml object](reading-zcx-configurations.md#keys-and-values) provided by you that describes how a control should behave.
Most control definitions will have the [keys](reading-zcx-configurations.md#objects) `color` and `gestures`.

#### gestures

Gestures are physical actions you can perform on a control to trigger a command. 
There are six gestures supported by zcx:

- **pressed** always fired immediately after a control is pressed
- **pressed_delayed** fires after the control is held for a short time
- **released** always fired immediately after a control is released
- **released_delayed** fired after a held control is released — will only fire after a `pressed_delayed` event
- **released_immediately** fired after a control that was **not** being held is released
- **double_clicked** fired after a control is pressed twice in quick succession

#### commands

Commands fire in response to gestures, and are usually a ClyphX Pro action list:

```yaml
gestures:
  pressed: DEV(SEL) ON
  released: DEV(SEL) OFF
```

Here, the gesture is the key, and the command is the value.

#### modes

Any control can be assigned as a modifier or 'mode' control.
A mode is just a keyword that can be on or off.
You can configure your other controls to behave differently depending on whether the mode is active or not.

```yaml
shift:
  gestures:
    pressed:
      mode_on: shift
    released:
      mode_off: shift
```

Above we see a control called `shift`.
It responds to the gestures `pressed` and `released`.
These gestures fire the `mode_on` and `mode_off` commands respectively.
The value for these commands is also `shift`.

So, whenever the control `shift` is held down, the mode `shift` is on.

```yaml
record:
  gestures:
    pressed: SRECFIX 8
    pressed__shift: SRECFIX 16
```

This `record` control has the `pressed` and `pressed__shift` gesture.
As you may have guessed, this control will fire the action list `SRECFIX 8` when pressed, unless the `shift` mode is active, in which case it does `SRECFIX 16`.

You can even require multiple modes for particular functionality:

```yaml
record:
  gestures:
    pressed__shift__select: SRECFIX 32
```

The names of these modes are completely arbitrary, but they must be defined in your `modes.yaml` file.

```yaml title="modes.yaml"
- shift
- select
- drums
```

### named controls and matrix controls

Although MIDI controllers come in all shapes and sizes, zcx is focused on controllers with a 'matrix' or grid of pads or buttons, such as the Ableton Push, Novation Launchpad, Akai APC, and  others like them. 
Because of this, zcx makes a distinction between controls that form the matrix, and those that don't.

#### named controls

These controls exist outside of the matrix. 
They can be given a simple name, and we can refer to them by that name throughout our configuration. 
Often, the control's name will be printed on the control.

```yaml
record:
  color: red
  gestures:
    pressed: SRECFIX 8
```

All named controls are defined in one place, `named_controls.yaml`:

```
zcx/
├─ _config/
│  ├─ named_controls.yaml
```

!!! note
    The names used in `named_controls.yaml` and `encoders.yaml` have already been mapped to MIDI messages sent by your hardware.

    To check the names of each control, look in the `hardware` folder.
    
    ```
    zcx/
    ├─ hardware/
    │  ├─ note_buttons.yaml
    │  ├─ cc_buttons.yaml
    ```

#### matrix controls

And obviously, these controls exist within the matrix. 
In our configuration we don't define them by name or coordinate, but by position within their containing `section`.


## matrix sections


A matrix section is a logical segment of the matrix, defined by row and column. 
These sections you define can be any size.

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

actions_top_left:   #   0 1 2 3
  col_start: 0      # 0 □ □ □ □
  col_end: 3        # 1 □ □ □ □
  row_start: 0      # 2 □ □ □ □
  row_end: 3        # 3 □ □ □ □
  
actions_top_right:  
  col_start: 4  
  col_end: 7  
  row_start: 0  
  row_end: 3

track_section:
  col_start: 0
  col_end: 7
  row_start: 4
  row_end: 7
```

The dimensions or **bounds** of the matrix are defined in `_config/matrix_sections.yaml`. 
However, each section then needs its own config file in `_config/matrix_sections/<section name>.yaml`.

So, looking at the above config, your config directory would have these files:

```
zcx/
├─ _config/
│  ├─ matrix_sections/
│  │  ├─ actions_top_left.yaml
│  │  ├─ actions_top_right.yaml
│  │  ├─ track_section.yaml
│  ├─ matrix_sections.yaml/

```

And in each of those files you define a list, containing a definition for every pad that belongs to that section:

```yaml title="actions_top_left.yaml"
# row 1
# col 1
- color: red
  gestures:
    pressed: METRO
# col 2
- color: blue
  gestures:
    pressed: SETPLAY
...
```

!!! info "Skeleton sections"
    The demo config that comes with zcx features several mostly-empty sections that are great for getting started, as they have a minimal control definition with helpful comments denoting the row and column of each control.

    Later, you may want to use [the generator](../../resources/matrix-gen.md) to create your own skeletons of custom size.

## pages

So matrix controls are contained within matrix sections, but there's one more layer: sections are contained within pages:


```yaml title="pages.yaml"
pages:
  main_page:
    - actions_top_left
    - actions_top_right
    - actions_bottom_double
  alt_page:
    - actions_top_left
    - actions_bottom_right
    - actions_bottom_left
    - actions_top_right
  ring_page:
    - ring_control
  blank_page:
    - blank_section
```

The pages system means that you can change your matrix controls entirely depending on the context.
By assigning controls to sections, and not directly to pages, we can have one section appear on multiple pages, or even on all of them, without defining the same control every time.

Matrix sections are always bound to their defined coordinates, which means while they can appear on multiple pages, they'll always be in the same place.

One thing we can't do is have sections on a page that overlap: 

```yaml title="matrix_sections.yaml"

big_section:
  col_start: 0
  col_end: 7
  row_start: 0
  row_end: 7

tiny_section:
  col_start: 0
  col_end: 1
  row_start: 0
  row_end: 1
```
```yaml title="pages.yaml"

my_page:
  - big_section
  - tiny_section    # not gonna fit :(
```

If you try to do this, zcx will throw an error.

!!! note "Named controls and pages"
    Only matrix controls are affected by page changes; named controls will behave the same way regardless of the current page.

## encoder mappings

zcx allows you to dynamically map encoders (knobs, faders, etc.) to parameters in Live. 
Targeting of parameters follows the same syntax as ClyphX Pro encoder bindings:

```yaml title="encoders.yaml"
tempo:
  binding: SEL / VOL
```

Encoders are also mode-aware:
```yaml
tempo:
  binding:
    default: SEL / VOL
    __shift: SEL / PAN
```

You can read more about encoder mappings in the [Encoder Reference](../../reference/encoder.md)

## control types

The most common type of control you'll use is the [standard ZControl](../../reference/control/standard.md). 
There are also special subclasses of control that offer extra functionality, often in the LED feedback they provide.

One class of control is the [page control](../../reference/control/page.md),  which is bound to a page you specify.
It shows one color when its bound page is in view, and another when it isn't. 
Another is the [transport](../../reference/control/transport.md) control: you can bind your `play` button to Live's transport, and it will turn green while the set is playing, and white when it stops.

See the [Control Reference](../../reference/control/index.md) to learn more about the different control types.

## templating

zcx features a powerful templating system that allows you to configure multiple controls at a time.
By using this system, you can make a change in one place and have it affect any number of controls, saving you time when creating and, later, updating your config.

Here is an example of the templating system:

```yaml title="named_controls.yaml"
__scene_buttons:
  includes: [scene_1, scene_2, scene_3, scene_4]
  gestures:
    pressed: SCENE ${me.Index}
```

This is a group definition.
We have grouped the buttons `scene_1` through `scene_4` under the `includes` key to apply a common definition to them.
There is one gesture defined, `pressed`, with the command (action list) `SCENE ${me.Index}`.

The `${me.Index}` is new syntax called a template string.
Behind the scenes, zcx will evaluate these strings so that the controls fire `SCENE 1` through `SCENE 4`.

The benefits of this system become apparent when we want to extend the control:

```yaml title="named_controls.yaml" hl_lines="5"
__scene_buttons:
  includes: [scene_1, scene_2, scene_3, scene_4]
  gestures:
    pressed: SCENE ${me.Index}
    pressed__select: SCENE SEL ${me.Index}
```

With just one line of yaml we have extended the definition for all four controls in the group.

### going further with templating

The purpose of this section is to provide a brief overview of template strings.
If you have explored the zcx demo config in your code editor, you would have seen many examples of them, so it's important to have _some_ idea what you're looking at.

After finishing this "Getting Started" tutorial, you might want to check out the [Template Reference](../../reference/template.md) for a deeper understanding of the templating system.
