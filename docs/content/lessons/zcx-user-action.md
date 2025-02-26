---
weight: -4
---

# Controlling zcx from ClyphX Pro

zcx ships with a suite of user actions for ClyphX Pro that allow you to control a zcx script from ClyphX. This means an individual script can be interacted with via any X-Trigger, such as an X-Clip, or an X-Control bound to another controller.

As of zcx v0.3.0, the user action allows you to set modes and change pages.

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

#### Page

Activate a particular page by name or number.

`ZCX <target script> PAGE 0`

`ZCX <target script> PAGE my_cool_page`

Or cycle through pages.

`ZCX <target script> PAGE NEXT`

`ZCX <target script> PAGE PREV`

#### Mode

Enable, disable, or toggle a zcx mode.

`ZCX <target script> MODE ON SHIFT`

`ZCX <target script> MODE OFF SHIFT`

`ZCX <target script> MODE TGL SHIFT`
