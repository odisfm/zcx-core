---
title: Push 1
template: demo-tour.html
---

## Overview

### Modes

This config comes with nine [modes](../zcx-concepts.md#modes) pre-configured.
These modes are `shift`, `select`, `delete`, `volume`, `track`, `device`, `sends`, `browse`, and `clip`.
They are all mapped to controls of the same name (`sends` is mapped to the control `pan_send`).

Six of these modes, `volume`, `track`, `device`, `sends`, `browse`, and `clip` are set up [exclusively](../../../reference/file/preferences.md#exclusive_modes), so that enabling one will disable the others.

`shift` and `select` will only be active while they are held.

### Pages

This config comes with six [pages](../zcx-concepts.md#pages) pre-configured.
By looking at `pages.yaml`, we can see these pages are named `home_page`, `alt_page`, `session_view_page`, `ring_devices_page`, `keyboard_page`, and `blank_page`.
Push's eight `state` buttons have been configured as a group.
They are the multicolor buttons below the display, and they will each take you to a different page on a press.

As some buttons are unassigned, if you add a new page it will automatically be assigned to one of the free buttons.

### Named controls

Push's eight `select` buttons have been configured as a group.
They are [param controls](../../../reference/control/param.md), bound to the selection state of the eight tracks in view of the [session ring](../../session-ring.md).
Pressing one will select the relevant track, and the button will become brighter to indicate that.
Holding one of these buttons will arm the track exclusively, while pressing with `shift` will arm non-exclusively.
Holding a button while holding `delete` will delete the track.

Four [transport controls](../../../reference/control/transport.md) are configured, for the controls `play`, `record`, `metronome`, and `automation`.
These controls will indicate the status of the relevant transport function.
On a short press, `record` will fire the action list `SREC`, starting Live's session record.
On a long press, it will fire `SRECFIX 8`, starting session record for a fixed length of 8 bars.

Push's eight `scene` buttons have been configured as a group.
Pressing a scene button will launch the scene at that position of the session ring.
Pushing a scene button while holding `shift` will launch scenes below the ring.
Pushing a scene button while holding `select` will select the scene, but not launch it.
Pushing a scene button with both `shift` and `select` will select scenes below the ring.

The `undo` control trigger's Live's undo feature.

The `duplicate` control duplicates the selected scene.

The `new` control inserts a new scene.

`master` is another param control, bound to the selection status of the Main track.
`stop`, also a param control, is bound to the target `SEL / STOP`, and will be brighter when the selected track is playing (and can thus be stopped).

The controls `in` and `out` are found to the right of `master` and are marked with the ↪ and ↩ symbols.
Pressing these controls will move the session ring across by eight tracks.
When the mode `device` is active, a short press on these controls will move left and right through the devices on the selected track, while a long press will move to the first or last device.

`mute` and `solo` are both param controls, mapped to the functions you'd expect.

The controls `note` and `session` will enable the pages `keyboard_page` and `session_view_page` respectively.

The D-pad will move throughout the Live set.
If `shift` is held, the D-pad will move the session ring one step at a time.

### Matrix pages

#### home_page

##### actions

Enter the first page by pressing the first `state` button.
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

#### session_view_page

##### __session_view

The top six rows are occupied by zcx's session view.
This works much the same as the Push's native session view.
Pressing a pad will launch the respective clip slot.
Pressing a pad with `select` held will select the slot.
Pressing a pad with `delete` held will delete the clip in that slot.
See the [session view lesson](../../../lessons/session-view.md) for more detail on configuring this section.

##### session_controls

The bottom two rows feature the section `session_controls`.
The top row are param controls, bound to those track's selection status.
The bottom row will set its respective track to a random color, which isn't particularly useful, but it's there to demonstrate how we can [target ring tracks with action lists](../../session-ring.md#referencing-the-ring-from-template-strings).

#### keyboard_page

This page features a full-size keyboard view for playing notes.
See the [keyboard view lesson](../../keyboard.md) to learn more about how it works.

From this page, you can also access two [overlays](../../overlays-layers.md):

##### scales

By pressing the `scales` button, you can toggle the `scales` overlay.
This is similar to the scales interface from the Push factory script: 14 of the controls set the tonic of Live's [Scale Mode](https://help.ableton.com/hc/en-us/articles/11425083250972-Keys-and-Scales-in-Live-12-FAQ), which is reflected on the keyboard.
These buttons are arranged in a Circle of Fifths pattern.
An additional button toggles the keyboard's [in key status](../../keyboard.md#in-key--chromatic).

When `scales` is active, the top two rows of the matrix will let you select one of sixteen scales.

##### note_repeat

Pressing the `repeat` button toggles the `note_repeat` overlay.
With this overlay, the scene buttons will set the keyboard's [note repeat state](../../keyboard.md#note-repeat).

Leaving the `keyboard_page` will [automatically disable](../../overlays-layers.md#pages_in-pages_out) the `note_repeat` overlay.

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

Push's eight main encoders — the ones above the display — are configured as a group.
The six buttons in the top right of the controller — corresponding to six modes — determine what parameters they control.
By default, with the `volume` mode active, they control the volume of the eight ring tracks.
With `shift` active, they control the pan of those tracks.

With the mode `sends` active, they control the first eight sends of the selected track.
With the mode `device` active, they control the first eight parameters of the selected device.
With both `device` and `shift` active, they control the next eight parameters.

The mode `track` offers a compromise between these modes.
`enc_1` and `enc_2` control volume and pan of the selected track.
`enc_3` and `enc_4` control the first two sends.
`enc_5` through `enc_8` control the first four parameters of the selected device.
By holding `shift` we can control the next two sends and the next four device parameters.

The `browse` and `clip` bindings have been left unassigned, ready for you to assign them to any arbitrary parameter.
(Remember, you can always re-assign **any** of these preconfigured bindings).

`enc_master` (to the right of `enc_8`) controls the Main track's volume.
With `shift` held it controls the cue volume.

`enc_tempo`, the leftmost encoder, always controls the selected track's pan.
`enc_swing`, to its right, controls the selected track's volume.

!!! note "Controlling tempo with zcx"
    Unfortunately, the current version of zcx cannot natively bind to Live's tempo.
    If you have Max for Live, you can add [this free device](https://www.maxforlive.com/library/device/10403/tempo-control) to your set, and bind a zcx encoder to it.
