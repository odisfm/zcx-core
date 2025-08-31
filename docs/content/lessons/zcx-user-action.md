---
weight: -4
---

# Controlling zcx from ClyphX Pro

zcx ships with a suite of user actions for ClyphX Pro that allow you to control a zcx script from ClyphX. This means an individual script can be interacted with via any X-Trigger, such as an X-Clip, or an X-Control bound to another controller.

## Installing the user action

Releases of zcx from v0.3.0 include a folder named `_user_actions`. Simply drag the contents of this folder (`Zcx.py`) into the ClyphX Pro user actions folder. The location of this folder is `.../Ableton/User Library/Remote Scripts/_user_actions`. If this folder doesn't exist, create it.

## Using the action

Usage of the zcx action is like so:

`ZCX <target script> <command type> <command definition>`

E.g.

`ZCX zcx_push_1 PAGE NEXT`

`ZCX 2 MODE TGL SHIFT`

### Targeting a script

The zcx action requires a specific script to be targeted. You may target by either script name or slot number.

#### By name

`ZCX zcx_push_1 PAGE NEXT`

This is the name of the folder containing the zcx script (similar to as seen in Live’s preferences) with any leading underscores removed. E.g. a script in a folder called `_my_zcx_script` (shown as `my zcx script` in Live’s prefs) is targeted like `ZCX my_zcx_script`. If you change the name of the script (by renaming its folder), you will need to update every ClyphX action list that uses the old name.

#### By number

`ZCX 2 MODE TGL SHIFT`

This is the number of the control surface script slot the zcx script resides in. If you move this script to another slot, you will need to update every ClyphX action list that uses the old name.

### Available commands

#### PAGE

Activate a particular page by name or number.

`ZCX <target script> PAGE 0`

`ZCX <target script> PAGE my_cool_page`

Or cycle through pages.

`ZCX <target script> PAGE NEXT`

`ZCX <target script> PAGE PREV`

#### MODE

Enable, disable, or toggle a zcx mode.

`ZCX <target script> MODE ON SHIFT`

`ZCX <target script> MODE OFF SHIFT`

`ZCX <target script> MODE TGL SHIFT`

#### BIND

Manually re-bind a zcx encoder to a new target.
This works much the same as the [ClyphX Pro BIND action](https://www.cxpman.com/action-reference/global-actions/#bind-i-x).

The `encoder name` is the same one you'd use in [encoders.yaml](../reference/configuration-files/encoders.md).

The `mapping target` is any of the targets specified in the [Encoder Reference](../reference/encoder.md#mapping-targets).
The **entire** mapping target must be wrapped in double-quotes.

!!!warning "Quotes within mapping targets"
    
    A special syntax is required when using double-quotes **within** your mapping target, e.g. `"my track" / VOL`.
    You must replace all instances of the double-quote character (") with a _backtick_ (`).

    The mapping target `"my track" / DEV("my device") P1` becomes `` `my track` / DEV(`my device`) P1``

    _The backtick key is below the escape key._


`ZCX <target script> BIND <encoder name> "<mapping target>"`

`ZCX zcx_push_1 BIND enc_3 "SEL / PAN"`

```ZCX zcx_launchpad_x BIND enc_1 "`my track` / DEV(`my device`) P1"```

#### MSG

**Only on [Push 1](../reference/hardware/push-1.md)**

Write a message to the controller's display. The message must be enclosed in double-quotes.

`ZCX <target script> MSG "hello there"`

#### HW_MODE

Set the controller to either 'Live' or zcx mode.

`ZCX <target script> HW_MODE live`

`ZCX <target script> HW_MODE zcx`

#### REFRESH

Force a refresh of all controller feedback.

`ZCX <target script> REFRESH`

#### Color commands

These commands allow you to set the color on an individual control by [alias](../reference/control/standard.md#alias), as well as across an entire section or group of controls.
Allowable color values are an [int](../reference/color.md#midi-value) or a [named color](../reference/color.md#name).

##### set_color

Set the color of a named or aliased control.

`ZCX <target script> SET_COLOR my_control 124`

`ZCX <target script> SET_COLOR record red`

##### set_section_color

Set the color of every control in a [matrix section](getting-started/zcx-concepts.md#matrix-sections).

`ZCX <target script> SET_SECTION_COLOR actions_bottom_right cyan`

##### set_group_color

Set the color of every control in a [group of controls](../reference/template.md#group-templates).

`ZCX <target script> SET_GROUP_COLOR scene_buttons 127`

