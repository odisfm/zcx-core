---
title: APC mini mkII
template: demo-tour.html
---

## Overview

### Modes

This config comes with five main [modes](../zcx-concepts.md#modes) pre-configured.
These are `shift`, `volume`, `pan`, `send`, and `device`.

`volume`, `pan`, `send`, and `device` are set up [exclusively](../../../reference/file/preferences.md#exclusive_modes), so that enabling one will disable the others.
These modes determine the functionality of eight of the [faders](#encoders).

### Pages

This config comes with six [pages](../zcx-concepts.md#pages) pre-configured.
By looking at `pages.yaml`, we can see these pages are named `home_page`, `alt_page`, `session_view_page`, `keyboard_page`, `ring_devices_page`, and `blank_page`.

### Named controls

The eight buttons below the matrix are configured as a page changer; pressing each button will take you to a different matrix page.
The eight buttons to the right of the matrix are scene launch buttons.

#### shift_overlay

When holding `shift`, the [overlay](../../overlays-layers.md) `shift_overlay` is enabled, changing the function of these sixteen buttons.
The buttons `volume`, `pan`, `send`, and `device` will activate their associated [mode](#modes), which affects the [faders](#encoders).
The directional buttons will move the [session ring](../../session-ring.md).
The scene launch buttons will control their alternate function; the top four buttons are now [param controls](../../../reference/control/param.md), bound to the functions indicated by their label. The buttons `drum` and `select` have been left unassigned.
The button labelled "stop all clips" will do just that on a short press, and with a long press will stop all clips without quantization.

### Matrix pages

#### home_page

##### actions

Enter the first page by pressing the `volume` button.
The top-left quadrant is the [section](../zcx-concepts.md#matrix-sections) `actions_top_left`.
Opposite `actions_top_left` is `actions_top_right`.
Taking up the bottom half of the matrix is `actions_bottom_double`.

These three sections have been left mostly unconfigured.

#### alt_page

The top half of the matrix still features `actions_top_left` and `actions_top_right`. 
This demonstrates how we can have sections appear on multiple pages.

##### select_control

In the bottom-left is the section `select_control`.
It's full of [param controls](../../../reference/control/param.md) that show dynamic feedback.
In this case, every control is mapped to the currently selected track.
The top row controls the track's mute, solo, arm, and input monitoring state.

The second row is mapped to the first four devices on the selected track.
If the track has less than four devices, you will see that one or more controls are off.
Note that these controls are configured for top-level devices, i.e. not devices nested in racks.
By pressing a control, we can select the corresponding device.
By holding `shift`, these controls map to the bypass state of the devices.

The third and fourth rows are mapped to the first eight parameters of the currently selected device.
Pressing a control will toggle its parameter between its minimum and maximum.
While `shift` is held, the **next** eight parameters will be controlled.

##### track_control

In the bottom-right is the section `track_control`.
It features 16 [ring_track controls](../../../reference/control/ring_track.md) that are bound to tracks rightward of the session ring.
These dynamic controls give feedback about the playing, arm, and selection state of their bound track.
A short press will select the track, and a long press will arm it.
If your Live set has less than 24 tracks, one or more of these controls might appear off.

##### __session_view

The top six rows are occupied by zcx's session view.
This works much the same as APC's native session view.
Pressing a pad will launch the respective clip slot.
See the [session view lesson](../../../lessons/session-view.md) for more detail on configuring this section.

##### session_controls

The bottom two rows feature the section `session_controls`.
The top row are param controls, bound to those track's selection status.
The bottom row will set its respective track to a random color, which isn't particularly useful, but it's there to demonstrate how we can [target ring tracks with action lists](../../session-ring.md#referencing-the-ring-from-template-strings).

#### keyboard_page

This page features a full-size keyboard view for playing notes.
See the [keyboard view lesson](../../keyboard.md) to learn more about how it works.

##### keyboard_notes overlay

By long-pressing the `device` button, you can enable the `keyboard_notes` [overlay](../../overlays-layers.md), which occupies the top two rows of the matrix.

The first three buttons of the top row set the scale of Live's [Scale Mode](https://help.ableton.com/hc/en-us/articles/11425083250972-Keys-and-Scales-in-Live-12-FAQ), which is reflected on the keyboard.
The next two buttons decrease or increase the [keyboard's octave](../../keyboard.md#octave).
The next two buttons decrease or increase the tonic of Scale mode by one semitone.
The last button toggles the keyboard's [in key status](../../keyboard.md#in-key-chromatic).

In the second row, the first seven buttons set the keyboard's [note repeat status](../../keyboard.md#in-key-chromatic), while the final button toggle's [full velocity mode](../../keyboard.md#full-velocity).

#### ring_devices_page

This page features only one section `ring_devices`, which fills the whole page.
Again, this section deals with the eight ring tracks.
Each column has eight param controls to affect the first eight parameters of the first device of the relevant track.
Press a pad to toggle the parameter between its minimum and maximum.
Release a pad after a hold to toggle the parameter again.

#### blank_page

This page contains one section — `blank_section` — an 8x8 unconfigured grid.
It's a great place to start experimenting with zcx's capabilities.

## Encoders

`fader_9` controls the Main track's volume.

`fader_1` through `fader_8` have four bindings preconfigured, which can be set via the [shift overlay](#shift_overlay).

In `volume` mode, they control the volume of the eight tracks in the session ring.
In `pan` mode, they control the pan of those tracks.
In `send` mode, they control the first eight sends of the selected track.
In `device` mode, they control the first eight parameters of the selected device.
