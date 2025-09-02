---
title: Push 2
template: demo-tour.html
---

## Overview

### Modes

This config comes with four [modes](../zcx-concepts.md#modes) pre-configured.
These modes are `shift`, `select`, `device`, and `delete`
They are all mapped to controls of the same name.

### Pages

This config comes with five [pages](../zcx-concepts.md#pages) pre-configured.
By looking at `pages.yaml`, we can see these pages are named `home_page`, `alt_page`, `session_view_page`, `ring_devices_page`, and `blank_page`.
Push's eight `state` buttons have been configured as a group.
They are the multicolor buttons above the display, and they will take you to a different page on a press.

As three buttons are unassigned, if you add a new page it will automatically be assigned to one of the free buttons.

### Named controls

Push's eight `select` buttons have been configured as a group.
They are the buttons below the display.
They are [ring_track controls](../../../reference/control/ring_track.md), bound to the eight tracks in view of the [session ring](../../session-ring.md).
Pressing one will select the relevant track.
Holding one of these buttons will arm the track.
Double clicking a button will fire the next clip for that track.
Holding a button while holding `delete` will delete the track.

Three [transport controls](../../../reference/control/transport.md) are configured, for the controls `play`, `record`, and `metronome`.
These controls will indicate the status of the relevant transport function.
On a short press, `record` will fire the action list `SRECFIX`, starting Live's session record.
On a long press, it will fire `SRECFIX 8`, starting session record for a fixed length of 8 bars.

Push's eight `scene` buttons have been configured as a group.
Pressing a scene button will launch the scene at that position of the session ring.
Pushing a scene button while holding `shift` will launch scenes below the ring.
Pushing a scene button while holding `select` will select the scene, but not launch it.
Pushing a scene button with both `shift` and `select` will select scenes below the ring.

The `undo` control trigger's Live's undo feature.

`mute` and `solo` are param controls, mapped to the functions you'd expect.
`stop_clip`, also a param control, is bound to the target `SEL / STOP`, and will be brighter when the selected track is playing (and can thus be stopped).

The `duplicate` control duplicates the selected scene.

The `new` control inserts a new scene.

`master` is another param control, bound to the selection status of the Main track.

The controls `note` and `session` will enable Live's clip view and device view respectively.

The upper D-pad will move throughout the Live set.
If `shift` is held, the D-pad will move the session ring one step at a time.

The lower D-pad, made up of `octave_up`, `octave_down`, `page_prev`, and `page_next` move the ring eight steps at a time.
If `shift` is held, the ring will move one step at a time,

### Matrix pages

#### home_page

##### actions

Enter the first page by pressing the first `state` button.
The top-left quadrant is the [section](../zcx-concepts.md#matrix-sections) `actions_top_left`.
Opposite `actions_top_left` is `actions_top_right`.
Taking up the bottom half of the matrix is `actions_bottom_double`.

These three sections have been left mostly unconfigured.
`actions_bottom_double` uses a [section template](../../../reference/template.md#section-templates) to apply the rainbow colors without defining a color for each pad.

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
They are param controls bound to the eight tracks contained in the session ring.
The top row is bound to those track's mute status, the bottom row to their solo status.

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
By default, they control the volume of the eight ring tracks.
With `shift` active, they control the pan of those tracks.

With the mode `device` active, they control the first eight parameters of the selected device.
With both `device` and `shift` active, they control the next eight parameters.

`enc_master` (to the right of `enc_8`) controls the Main track's volume.
With `shift` held it controls the cue volume.

`enc_tempo`, the leftmost encoder, always controls the selected track's pan.
`enc_swing`, to its right, controls the selected track's volume.
