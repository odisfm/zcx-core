# zcx-core

 Piggybacking on [ClyphX Pro from NativeKontrol](https://isotonikstudios.com/product/clyphx-pro/?srsltid=AfmBOoqqG4off70xaUpCuouiAf_Lg7eCxuyiNrYf7vlIRJFIul3UquE9), zcx turns your matrix-equipped MIDI controller into a deeply customisable interface for Ableton Live. It offers an alternative configuration system that makes heavy use of [yaml](https://www.redhat.com/en/topics/automation/what-is-yaml#:~:text=YAML%20is%20a%20human%2Dreadable,is%20for%20data%2C%20not%20documents.) files and templating to allow rapid prototyping of new ideas. It aims to enable musicians to program more ambitious controller setups with less work than it took before.


## hardware

zcx-core is currently maintained for these devices, with more planned:

* Ableton Push 1
* Ableton Push 2
* APC mini mk2

### [get it here!](https://github.com/odisfm/zcx-core/releases/latest)


___
## features

zcx scripts contain many features that are impractical or impossible to replicate natively in ClyphX

### built for modes
```yaml
record:
  color: red
  gestures:
    pressed: SEL / ARM ON
    pressed__shift: SEL / STOP
    pressed_delayed: SREC  8
    pressed_delayed__shift: SREC 16
    pressed__shift__select: SETSTOP

shift:
  gestures:
    pressed:
      mode_on: shift
    released:
      mode_off: shift
select:
  gestures:
    pressed:
      mode_on: select
    released:
      mode_off: select
```

Easily define any control as a modifier for any other control.

### rapid configuration
```yaml
# matrix_sections.yaml

clip_section:
  col_start: 0
  col_end: 7
  row_start: 0
  row_end: 7

# matrix_sections/clip_section.yaml

color:
  palette: nebula
gestures:
  pressed: SEL / PLAY ${me.Index}
```

```output
pad 1: SEL / PLAY 1
pad 2: SEL / PLAY 2
..
pad 64: SEL / PLAY 64
```

Configure dozens of buttons in seconds.

### deeper customisation
```yaml
play:
  color:
    pulse:
      a: red
      b: purple
      speed: 1
  gestures:
    double_clicked: STOPALL NQ
```

Unlock the full capabilities of your hardware.

### intelligent controls
```yaml
__state_row:
  includes: [
	state_1, state_2, state_3, state_4
  ]
  type: page
  page: ${me.index}
  gestures:
    pressed:
      page: ${me.index}

play:
  type: transport
  transport: play
  gestures:
    pressed: SETPLAY
```

Specialised control types give smart LED feedback without you writing any code.

### reusable components
```yaml
# control_templates.yaml

my_green_button:
  color: green shade ${me.index % 4}

hold_warning:
  gestures:
    released_immediately:
      msg: You must hold this control to trigger it!


# named_buttons.yaml

scene_1:
    template: [hold_warning, my_green_button]
    #color: green shade ${me.index % 4}
    gestures:
      pressed_delayed: SCENE 1
      #released_immediately:
       # msg: You must hold this control to trigger it!
```

Use templates instead of repeating definitions. Make a change in one place to see the differences across the whole control surface.

```yaml
# matrix_sections.yaml

home_row:
  col_start: 0
  col_end: 7
  row_start: 0
  row_end: 1

# pages.yaml

pages:
  main:
    - home_row
    - main_left
    - main_right
  track_page:
    - home_row
    - track_control
    - device_control
  drums:
    - home_row
    - drums_section
```
