# Porting zcx to new hardware

zcx has full support for [a limited set of MIDI controllers](../index.md#hardware).
If your controller is not one of those supported, it is relatively easy to create a 'port' for your hardware

!!! note "Getting help"
    If you get stuck, feel free to reach out on [the Discord](https://discord.zcxcore.com) for help.

!!! tip "Making your port available to others"
    If you'd like to make your port available to all users of zcx, have a look at the [contributing guide](../dev/contributing.md) and reach out in the Discord before getting started.

## Download the generic build

Head over to [the latest release](https://github.com/odisfm/zcx-core/releases/latest) and download the file `_zcx_generic.zip`.
Follow the [standard instructions](../lessons/getting-started/installation.md/#install-the-script) for installation.

## Optional: rename the folder

The folder can be named whatever you like. This helps to stay organised.

## Open the folder in your code editor

I.e. `_zcx_generic`, or whatever you've renamed it to.
This allows you to see all the relevant files at once.

If you don't have a code editor, [Microsoft Visual Studio Code](https://code.visualstudio.com/) is a good option.

## Edit the specification files

These are the files that tell zcx what MIDI messages to expect from your hardware, as well as what they should be named.
We'll go through each file.

### specs.yaml

Here we define settings that apply across the controller.

#### global_midi_channel

```yaml
global_midi_channel: 0
```

Most modern controllers send all messages on one channel: channel 1.
In this file we use zero-indexed values, so the default of `0` should be fine.

#### button_matrix

```yaml title="specs.yaml"
button_matrix:
  msg_type: note
  id_start: 0
  id_end: 63
#  raw_identifiers: [
#    [ 81, 82, 83, 84, 85, 86, 87, 88 ],
#    [ 71, 72, 73, 74, 75, 76, 77, 78 ],
#    [ 61, 62, 63, 64, 65, 66, 67, 68 ],
#    [ 51, 52, 53, 54, 55, 56, 57, 58 ],
#    [ 41, 42, 43, 44, 45, 46, 47, 48 ],
#    [ 31, 32, 33, 34, 35, 36, 37, 38 ],
#    [ 21, 22, 23, 24, 25, 26, 27, 28 ],
#    [ 11, 12, 13, 14, 15, 16, 17, 18 ]
#  ]
  feedback: rgb
  momentary: true
  width: 8
  playable: true
```

Here we define the specs of the button matrix.

##### msg_type

Either `note` or `cc`.

##### matrix IDs

Here we define the note or CC numbers that the matrix sends.
Most controllers have a contiguous matrix; if the matrix has 64 buttons, they are all in order with no gaps. 
The Ableton Push works like this — it sends notes 36 through 99.
In this case, we can set `id_start: 36` and `id_end: 99`.

Other controllers, like the Launchpad, have 'gaps' in the matrix.
In this case, comment out (or delete) `id_start` and `id_end`, and un-comment `raw_identifiers`.
This is a list of lists, where each inner list item is the note or CC number sent for that pad.

When looking at `raw_identifiers`, the layout you see is how the controller looks from the user's perspective: in this example the top-left pad sends ID 81, and the bottom-right pad sends ID 18.

##### feedback

Here we define what type of feedback the controller uses, either `rgb`, `biled`, or `basic` (on or off).
Modern controllers will use `rgb` feedback.

##### momentary

Modern controllers will have momentary buttons, so we can leave this as `true`.

##### width

Here we define the number of vertical columns in the matrix.

##### playable

Leave this as `true`.

#### cc_buttons, note_buttons

```yaml title="specs.yaml"
cc_buttons:
#  channel: 0
  momentary: true
  feedback: rgb

note_buttons:
#  channel: 0
  momentary: true
  feedback: rgb
```

These settings work the same way as in `specs.yaml`.
Set the values that apply to the majority of the controller's buttons.
We can override individual buttons later.

#### encoders

```yaml title="specs.yaml"
encoders:
  sensitivity: 1.0
  mode: RELATIVE_SMOOTH_TWO_COMPLIMENT
```

Here we define settings for the controllers encoders (knobs and/or faders).
If your controller has neither, you can leave this section.

##### sensitivity

Define the default sensitivity for all encoders.
In most cases the default of `1.0` is fine.
Later, we can override the sensitivity of individual encoders.

##### mode

This defines the specific type of message your hardware sends.
Again, we can override specific encoders later, so choose the mode applicable to most controls.

The available options are:

```
ABSOLUTE
ABSOLUTE_14_BIT             
RELATIVE_SIGNED_BIT                     
RELATIVE_SIGNED_BIT2
RELATIVE_BINARY_OFFSET
RELATIVE_TWO_COMPLIMENT          
RELATIVE_SMOOTH_SIGNED_BIT          
RELATIVE_SMOOTH_SIGNED_BIT2      
RELATIVE_SMOOTH_BINARY_OFFSET         
RELATIVE_SMOOTH_TWO_COMPLIMENT    
```

_Capital letters are mandatory._

For faders or knobs with a fixed start and end, use `ABSOLUTE`.

For 'endless' knobs, you will have to consult the technical specs of your controller, or simply try different modes and see which feels best.
The default, `RELATIVE_SMOOTH_TWO_COMPLIMENT` is a safe choice.

##### feedback

`true` or `false`, depending on whether the encoders display visual feedback.

#### preferences

Here we define [preferences](../reference/configuration-files/preferences.md#preference-reference) that are **specific to this controller**.
Other preferences should be left to the user.

In most cases, the only thing that should be added here is `session_ring`:

```yaml title="specs.yaml"
session_ring:
  width: 8
  height: 8
```

_Assuming an 8x8 matrix._

### cc_buttons.yaml, note_buttons.yaml

Here we define the CC or note number for **every** button on the controller.
Yes, it's quite tedious.

As you probably guessed, buttons that send CC are defined in `cc_buttons.yaml`, and note buttons in `note_buttons.yaml`.

If your controller uses only one type, e.g. CC messages, you may delete `note_buttons.yaml`, and vice versa.

Let's take a look at `cc_buttons.yaml`:

```yaml title="cc_buttons.yaml"
cc_button_placeholder:
  cc: 127
```

It's quite simple: each entry is the name of this control (`cc_button_placeholder`), and we must provide another key (`cc` or `note`) that matches what this control sends.

If this control deviates from the other controls, we can specify this:

```yaml title="cc_buttons.yaml"
cc_button_placeholder:
  cc: 127
  channel: 9
  feedback: rgb
```

#### giving good names to controls

The user will refer to these names in their [named_controls.yaml](../lessons/getting-started/zcx-concepts.md#named-controls), so it's important that the names you choose are intuitive.

Here are some pointers:

##### use snake_case

Control names should **always** be in lowercase.
Controls that need multiple words to describe them should use [snake_case](https://en.wikipedia.org/wiki/Snake_case), i.e. words should be separated by an underscore.
`My Cool Control` would be `my_cool_control`.

##### use the official control names

If the control has a label printed on it, use that name.
For example, the Push has a button labelled `Fixed Length`, so we would use the name `fixed_length`.

For unlabelled controls, you can usually find the official name in the manufacturer's documentation.

##### unless there's a good reason not to

The Push has a column of buttons that are used to launch scenes in Session View.
These buttons are also used to control note repeat functionality, and are labelled `1/32t`, `1/32`, `1/16t`, etc.

This is confusing, so it's better to use names like `scene_1`, `scene_2`, and so on.

### encoders.yaml

Just like `note_buttons.yaml` and `cc_buttons.yaml`, we create an entry for each encoder.

You may provide overrides for any of the [global options](#encoders) defined earlier.

If your controller does not feature encoders, you may delete this file.

### sysex.py

This file is only relevant for controllers with distinct 'Live' and 'user modes'.
If your controller does not, you can skip this.

Let's look at the `sysex.py` file for Push 1:

```python title="sysex.py"
LIVE_MODE = (240, 71, 127, 21, 98, 0, 1, 0, 247)
USER_MODE = (240, 71, 127, 21, 98, 0, 1, 1, 247)
ON_DISCONNECT = LIVE_MODE
INIT_DELAY = 2000
```

`LIVE_MODE` is the MIDI sysex sent upon entering 'Live' mode.
`USER_MODE` is the sysex for user mode.

It's particularly important to set `USER_MODE`, as this way zcx is aware of the mode switch, and can refresh all LED feedback.

To determine the appropriate messages, you can use a MIDI monitor app like [Protokol](https://hexler.net/protokol), and see what messages are sent when entering and exiting user mode.

Protokol should display a message like:

`ENDPOINT(Ableton Push User Port) TYPE(SYSTEMEXCLUSIVE) DATA(F0477F1562000100F7)`

The `DATA` portion is what we're after, though it's displayed here in hexadecimal, and we need it in decimal.
Please ask for help in the Discord if you're having trouble here.

### colors.py

This file determines how your controller responds to [named colors](../reference/color.md#name) and [animated colors](../reference/color.md#animated-colors).

The file provided in the generic release comes from the Push 1 release.
The Push 1, Launchpad series, and APC Mini mk2 use a similar color mapping — hopefully your controller does too.

If it doesn't, you can always specify colors by [MIDI value](../reference/color.md#midi-value) in your config.
If you'd like to try creating a custom `colors.py`, that is beyond the scope of this lesson, but reach out in the Discord for guidance.

#### problematic animations

If, after pressing a control, the RGB feedback seems to 'glitch out', one workaround is to set a [global control template](../reference/template.md#control-templates) with the option `suppress_animations: true`.

## notes

- Do **not** edit `zcx.yaml`. Specifically, `hardware` must be left as `generic`. Changing this means the [upgrade script](../lessons/upgrade.md) will **overwrite** the contents of your hardware folder, and you'll have to do all this again.

## the fun begins

Now that your controller is configured, see [getting started](getting-started/index.md) for details on creating your user configuration.
