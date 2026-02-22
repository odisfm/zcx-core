---
title: Launchpad X / Launchpad mini mk3
template: demo-tour.html
---

## Overview

### Modes

This config comes with two [modes](../zcx-concepts.md#modes) (`shift` and `select`) pre-configured.
`select` is mapped to the 7th scene launch button, and `shift` to the 8th.

### Pages

This config comes with three [pages](../zcx-concepts.md#pages) pre-configured.
By looking at `pages.yaml`, we can see these pages are named `home_page`, `session_view_page`, and `blank_page`.

The three buttons in the top-right are pre-mapped to these pages.
On Launchpad mini these are the buttons labelled `Drums`, `Keys`, and `User`, while on Launchpad X it's `Note`, `Custom`, and `Capture MIDI`.

### Named controls

The four arrow buttons in the top-left control Live's [session ring](../../session-ring.md).
By holding `shift` while pressing these buttons, we can move the ring one step at a time.

The four top scene launch buttons will launch the four scenes highlighted by the session ring.
By holding `shift`, we can launch four more scenes.
By holding `select`, we can select scenes rather than launch them.
By holding both, we can select the extra scenes.

By holding the button labelled `Session`, we can enter the Launchpad's factory script (Live mode), provided that script is also selected as a control surface in Live's preferences.

### Matrix pages

#### home_page

##### actions

Enter the first page by pressing `Drums` or `Note`.
The top-left quadrant is the [section](../zcx-concepts.md#matrix-sections) `actions_left`.
Opposite `actions_left` is `actions_right`.
In the bottom-left corner we have `actions_small`.

These three sections have been left mostly unconfigured.

##### ring_tracks

The fifth row of pads is the matrix section `ring_tracks`.
It's filled with [ring_track controls](../../../reference/control/ring_track.md) that bind to the tracks highlighted by the session ring.
By pressing each control, we can select its bound track.
By holding the control, we can arm the track exclusively (un-arm all other tracks).
By holding the control with `shift`, we can arm the track non-exclusively.

##### nav

The bottom right corner has the section `nav`.
The d-pad will move around the Live set.
By holding `shift` while using the d-pad we can move the session ring.

There are also four [transport controls](../../../reference/control/transport.md).
The green and red are bound to the transport's play and session record, while the purple and blue are bound to the metronome and arrangement loop.

#### session_view_page

Enter the second page by pressing `Keys` or `Custom`.

In the bottom right, we still have `nav`.
This demonstrates how we can have sections appear on multiple pages.

##### __session_view

The top half is occupied by zcx's session view.
This works much the same as the Launchpad's native session view.
Pressing a pad will launch the respective clip slot.
Pressing a pad with `select` held will select the slot.
See the [session view lesson](../../../lessons/session-view.md) for more detail on configuring this section.

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

The third row is mapped to the first four parameters of the currently selected device.
Pressing a control will toggle its parameter between its minimum and maximum.
While `shift` is held, the **next** four parameters will be controlled.

#### blank_page

This page contains one section — `blank_section` — an 8x8 unconfigured grid.
It's a great place to start experimenting with zcx's capabilities.
