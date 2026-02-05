---
title: APC40 mkII
template: demo-tour.html
---

## Overview

### Modes

This config comes with five main [modes](../zcx-concepts.md#modes) pre-configured.
These are `shift`, `select`, `pan`, `sends`, and `user`.
They are mapped to controls of the same name, except `select`, which is on the `bank_lock` button (next to `shift`).

`pan`, `sends`, and `user` are set up [exclusively](../../../reference/file/preferences.md#exclusive_modes), so that enabling one will disable the other two.

`shift` and `select` will only be active while they are held.

There are two other groups of exclusive modes; `bank_1` and `bank_2`, and also `send_1` through `send_8`.
We will cover these modes [later](#encoders).

### Pages

This config comes with five [pages](../zcx-concepts.md#pages) pre-configured.
By looking at `pages.yaml`, we can see these pages are named `home_page`, `alt_page`, `session_view_page`, `ring_devices_page`, and `blank_page`.
The top row the matrix has been set up as a page changer.
This is defined in the matrix section `page_changer`, which appears on every page.

As some buttons are unassigned, if you add a new page it will automatically be assigned to one of the free buttons.

### Named controls

Most of the controls on APC40 are set up to replicate their factory script functionality.

Above the faders are the `mute`, `cross`, `solo`, `arm`, `select`, and `stop` buttons, each set up as [groups](../zcx-concepts.md#templating) of [param controls](../../../reference/control/param.md), controlling the eight tracks inside the [session ring](../../session-ring.md).

Four controls, `play`, `record`, `session_record`, and `metronome` are [transport controls](../../../reference/control/transport.md), and they control the functions you'd expect.

The buttons `device_left` and `device_right` move the device selection left or right on a short press, or to the first or last device on a long press.

`device_on` is another param control, toggling the selected device's bypass.

The bottom four `scene` buttons launch their associated scene.
With `shift` held, they launch scenes below the session ring.

The top button, `scene_1`, functions as a redundant `shift` button.
This control — like any zcx control — can be reassigned to a function of your choice.

The directional buttons labelled "bank select" move the session ring.
By holding `shift` you can move the ring by a whole bank.
By holding `select` you can move the highlighted clip.
In zcx, these buttons are called `dpad_up`, `dpad_right`, `dpad_down`, and `dpad_left`.

### Matrix pages

#### home_page

##### actions

Enter the first page by pressing the top-left matrix button.
The left half is the [section](../zcx-concepts.md#matrix-sections) `actions_left`.
Opposite `actions_left` is `actions_right`.

These two sections have been left mostly unconfigured.

#### alt_page

This page features the section `actions_double`, which is also unconfigured.

#### session_view_page

The bottom four rows are occupied by zcx's session view.
This works much the same as the APC's native session view.
Pressing a pad will launch the respective clip slot.
Pressing a pad with `select` held will select the slot.
See the [session view lesson](../../../lessons/session-view.md) for more detail on configuring this section.

#### ring_devices_page

This page features the section `ring_devices`.
This section deals with the eight ring tracks.
Each column has four param controls to affect the first four parameters of the first device of the relevant track.
Press a pad to toggle the parameter between its minimum and maximum.
Release a pad after a hold to toggle the parameter again.
Hold `shift` to access the _next_ four parameters on each track.

#### blank_page

This page contains 1blank_section`, a 4x8 unconfigured grid.
It's a great place to start experimenting with zcx's capabilities.

## Encoders

### Faders

`fader_1` through `fader_8` control the volume of the tracks inside the session ring, while `fader_9` controls the Main track's volume.

### Track encoders

Like with the factory script, the eight track encoders are linked to the `pan`, `sends`, and `user` modes.

In `pan` mode, they control the pan of the eight session ring tracks.

In `sends` mode, they control one send for each of these tracks.
By holding down the `sends` button, you will activate the `sends` [overlay](../../overlays-layers.md).
With this overlay, you can use the buttons `select_1` through `select_8` to activate modes `send_1` through `send_8`.
The encoders will now control that send.

In `user` mode, the encoders have been left unconfigured, making it easy to start binding them to arbitrary parameters of your choice.
There is also a blank binding for `__user__shift`, giving you easy access to another eight custom parameters.
Of course, **all** of these encoder modes can be reassigned to a parameter of your choice.

### Device encoders

These eight encoders control the first eight parameters of the selected device.
By using `bank_left` and `bank_right` you can switch between the modes `bank_1` and `bank_2`.
With `bank_2` enabled, you can control the next eight parameters of the device.


### Miscellaneous encoders

`cue` and `crossfader` control their default functions.

`tempo` has been left unbound.

!!! note "Controlling tempo with zcx"
    Unfortunately, the current version of zcx cannot natively bind to Live's tempo.
    If you have Max for Live, you can add [this free device](https://www.maxforlive.com/library/device/10403/tempo-control) to your set, and bind a zcx encoder to it. 

