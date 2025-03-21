---
weight: 2
---

# zcx concepts

zcx uses a lot of jargon. Here is a quick guide to the most important concepts.

## ZControls

Roughly equivalent to an [X or G control from ClyphX Pro](https://www.cxpman.com/manual/using-midi-controllers/) (first party controls). Original, I know. You define ZControls in your configuration file and when you press them they trigger action lists. Like with first party controls, you can configure the control's color. However, ZControls can have many additional options that give you more control(!) over how they behave. There are even special subclasses of controls that offer specific functionality. More on that [later](#control-classes).

Although MIDI controllers come in all shapes and sizes, zcx is focused on controllers with a 'matrix' or grid of pads or buttons, such as the Ableton Push, Novation Launchpad, Akai APC, and  others like them. Because of this, zcx makes a distinction between controls that form the matrix, and those that don't.

### named controls

These controls exist outside of the matrix. That means they perform the same functions regardless of what [page](#pages) the matrix is on. They can be given a simple name, and we can refer to them by that name throughout our configuration. Often, the control's name will be printed on the control.

```yaml
record:
  color: red
  gestures:
    pressed: SRECFIX 8
```

**Note:** while named controls are unaffected by page changes, they _are_ affected by [modes](#modes).

These names have been mapped to MIDI messages already by the zcx maintainer for your hardware. The 'canonical' names for each control should be included in the documentation of your distribution. You can always find these names (and change them) in the following locations:

```
zcx/
├─ hardware/
│  ├─ note_buttons.yaml
│  ├─ cc_buttons.yaml
```

All named controls are defined in one place, `named_controls.yaml`:

```
zcx/
├─ _config/
│  ├─ named_controls.yaml
```


### matrix controls

And obviously, these controls exist within the matrix. In our configuration we don't define them by name or coordinate, but by position within their containing `section`.

What is a section, you ask?


## matrix sections


A matrix section is a logical segment of the matrix, defined by row and column. These sections you define can be any size.

```yaml
# matrix_sections.yaml

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

The dimensions or **bounds** of the matrix are defined in `_config/matrix_sections.yaml`. However, each section then needs its own config file in `_config/matrix_sections/<section name>.yaml`.

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

And in each of those files you define every pad that belongs to that section:

```yaml
# row 1
# col 1
- color: red
  gestures:
    pressed: METRO
# col 2
- color: blue
  gestures:
    pressed: SETPLAY
```

Or you can have [one definition that applies to all pads](/reference/template-reference/#whole-section-templates) based on their position within the section:

```yaml
# scene_section.yaml

color:
  palette: rainbow
gestures:
  pressed: SCENE ${me.Index} 
  # `SCENE 1` for pad 1, `SCENE 2` for pad 2...
  pressed__select: SCENE SEL ${me.Index}
```

!!! tip
    You will learn more about defining matrix controls in [the next lesson](/tutorials/getting-started/editing-a-config).

## pages

There's a good chance pages are why you're interested in zcx in the first place. Pages contain sections which contain controls. Because of this, we can turn an 8×8 pad matrix into an 8×8×∞ matrix. This system allows you to design a multi-mode control surface script, like the one that shipped with your controller, while harnessing the power of ClyphX — all without learning Python!

```yaml
# pages.yaml

pages:  
  main:  
    - big_colors  
  test_page:  
    - actions_top_left  
    - actions_bottom_right  
    - actions_bottom_left  
    - actions_top_right  
  track_page:  
    - actions_top_left  
    - mega_launcher  
    - track_half
```

By assigning controls to sections, and not directly to pages, we can have one section appear on multiple pages, or even on all of them, without defining the same control every time.

One thing we can't do is have sections on a page that overlap: 

```yaml
# matrix_sections.yaml

big_bad_section:
  col_start: 0
  col_end: 7
  row_start: 0
  row_end: 7

teeny_tiny_section:
  col_start: 0
  col_end: 1
  row_start: 0
  row_end: 1

# pages.yaml

my_page:
  - big_bad_section
  - teeny_tiny_section    # not gonna fit :(
```

If you try to pull this type of move, zcx will yell at you and refuse to run.

!!! warning
    Matrix sections are always bound to their defined coordinates, which means while they can appear on multiple pages, they'll always be in the same place.


## modes

Any control can be assigned as a modifier or 'mode' control.

```yaml
shift:
  gestures:
    pressed:
      mode_on: shift
    released:
      mode_off: shift

record:
  gestures:
    pressed: SRECFIX 8
    pressed__shift: SRECFIX 16
```

A mode is just a keyword we can activate, and when activated we can enable different functionality on our controls like you see above.

You can even require multiple modes for particular functionality:

```yaml
record:
  gestures:
    presssed__shift__select: SRECFIX 64
```

The names of these modes are completely arbitrary, but they must be defined in your `modes.yaml` file.
```yaml
# modes.yaml

- shift
- select
- drums
```

## ZEncoders

ZEncoders allow you to dynamically map encoders (knobs, faders, etc.) to parameters in Live. [With some exceptions](https://github.com/odisfm/zcx-core/releases/tag/v0.2.0-alpha.1), targeting of parameters with ZEncoders follows the same syntax as ClyphX encoder bindings:

```yaml
# encoders.yaml

tempo:
  binding: SEL / VOL
```

ZEncoders are also mode-aware:
```yaml
tempo:
  binding:
    default: SEL / VOL
    __shift: SEL / PAN
```


## control classes

The most common type of control you'll use is the default or [standard ZControl](/reference/control-reference/z-control). There are also special subclasses of control that offer extra functionality, often in the LED feedback they provide.

One class of control is the [page control](/reference/control-reference/page),  which is bound to a page you specify. It shows one color when its bound page is in view, and another when it isn't. Another is the [transport](/reference/control-reference/transport) control: you can bind your `play` button to Live's transport, and it will turn green while the set is playing, and white when it stops. Just like it did on the original script for your controller.
