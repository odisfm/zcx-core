## Note on different Launchkey mk4 versions

Launchkey mk4 is available in 25, 37, 49, and 61-key versions, with the 25 and 37-key also available in a "mini" form factor.
All versions use the same [release](https://github.com/odisfm/zcx-core/releases/latest), with only a few differences:

- Mini version only:
    - You must configure the [Launchkey mk4 plugin](#launchkey-mk4-plugin) with `mini: true` to enable display output
    - **Note:** this is not necessary for the full-size 25 and 37-key versions
- Differences in named controls:
      - On 49 and 61-key models, you must use the names `enc_bank_down` and `enc_bank_up` for the controls next to the encoders, while on smaller models you must use the names `enc_bank_down_m` and `enc_bank_up_m`.
    - On 49 and 61-key models, you must use the names `track_left` and `track_right` for the buttons labeled ❮ and ❯, while on smaller models you must use the names `track_left_m` and `track_right_m`.
    - You may delete the unused definitions from [named_controls.yaml](../file/named_controls.md). 
- Only 49 and 61-key models feature faders and their associated buttons. On smaller models, you may delete the definitions for `fb_1` through `fb_9` from [named_controls.yaml](../file/named_controls.md), and `fader_1` through `fader_9` from [encoders.yaml](../file/encoders.md).

## Launchkey mk4 plugin

zcx for Launchkey mk4 ships with a plugin to enable display output, as well as some miscellaneous features including [controlling the Launchkey from the zcx user action](#user-action).

The plugin can be configured via [preferences.yaml](../file/preferences.md#plugins).

### Preferences

```yaml title="preferences.yaml"
plugins:
  launchkey_mk4:
    mini: false # set this to `true` if using Mini 25 or Mini 37 model
    follow_key: true
```

### mini

Set to `true` for Mini 25 and Mini 37 models to enable display output.

### follow_key

When `true`, the tonic and scale type of Launchkey's [scale mode](https://userguides.novationmusic.com/hc/en-gb/articles/27613113249554-Using-the-Launchkey-s-built-in-features#UUID-2eac012a-1238-ce63-06a8-d89f7444fd80) will follow [Live's key](https://help.ableton.com/hc/en-us/articles/11425083250972-Keys-and-Scales-in-Live-12-FAQ), as long as Live's scale type is also available on Launchkey.


## control names

### buttons

These are the names you must use in [named_controls.yaml](../../lessons/getting-started/zcx-concepts.md#named-controls-and-matrix-controls)

- `pad_bank_up`, `pad_bank_down` - The buttons left of the pads labeled ˄ and ˅
- `scene_launch` - The button right of the pads labeled ❯
- `function` - The button labeled `function`
- `capture` - The button labeled `capture MIDI`
- `undo` - The button labeled `undo`
- `quantize` - The button labeled `quantise`
- `metronome` - The button labeled `metronome`
- `stop` - The button labeled ⏹
- `play` - The button labeled ▶
- `record` - The button labeled ⏺
- `loop` - The button labeled ⟳

**25 and 37-key only (including mini):**

- `enc_bank_up_m`, `enc_bank_down_m` - The buttons next to the encoders labeled ˄ and ˅
- `track_left_m`, `track_right_m` - The buttons labeled ❮ and ❯

**48 and 61-key only:**

- `enc_bank_up`, `enc_bank_down` - The buttons next to the encoders labeled ˄ and ˅
- `track_left`, `track_right` - The buttons labeled ❮ and ❯
- `fb_1` through `fb_9` - The nine buttons below the faders

### unmappable controls

- The buttons labelled `shift`, `settings`, `scale`, `chord map`, `arp`, `fixed chord`, and the octave up/down buttons
- The keybed
- The pitch/modulation wheels

These controls will all perform their normal functions.

### encoders

These are the names you must use in [encoders.yaml](../encoder.md)

- `fader_1` through `fader_9` - The nine faders
- `enc_1` through `enc_8` - The eight encoders

## User action

With Launchkey mk4, a variety of special functions are available via the [zcx user action](../../lessons/zcx-user-action.md).
To use these actions, [target your Launchkey as normal](../../lessons/zcx-user-action.md#targeting-a-script).

All these functions should be prefixed with `LK`, e.g. 

`ZCX <target script> LK <command> <subcommand> <arguments>`


### Set layouts

These actions can be used to set the layouts of Launchkey's pads, encoders, and faders.

**Note:** changing these modes will leave these controls unusable by zcx; you will need to change back to `zcx` mode to control zcx again.

#### Pad layouts

`ZCX <target script> LK LAYOUT PAD <pad layout>`

Where `<pad layout>` is one of:

- `zcx` or `daw`
- `drum`
- `chords`
- `cm1` through `cm4` (custom modes 1-4)
- `arp`
- `chord_map`

#### Encoder layouts

`ZCX <target script> LK LAYOUT ENC <encoder layout>`

Where `<encoder layout>` is one of:

- `zcx` or `transport`
- `cm1` through `cm4` (custom modes 1-4)
- `mixer`, `plugin`, and `sends` (these should generally not be used)

#### Fader layouts

`ZCX <target script> LK LAYOUT FADER <fader layout>`

Where `<fader layout>` is one of:

- `zcx` or `volume`
- `cm1` through `cm4` (custom modes 1-4)

### MIDI and zone settings

#### MIDI channel settings

`ZCX <target script> LK MIDICH <feature> <channel>`

Where `<channel>` is a number from 1-16 and `<feature>` is one of:

- `a` - Split A channel (or global keybed channel for versions without split)
- `b` - Split B channel
- `chord` - chords channel
- `drum` - drums channel

#### Zone settings

`ZCX <target script> LK ZONE <option>`

Where `<option>` is one of:

- `a`
- `b`
- `split`
- `layer`

#### Split position

`ZCX <target script> LK SPLIT <note>`

Set the split position of they keybed, where `<note>` is a number between 0 and 127.

### Arpeggiator settings

#### Enable/disable

`ZCX <target script> LK ARP ON`

`ZCX <target script> LK ARP OFF`

#### Type

`ZCX <target script> LK ARP TYPE <type>`

Where `<type>` is one of:

`up`, `down`, `up_down`, `up_down_2`, `as_played`, `random`, `chord`, `strum`

#### Rate

`ZCX <target script> LK ARP RATE <rate>`

Where `<rate>` is one of:

`1/4`, `1/4t`, `1/8`, `1/8t`, `1/16`, `1/16t`, `1/32`, `1/32t`

#### Octave

`ZCX <target script> LK ARP OCTAVE <octave>`

Where `<octave>` is between 1 and 4.

#### Latch

`ZCX <target script> LK ARP LATCH ON`

`ZCX <target script> LK ARP LATCH OFF`

#### Gate

`ZCX <target script> LK ARP GATE <value>`

Where `<value>` is between 0 and 95.

#### Mutate

`ZCX <target script> LK ARP MUTATE <value>`

Where `<value>` is between 0 and 127.

#### Velocity

`ZCX <target script> LK ARP VEL FULL`

`ZCX <target script> LK ARP VEL NOTE`


### Scale settings

#### Enable/Disable

`ZCX <target script> LK SCALE ON`

`ZCX <target script> LK SCALE OFF`

#### Behaviour

`ZCX <target script> LK SCALE BHV <option>`

Where `<option>` is one of `snap`, `filter`, or `easy`.

#### Root note

`ZCX <target script> LK SCALE ROOT <note>`

Where `<note>` is a note `C` through `B` (including sharps or flats), or a number.

You may provide `match` as the note, which will set the Launchkey's root note to match Live's internal root note.

See also: [follow_key](#follow_key)

#### Scale type

`ZCX <target script> LK SCALE NAME <name>`

Where `<name>` is one of:

`major`, `minor`, `dorian`, `mixolydian`, `lydian`, `phrygian`, `locrian`,
`whole tone`, `half-whole dim.`, `whole-half dim.`, `minor blues`, `minor pentatonic`,
`major pentatonic`, `harmonic minor`, `harmonic major`, `dorian #4`, `phrygian dominant`,
`melodic minor`, `lydian augmented`, `lydian dominant`, `super locrian`, `8-tone spanish`,
`bhairav`, `hungarian minor`, `hirajoshi`, `in-sen`, `iwato`, `kumoi`, `pelog selisir`,
`pelog tembung`

Scale names must be written **exactly** as they appear here.

You may provide `match` as the scale name, which will attempt to match Launchkey's scale to Live's scale.
**Note:** not every scale is shared between Launchkey and Live.

See also: [follow_key](#follow_key)

### Chord map settings

#### Enable/disable

[See here](#pad-layouts).

#### Adventure

`ZCX <target script> LK CHORD ADV <value>`

Where `<value>` is a number between 1 and 5.

#### Explore

`ZCX <target script> LK CHORD EXPLORE <value>`

Where `<value>` is a number between 1 and 8.

#### Spread

`ZCX <target script> LK CHORD SPREAD <value>`

Where `<value>` is a number between 1 and 3.

#### Roll

`ZCX <target script> LK CHORD ROLL <value>`

Where `<value>` is a number between 0 and 100 (in milliseconds).

### Other functions

#### Shift

Emulate pressing (and latching) the `shift` button:

`ZCX <target script> LK CHORD SHIFT ON`

`ZCX <target script> LK CHORD SHIFT OFF`