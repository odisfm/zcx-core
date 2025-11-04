---
weight: -5
---

# seeing changes in your zcx config

Any changes made to your zcx configuration will not be effective until the control surface script is reloaded.
There are two ways to reload zcx:

## hot reload

With a "hot reload", your config is reloaded without reloading the zcx application code.

A hot reload can be triggered via:

* The [hot_reload command](../reference/command.md#hot_reload)
* The [zcx user action](zcx-user-action.md#hot_reload)

!!! tip ""
    Each [demo configuration](getting-started/demo-tour/index.md) has a pre-configured hot reload button combination.

!!! note
    The hot reload feature is designed to speed up your workflow when creating your config.
    It should not be relied upon in a performance situation.

### unaffected by hot reload

The following config changes will require a [full reload](#full-reload) to take effect:

* Changes to the width and/or height of the [session ring](session-ring.md#resizing-the-ring).
* Changes to files in the `hardware/` directory. This is only relevant if you've [made your own port](porting.md).
* Changes to the keyboard's [MIDI channel](keyboard.md#midi-channel).

## full reload

With a full reload, all zcx code is restarted and then your config is loaded again.
There are several ways to achieve this, listed here from most to least tedious.

### restart ableton live

Quit Ableton Live and re-open it, reloading all control surface scripts.

### reload the set

Save your set and re-open it.
After saving, click "Open Recent Set" in the menu bar to easily reload the current set.
This will reload all control surface scripts.

### manually reload zcx

In Live's MIDI preferences, reassign the zcx slot to any other script, then select zcx again.
This will reload only the chosen zcx script.

### reload all scripts at will

If you have the Ableton 12 Beta, you can enable a special `Tools` item in the menu bar. 
In this menu is an option to `Reload MIDI Remote Scripts`, which has a hotkey assigned. 
This will reload all scripts connected, including ClyphX Pro.

**Note:** If you own a copy of Ableton 12, you are automatically eligible for the [beta](https://www.ableton.com/en/beta/) program.

[Here is a guide](https://www.youtube.com/watch?v=L8JdzM0Lg8o) on getting the beta and enabling this menu.
