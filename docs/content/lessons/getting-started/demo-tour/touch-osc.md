---
title: TouchOSC
template: demo-tour.html
---
!!! warning ""
    This lesson assumes basic familiarity with TouchOSC, and that TouchOSC is installed with working MIDI and OSC connections between the computer running Live and the device running TouchOSC.
    
    Refer to the [TouchOSC manual](https://hexler.net/touchosc/manual) if needed.

!!! note
    This tour is specifically for the pre-configured zcx release called `touch_osc` and its accompanying TouchOSC layout `zcx_touch_osc.tosc`.
    For details on creating a zcx configuration for your own TouchOSC layout, see [the lesson](../../touch-osc.md).

## Additional setup

!!! note ""
    "TouchOSC host" refers to the device which is running the TouchOSC app.

### Install the .tosc file

You will find the file `zcx_touch_osc.tosc` within the [installation folder](../installation.md#install-the-script) inside the folder `extras/`.
Move this file to an appropriate location on the TouchOSC host.

### Configure Ableton Live

If you haven't already, [activate the zcx script](../installation.md#activate-the-script).
Use the TouchOSC ports as the zcx script MIDI in/out.
This will usually be `TouchOSC Bridge`.

### Configure OSC settings on the TouchOSC host

Refer to the [TouchOSC manual](https://hexler.net/touchosc/manual/connections-osc).

### Set up ClyphX Pro's OSC output

Refer to [this lesson](../../osc-output.md).
`OUTGOING_OSC_PORT` should be the port set up in the last step.
`OSC_DEVICE_IP_ADDRESS` should be the IP address of the TouchOSC host, or `127.0.0.1` if using TouchOSC on the same computer that's running Live.

**Note:** the demo config already has the appropriate `osc_output` values in `preferences.yaml`.

## Overview

### Layout

On the left side of the layout is a column of twelve buttons, from `dock_1` at the bottom to `dock_12` at the top.
At the top right is a [pager](https://hexler.net/touchosc/manual/controls#pager), with three pages.

On the first page, you will find `track_fader` and `track_pan` 1 through 8.
On the second is `enc_17` through `enc_32`.
On the third is `enc_1` through `enc_16`.

Below the pager is a row with `track_select_1` through `track_select_8`.

The bottom half of the layout features [the matrix](../zcx-concepts.md#matrix-controls).

### Modes

This config comes with two [modes](../zcx-concepts.md#modes) — `shift` and `select` — pre-configured.
They are mapped to `dock_1` and `dock_2` at the bottom-left of the layout.

### Pages

This config comes with four [pages](../zcx-concepts.md#pages) pre-configured.
By looking at `pages.yaml`, we can see these pages are named `home_page`, `alt_page`, `channel_strip_page`, and `blank_page`.
The controls `dock_12` through `dock_7` have been configured as a group, and pressing one will take you to the relevant page.

As two buttons are unassigned, if you add a new page it will automatically be assigned to one of the free buttons.

### Named controls

`track_select_1` through `track_select_8` are [param controls](../../../reference/control/param.md), bound to the selection state of the eight tracks in view of the [session ring](../../session-ring.md).
They are [param controls](../../../reference/control/param.md), bound to the selection state of the eight tracks in view of the [session ring](../../session-ring.md).
Pressing one will select the relevant track, and the button will become brighter to indicate that.
Holding one of these buttons will arm the track.
With the mode `shift` active, the buttons will control the mute state of each track.

The controls labelled ↤ and ↦ (`dock_5` and `dock_6`) will move the session ring left or right by eight positions.

Two controls, `dock_3` and `dock_4` have been left unassigned.

### Matrix pages

#### home_page

##### nav

The left side of `home_page` features the section `nav`.
The top row of `nav` has four [transport controls](../../../reference/control/transport.md), bound to the functions `play`, `session_record`, `metronome`, and `loop`.

The three bottom rows features a D-pad (⬆, ⬅, ⮕, ⬇).
Pressing the D-pad will move you around the Live set.

In the center is a [param control](../../../reference/control/param.md), mapped to the target `SEL / PLAY`.
This button will fire the currently selected clip.

In the corners of the D-pad are controls labelled ⇈, ⇊, ⇇ and ⇉ which will move the session ring by one position.
With `shift` active, the ring will move by eight positions.

##### actions

This section has been left unconfigured.

#### alt_page

The top half of the matrix still features `nav`, demonstrating how we can have sections appear on multiple pages.

##### select_control

On the top row are four controls labelled 🔇, 🔊, 👂, and ●.
They are param controls, mapped respectively to the selected track's mute, solo, input monitoring, and arm status.

On the second row is another group of param controls, mapped to the selection status of the first four devices on the selected track.

The bottom two rows have been left unconfigured.

#### channel_strip_page

This page features only one section, `channel_strip`.
Each column of the matrix will control the mute, solo, input monitoring, and arm status of the relevant track in the session ring.

#### blank_page

This page contains one section — `blank_section` — an 8x4 unconfigured grid.
It's a great place to start experimenting with zcx's capabilities.

### Encoders

The TouchOSC layout has three different pages of encoders, which can be swapped between with the buttons labelled `i`, `ii`, and `iii`.

!!! warning ""
    These pages are distinct from [zcx pages](../zcx-concepts.md#pages).

#### page i

The faders (`track_fader_1` through `track_fader_8`) are configured as a group, and control the volume of the eight tracks in view of the session ring.
The encoders (`track_pan_1` through `track_pan_8`) are also grouped, and control the pan of those same tracks.

#### page ii

These encoders (`enc_17` through `enc_32`) control the first 16 parameters of the selected device.

#### page iii

These encoders (`enc_1` through `enc_16`) have been left unmapped.

## Troubleshooting

If after following these steps you are unsuccessful, reach out on [the Discord](https://discord.zcxcore.com) or [report a bug](../../reporting-bugs.md).

### I'm pressing buttons but nothing is happening

There are several likely reasons:

* Live's control surface settings are misconfigured, [see above](#configure-ableton-live).
* The connection between the computer running Live and the TouchOSC host is misconfigured. See the [TouchOSC manual](https://hexler.net/touchosc/manual/connections).

### There is no text in the TouchOSC layout

Most likely, the OSC connection between ClyphX Pro and TouchOSC is misconfigured, [see above](#configure-osc-settings-on-the-touchosc-host).

### Other issues

If you have edited the zcx config files, there is likely a problem with your configuration.
See any errors that popup when loading the zcx script, and also any errors in the log file.

For further help, reach out on the Discord.

## Editing the TouchOSC layout

If you would like to adapt the layout, this will require editing the files in `zcx_touch_osc/hardware`.

!!! danger ""
    Before doing this, you must edit the file `zcx_touch_osc/zcx.yaml`, and change the line `hardware: touch_osc` to `hardware: generic` (ignore the warning).
    
    If you fail to do this and later run [the upgrade script](../../upgrade.md#automatic-upgrade), any edits to the files in `hardware/` will be **overwritten**.

