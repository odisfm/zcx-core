# Encoder Reference

Encoder mapping in zcx aims to emulate the Encoder Bindings feature from the [ClyphX Pro Bindings](https://www.cxpman.com/manual/optional-accessories/#clyphx-pro-bindings) optional accessory.

## Configuration

Encoder mappings are configured in `encoders.yaml`, within your `_config` folder.
An encoder config looks like this:

```yaml title="encoders.yaml"
enc_1:
  binding: >
    SEL / VOL
```

Just like with buttons or pads, we can dynamically rebind parameters based on the [active mode(s)](/tutorials/getting-started/zcx-concepts/#modes).

```yaml title="encoders.yaml" hl_lines="2 4"
enc_1:
  binding:
      default: >
        SEL / VOL
      __shift: >
        SEL / PAN
```

When using this feature, the special key `default` applies when no other (more specific) binding is applicable.

### Mapping targets

Mapping targets are provided as a string in ClyphX Pro syntax. 
[Template strings](/reference/template-reference#template-strings) may be used within these strings.

With [some exceptions](#limitations), the available targets are the same as ClyphX Pro bindings.
As such, nativeKONTROL's examples are reproduced below:

#### VOL

**Applies to**: Any track's volume control.

**Example:** `SEL/VOL`

#### PAN

**Applies to**: Any track's pan control.

**Example:** `2/PAN`

#### SEND `z`

**Applies to**: Any particular send on any track, where `z` is the send letter.

**Example:** `SEL/SEND F`

#### PANL / PANR

**Applies to**: Any track's left or right pan position when using [split-stereo panning](https://help.ableton.com/hc/en-us/articles/360000103324-Split-Stereo-Pan-Mode).

**Example:** `"my cool track"/PANL`

#### SELP

**Applies to**: The last parameter in Live that was clicked on with your mouse.

**Example:** `SELP`

#### DEV(`d`) CS

**Applies to**: The Chain Selector of any Rack on any Track where `d` specifies the Device.

**Example:** `1/DEV(SEL) CS`

#### DEV(`d`) P`p`

**Applies to**: Device Best-of-Bank parameter of any Device on any Track where `d` specifies the Device and `p` specifies the number of the parameter or Macro in the case of Racks.

**Example:** `1/DEV(SEL) P4`

#### DEV(`x`.`y`) PAN

**Applies to**: A particular chain's pan control, targeted with [ClyphX Pro rack dot notation](https://www.cxpman.com/manual/general-action-information/#single-devices). 

**Example:** `1/DEV(2.3) PAN`

#### DEV(`x`.`y`) SEND `z`

**Applies to**: A particular send letter `z` of a particular chain `y`, targeted with [ClyphX Pro rack dot notation](https://www.cxpman.com/manual/general-action-information/#single-devices). 

**Example:** `1/DEV(1.4) SEND A`

#### DEV(`x`.`y`) VOL

**Applies to**: A particular chain's volume control, targeted with [ClyphX Pro rack dot notation](https://www.cxpman.com/manual/general-action-information/#single-devices). 

**Example:** `1/DEV(1.1) VOL`

#### XFADER

**Applies to**: Main (master) track's crossfader.

**Example:** `XFADER`

### Targeting the session ring

With a special syntax, we can dynamically target a track at a particular position of the [session ring](/lessons/session-ring/).
We can use any [valid track target](#mapping-targets) with this syntax:

```yaml
enc_1:
  binding: >
    RING(0) / VOL
  __shift: >
    RING(0) / PAN
```

**Note**: this syntax is zero-indexed, i.e. `RING(0)` means the **first** track of the session ring.

### Encoder groups

We can group encoders to apply common definitions to them. See [Template Reference](/reference/template-reference#encoder-groups) for details.

### Additional options

The following options may be configured on each encoder.

#### unbind_on_fail
```yaml
enc_1:
  binding: >
    SEL / VOL
  unbind_on_fail: false
```

With the example binding `SEL / VOL`, `enc_1` will control the volume of the selected track.
Let's say the selected track is an audio track, `guitar`.
`enc_1` will, obviously, control the volume of `guitar`.

If we navigate to a blank MIDI track (which does not have a volume parameter), by default zcx will remain bound to `guitar`'s volume, until we select another track with a volume parameter.
By setting `unbind_on_fail: true` for this control, `enc_1` would instead be bound to no parameter, until there is a relevant parameter to bind to (i.e. we select another audio track).

## Limitations

### FIRST, LAST, and SEL keyword

When using [ClyphX Pro rack dot notation](https://www.cxpman.com/manual/general-action-information/#single-devices), the `FIRST`, `LAST`, and `SEL` keywords are not recognised.
This may be added in a future release.

### Bank syntax

ClyphX Pro allows targeting of parameters by bank, e.g `SEL / DEV(1) B2 P1` to target the first parameter of the second bank.
This is not recognised in zcx.
Instead, you would use the parameter number (or name) directly (`P9` for the above example).
