---
title: Launchkey mk4
template: demo-tour.html
---

## Overview

### Modes

This config comes with one main [mode](../zcx-concepts.md#modes) pre-configured.
This mode is called `shift`, and is assigned to the `function` button.

**Note:** the button labeled `shift` continues to perform its default function, and is not assignable to zcx.
In this article, when we say "with `shift` held", we are referring to the _mode_ `shift`.

There are two other groups of [exclusive modes](../../../reference/file/preferences.md#exclusive_modes); `eb_1` and `eb_2`, and also `fb_1` through `fb_8`.
We will cover these modes [later](#encoders).

### Pages

This config comes with four [pages](../zcx-concepts.md#pages) pre-configured.
By looking at `pages.yaml`, we can see these pages are named `home_page`, `session_view`, `device_control`, and `blank_page`.
The controls to the left of the pads, `pad_bank_up` and `pad_bank_down`, are used to switch between the pages.
You can quickly change to the first or last page by holding these buttons.

The top row of the Launchkey's display will show the current page name.

### Named controls

The controls `track_left` and `track_right` (`track_left_m` and `track_right_m` on smaller models) change the selected track.
With `shift` held, these controls will move the [session ring](../../session-ring.md).

The control `scene_launch` (labeled ❯) will launch the scene at the top of the session ring.

To the right, the controls `capture`, `undo`, `quantize`, `metronome`, `play`, `record`, and `loop` will perform their normal functions.
`stop` is a [param control](../../../reference/control/param.md) that will stop the selected track.

Next to the encoders, the controls `enc_bank_up` and `enc_bank_down` (`enc_bank_up_m` and `enc_bank_down_m` on smaller models) will toggle between the modes `eb_1` and `eb_2`, changing the function of the [encoders](#encoders).

### 49 and 61-key only

Below the faders, `fb_1` through `fb_8` are [ring_track controls](../../../reference/control/ring_track.md), which control tracks associated with the session ring, and display LED feedback representing their state.

Pressing a control will select that track, while holding a control will arm that track exclusively.
Holding a control with `shift` will arm the track non-exclusively, and double-clicking the control will play the track's next clip.

`fb_9` will toggle the [overlay](../../overlays-layers.md) `fader_bank_select`, allowing you to change the binding of the [faders](#faders).

### Matrix pages

#### home_page

The first page contains the section `actions_main`, which has been left mostly unconfigured.

#### session_view

This page contains the [session view](../../session-view.md).
Pressing a clip with `shift` held will select that clip.
Pressing the page controls with `shift` held will move the session ring.

By double-clicking `function`, you can switch between the [overlays](../../overlays-layers.md) `session_mute`, `session_solo`, and `session_stop`, letting you use the bottom row of pads to mute, solo, or stop the respective track.

#### device_control

This page features the section `device`.
This section is made up of [param controls](../../../reference/control/param.md).

The top row lets you change the track's selected device.
The bottom row will toggle the first eight parameters on that device.

#### blank_page

This page contains `blank_section`, an 8x2 unconfigured grid.
It's a great place to start experimenting with zcx's capabilities.

## Encoders

### Knobs

The eight knobs control the parameters of the selected device.
By using the ˄ and ˅ buttons next to the knobs, you can toggle between controlling the first or second bank of parameters.
Pressing these controls while holding `shift` will move between devices on the current track.

### Faders

_49 and 61-key models only_

By default, `fader_1` through `fader_8` control the volume of the tracks inside the session ring, while `fader_9` controls the Main track's volume.

By pressing `fb_9` (below `fader_9`), you will activate the `fader_bank_select` overlay.
With this overlay, controls `fb_1` through `fb_8` will activate the _modes_ `fb_1` through `fb_8`, re-binding the faders.

**Note:** [encoders.yaml](../../../reference/file/encoders.md) only has a pre-configured binding for `fb_1`.
It is up to you to add additional bindings.

### Additional bindings for the knobs

You can use these same fader bank modes for the knobs.
To do so, your `encoders.yaml` would look something like this:

```yaml title="encoders.yaml"
__encoders:
  includes: [enc_1, enc_2, enc_3, enc_4, enc_5, enc_6, enc_7, enc_8]
  sensitivity: 4.0
  binding:
    default: NONE
    __fb_1__eb_1: >
      SEL / DEV(SEL) B1 P${me.Index}
    __fb_1__eb_2: >
      SEL / DEV(SEL) B2 P${me.Index}
    __fb_2__eb_1: >
      RING(${me.index}) / VOL
    __fb_2__eb_2: >
      RING(${me.index}) / PAN
    __fb_3__eb_1: >
      RING(${me.index}) / SEND A
    __fb_3__eb_2: >
      RING(${me.index}) / SEND B
```

With a configuration like this, you can easily set up 16 different banks of encoders.
