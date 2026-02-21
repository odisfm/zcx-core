---
title: zcx
hide:
#  - toc
  - navigation
  - footer
---

# zcx core {: #about-heading }

Extending [ClyphX Pro from NativeKontrol](https://isotonikstudios.com/product/clyphx-pro/?srsltid=AfmBOoqqG4off70xaUpCuouiAf_Lg7eCxuyiNrYf7vlIRJFIul3UquE9), zcx turns the user mode of your matrix-equipped MIDI controller into a deeply customisable interface for Ableton Live.

zcx is similar to ClyphX Pro's X-Controls, but far more powerful.
Features include:

* Unlimited pages of controls
* A modes system, letting you change the behaviour of controls and encoders when a button is held
* Intelligent controls that provide contextual LED feedback
* Session view and keyboard view
* A powerful templating system
* Animated LED feedback
* Control of zcx from ClyphX Pro, e.g. via X-Clips
{: #about-pitch }

!!! warning ""
    zcx requires Ableton Live 12.1 or above and ClyphX Pro

<iframe width="960" height="540" src="https://www.youtube.com/embed/_xLHWf9I4Ak?si=HQpS_yxdPwB2NADP" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

[documentation :material-book:](docs.md){ .md-button .md-button--primary }

[download :fontawesome-brands-github:](https://github.com/odisfm/zcx-core/releases/latest){ .md-button .md-button--primary }

[discord :fontawesome-brands-discord:](https://discord.zcxcore.com){ .md-button .md-button--primary }


## hardware

zcx is currently maintained for these devices, with more planned:

* Ableton Push 1
* Ableton Push 2
* Akai APC40 mk2
* Akai APC mini mk2
* Novation Launchpad X
* Novation Launchpad Pro mk3
* Novation Launchpad Mini mk3
* [generic controllers](lessons/porting.md)

[If your device isn't here
](lessons/getting-started/installation.md/#my-hardware-isnt-listed)
___
## features

zcx scripts contain many features that are impractical or impossible to replicate natively in ClyphX Pro

### unlimited pages

With zcx, your controller's matrix can switch between any number of pages.
Each page may have a unique selection of controls, or you may have some controls that appear on many pages.

[see more](./lessons/getting-started/zcx-concepts.md#pages)

### built for modes

Any control can be defined as a modifier control.
When this control is held, other controls can alter their functionality, and encoders can be re-bound.

[see more](./lessons/getting-started/zcx-concepts.md#modes)

### intelligent controls

zcx features an array of specialised controls that display contextual LED feedback.

The [track control](./reference/control/track.md) binds to a specific track, and displays feedback about that track's state. 
The [param control](./reference/control/param.md) binds to almost any parameter in Live.

[see more](./reference/control/index.md)

### session view and keyboard view

zcx features [session view](./lessons/session-view.md), the familiar interface for launching clips.
Session view in zcx lets you target session view clips with action lists.

With [keyboard view](./lessons/keyboard.md), your zcx script can be played like an instrument.

### templating system

With zcx's templating system, you can apply a common definition across many controls.

[see more](./reference/template.md)

**[Go to top](#)**
