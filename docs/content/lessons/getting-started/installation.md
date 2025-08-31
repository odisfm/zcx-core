---
weight: 0
---

# installing zcx

Installing zcx is super easy.

## get a distribution

A 'distribution' is what we call a finished release of a zcx script. It contains the 'core' of zcx, along with hardware-specific code that makes it work with your controller. 

[Click here to see the latest release for all maintained hardware.](https://www.github.com/odisfm/zcx-core/releases/latest)

Scroll to the bottom of that page and check the 'Assets' dropdown.

### my hardware isn't listed

No problem. Have a look at the [zcx-core discord server](https://discord.zcxcore.com) to see if there is a pre-release version available. There may be a distribution ready to go that just needs someone who actually owns the hardware to confirm it works. And if there isn't, feel free to put in a request for your hardware!

Alternatively, it is relatively easy to create a 'port' of zcx for your controller.
See [the lesson](../porting.md) for details.

## install the script

Each distribution comes as a .zip file. Unzip that file, and you'll see a folder with the same name. The directory structure looks like this:

``` hl_lines="3"
_zcx_push_1.zip/
├─ _zcx_push_1/
│  ├─ _zcx_push_1/
│  │  ├─ _config/
│  │  ├─ __init__.py
│  │  ├─ some_python_file.py
│  │  ├─ etc...
│  ├─ user_actions/

```

This highlighted folder is the 'root' folder of this zcx distro. 
Simply drag this folder into your Live `Remote Scripts` directory.

On macOS the default path is:

`'/Users/[username]/Music/Ableton/User Library/Remote Scripts'`

On Windows it's:

`\Users\[username]\Documents\Ableton\User Library\Remote Scripts`

You can rename the folder to whatever you like, and that's the name that shows up in Live's preferences. We include a leading underscore, because that should push it to the top of the control surface list. Feel free to remove it.

### optional: install the zcx user action

By installing the zcx user action, you can [control zcx from ClyphX action lists](../zcx-user-action.md).
Drag the contents of the `user_actions` folder into your ClyphX Pro user actions folder, which should be in `User Library/Remote Scripts/_user_actions`.

## activate the script

For our purposes, zcx functions like any other control surface script, so you should [follow the Live manual's instructions](https://help.ableton.com/hc/en-us/articles/209072009-Installing-third-party-remote-scripts) for that.

!!! note

    ClyphX Pro should always be in a higher slot than all zcx scripts. I reccomend installing ClyphX Pro in slot 1. It's ok if XT scripts (ClyphX Pro XTA-E) are below zcx scripts.

When you assign the script to a slot in Live's preferences, the script automatically loads.

You should set the MIDI in and out ports to the relevant hardware before assigning the script to a slot.

For your controller's input, check the boxes `Track` and `Remote`, and for the output `Track`, `Sync` , and `Remote`.

At this point, you may need to [reload the script](../reloading-control-surfaces.md).

### if your controller has a distinct 'user mode'

Many controllers, such as the Push and Launchpad have a 'Live' mode and a 'user' mode. 

When setting up the Input and Output of the zcx script, you must use the 'user mode' port.
For example, Push 1 has the MIDI inputs `Ableton Push (Live mode)` and `Ableton Push (User mode)` — use the latter.
You are able to use the 'Live' and 'user' modes of your controller by switching between them with the dedicated hardware button, though the official control surface and the zcx script will each need their own control surface slot.

For the Launchpad series, use the port `Launchpad X MIDI In` or similar, rather than the `DAW in` and `DAW out` ports.

If you have officially supported hardware, zcx should automatically handle switching the controller's mode. If it doesn't, [raise an issue](../reporting-bugs.md).

## explore!

Your zcx distribution comes with a carefully crafted demo config, put together by the maintainer for your hardware. It's designed to give a taste of zcx's capabilities out of the box, and be intuitive to edit. Once you're done with that, continue with this tutorial. :)
