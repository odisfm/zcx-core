# seeing changes in your zcx config

Any changes made to your zcx configuration will not be effective until the control surface script is reloaded. There are several ways to achieve this:

## reload ableton live 😡

Sucks to do, obviously. This should only be necessary if you are tinkering with the Python part of the script and screw things up (ask me how I know).

## reload the set 😒

cmd + S, then in the menu bar `File -> Open Recent Set -> <my cool set>.als`. Much better than reloading Live, but still sucks with heavier sets.

## manually reload zcx 😏

In Live's MIDI preferences, reassign the zcx slot to any other script, then select zcx again. **Note:** if a script throws too serious of an error, Live will not allow this script to be loaded until all control surface scripts are reloaded. The impacted zcx script will disappear from the dropdown. This probably won't happen, but since zcx is in alpha it's not impossible.

And if it does happen, it will require a full reload of Live, or...

## reload all scripts at will 😎

If you have the Ableton 12 beta, you can enable a special `Tools` item in the menu bar. In this menu is an option to `Reload MIDI Remote Scripts`, which has a hotkey assigned. It's an awful hotkey, and you might want to reassign it with BetterTouchTool, AutoHotkey, etc. This will reload all scripts connected, including ClyphX Pro.

**Note:** If you own a copy of Ableton 12, you are automatically eligible for the [beta](https://www.ableton.com/en/beta/) program.

[Here is a guide](https://www.youtube.com/watch?v=L8JdzM0Lg8o) on getting the beta and enabling this menu.
