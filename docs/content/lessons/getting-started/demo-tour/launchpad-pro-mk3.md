---
title: Launchpad Pro mk3
template: demo-tour.html
---

## Overview

### Modes

By default, this config only has one mode; `shift`, mapped to the `shift` button in the top right of the controller.
Of course, you can always [add more modes](../zcx-concepts.md#modes) later.

### Pages

This config comes with six [pages](../zcx-concepts.md#pages) pre-configured.
By looking at `pages.yaml`, we can see these pages are named `home_page`, `alt_page`, `session_view_page`, `ring_devices_page`, `keyboard_page`, and `blank_page`.

Six of the buttons above the matrix have been configured as a group.
These are `session`, `note`, `chord`, `custom`, `sequencer`, and `projects`.
They will each take you to a different page on a press.


### Named controls

The four arrow buttons in the top-left will move around the Live set.
Holding `shift` while pressing these buttons will move the [session ring](../../session-ring.md).

The scene launch buttons will launch scenes relative to the session ring.
Pressing them while holding `shift` will launch scenes below the ring.

Launchpad's eight `track` buttons have been configured as a group.
These are the top row of buttons below the matrix.
They are [ring_track controls](../../../reference/control/ring_track.md), bound to the eight tracks in view of the [session ring](../../session-ring.md).
Pressing one will select the relevant track.
Holding one of these buttons will arm the track exclusively, while holding with `shift` will arm the track non-exclusively.
Double clicking a button will fire the next clip for that track.

Two [transport controls](../../../reference/control/transport.md) are configured, for the controls `play` and `record`.
These controls will indicate the status of the relevant transport function.
On a short press, `record` will fire the action list `SREC`, starting Live's session record.
On a long press, it will fire `SRECFIX 8`, starting session record for a fixed length of 8 bars.

Many of the buttons in the bottom row below the matrix mimic the functionality of the factory Launchpad script.

### Matrix pages

### Matrix pages

#### home_page

##### actions

Enter the first page by pressing the `session` button.
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
This works much the same as the Launchpad's native session view.
Pressing a pad will launch the respective clip slot.

See the [session view lesson](../../../lessons/session-view.md) for more detail on configuring this section.

##### session_controls

The bottom two rows feature the section `session_controls`.
They are param controls bound to the eight tracks contained in the session ring.
The top row is bound to those track's mute status.
The bottom row will set its respective track to a random color, which isn't particularly useful, but it's there to demonstrate how we can [target ring tracks with action lists](../../session-ring.md#referencing-the-ring-from-template-strings).

#### keyboard_page

This page features a full-size keyboard view for playing notes.
See the [keyboard view lesson](../../keyboard.md) to learn more about how it works.

From this page, you can also access two [overlays](../../overlays-layers.md):

##### keyboard_notes overlay

By long-pressing the `note` button, you can enable the `keyboard_notes` overlay, which occupies the top two rows of the matrix.

The first five buttons of the top row set the scale of Live's [Scale Mode](https://help.ableton.com/hc/en-us/articles/11425083250972-Keys-and-Scales-in-Live-12-FAQ), which is reflected on the keyboard.
The next two buttons decrease or increase the tonic of Scale mode by one semitone.
The last button toggles the keyboard's [in key status](../../keyboard.md#in-key--chromatic).

In the second row, the first seven buttons set the keyboard's [note repeat status](../../keyboard.md#in-key--chromatic), while the final button toggle's [full velocity mode](../../keyboard.md#full-velocity).

#### ring_devices_page

This page features only one section `ring_devices`, which fills the whole page.
Again, this section deals with the eight ring tracks.
Each column has eight param controls to affect the first eight parameters of the first device of the relevant track.
Press a pad to toggle the parameter between its minimum and maximum.
Release a pad after a hold to toggle the parameter again.

#### blank_page

This page contains one section — `blank_section` — an 8x8 unconfigured grid.
It's a great place to start experimenting with zcx's capabilities.

