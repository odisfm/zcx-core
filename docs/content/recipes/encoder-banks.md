# Encoder banks

By using [modes](../lessons/getting-started/zcx-concepts.md#modes) we can set up a group of buttons as a bank select, letting us remap [encoders](../lessons/getting-started/zcx-concepts.md#encoder-mappings) to any number of parameters.
LED feedback on the bank buttons will let us know which bank is active.

In this recipe we'll use four banks of four encoders, but you may use any number of each.

## Instructions

### Modes

Each bank will need its own mode, so add `bank_1` through `bank_4` to your [modes.yaml](../reference/file/modes.md).

```yaml title="modes.yaml" hl_lines="2-5"
- shift
- bank_1
- bank_2
- bank_3
- bank_4
```

It only makes sense to have one bank active at a time, so let's group these modes into an exclusive mode group.
We do this with the [exclusive_modes](../reference/file/preferences.md#exclusive_modes) preference:

```yaml title="preferences.yaml"
exclusive_modes:
  - [bank_1, bank_2, bank_3, bank_4]
```
!!! note ""
    This data structure is a [list of lists](../lessons/getting-started/reading-zcx-configurations.md#lists)

We'd like a bank to be active when zcx loads, so let's add a [startup_command](../reference/file/preferences.md#startup_command):
```yaml title="preferences.yaml" hl_lines="4-5"
exclusive_modes:
  - [bank_1, bank_2, bank_3, bank_4]

startup_command:
  mode_on: bank_1
```

### Bank controls

We'll make a [group](../reference/template.md#group-templates) of four named controls for the bank select.
For this recipe we'll use the [named controls](../lessons/getting-started/zcx-concepts.md#named-controls) `select_1` through `select_4`, though you may use any, including [matrix controls](../lessons/getting-started/zcx-concepts.md#matrix-controls).

```yaml title="named_controls.yaml"
__bank_select:
  includes: [
    select_1, select_2, select_3, select_4
  ]
  type: mode
  mode: bank_${me.Index}
  active_color: yellow
  inactive_color: red
  gestures:
    pressed:
      mode_on: bank_${me.Index}
```

Using [template strings](../reference/template.md#template-strings) we've created four [mode controls](../reference/control/mode.md) for our four modes.
We can now press a control to activate that bank, and the LED feedback will confirm it.

### Encoders

First, we'll make an [encoder group](../reference/template.md#encoder-groups) called `__banked_encoders`.
We'll include encoders `enc_1` through `enc_4`:

```yaml title="encoders.yaml"
__banked_encoders:
  includes: [enc_1, enc_2, enc_3, enc_4]
  binding: NONE
```

For this example, we'll have these four banks:

- **bank one:** volume, pan, send A, send B of the selected track
- **bank two:** parameters one through four of the selected device
- **bank three:** parameters five through eight of the selected device
- **bank four:** an empty bank, for now...

We'll achieve this by creating an override for each encoder, each with a binding for the four modes:

```yaml title="encoders.yaml" hl_lines="4"
__banked_encoders:
  includes: [enc_1, enc_2, enc_3, enc_4]
  binding: NONE
  encoders:
    enc_1:
      binding:
        __bank_1: >
          SEL / VOL
        __bank_2: >
          DEV(SEL) B1 P${me.Index}
        __bank_3: >
          DEV(SEL) B1 P${me.Index + 4}
        __bank_4: >
          NONE

    enc_2:
      binding:
        __bank_1: >
          SEL / PAN
        __bank_2: >
          DEV(SEL) B1 P${me.Index}
        __bank_3: >
          DEV(SEL) B1 P${me.Index + 4}
        __bank_4: >
          NONE

    enc_3:
      binding:
        __bank_1: >
          SEL / SEND A
        __bank_2: >
          DEV(SEL) B1 P${me.Index}
        __bank_3: >
          DEV(SEL) B1 P${me.Index + 4}
        __bank_4: >
          NONE

    enc_4:
      binding:
        __bank_1: >
          SEL / SEND B
        __bank_2: >
          DEV(SEL) B1 P${me.Index}
        __bank_3: >
          DEV(SEL) B1 P${me.Index + 4}
        __bank_4: >
          NONE
```

We can even get rid of a lot of repetition by defining the `bank_2` and `bank_3` bindings on the group:

```yaml title="encoders.yaml" hl_lines="3-5"
__banked_encoders:
  includes: [enc_1, enc_2, enc_3, enc_4]
  binding:
    __bank_2: DEV(SEL) B1 P${me.Index}
    __bank_3: DEV(SEL) B1 P${me.Index + 4}

  encoders:
    enc_1:
      binding:
        __bank_1: >
          SEL / VOL
        __bank_4: >
          NONE

    enc_2:
      binding:
        __bank_1: >
          SEL / PAN
        __bank_4: >
          NONE

    enc_3:
      binding:
        __bank_1: >
          SEL / SEND A
        __bank_4: >
          NONE

    enc_4:
      binding:
        __bank_1: >
          SEL / SEND B
        __bank_4: >
          NONE
```

## Final output

```yaml title="modes.yaml"
- bank_1
- bank_2
- bank_3
- bank_4
```
```yaml title="preferences.yaml"
exclusive_modes:
  - [bank_1, bank_2, bank_3, bank_4]

startup_command:
  mode_on: bank_1
```
```yaml title="named_controls.yaml"
__bank_select:
  includes: [
    select_1, select_2, select_3, select_4
  ]
  type: mode
  mode: bank_${me.Index}
  active_color: yellow
  inactive_color: red
  gestures:
    pressed:
      mode_on: bank_${me.Index}
```
```yaml title="encoders.yaml"
__banked_encoders:
  includes: [enc_1, enc_2, enc_3, enc_4]
  binding: NONE
  encoders:
    enc_1:
      binding:
        __bank_1: >
          SEL / VOL
        __bank_2: >
          DEV(SEL) B1 P${me.Index}
        __bank_3: >
          DEV(SEL) B1 P${me.Index + 4}
        __bank_4: >
          NONE

    enc_2:
      binding:
        __bank_1: >
          SEL / PAN
        __bank_2: >
          DEV(SEL) B1 P${me.Index}
        __bank_3: >
          DEV(SEL) B1 P${me.Index + 4}
        __bank_4: >
          NONE

    enc_3:
      binding:
        __bank_1: >
          SEL / SEND A
        __bank_2: >
          DEV(SEL) B1 P${me.Index}
        __bank_3: >
          DEV(SEL) B1 P${me.Index + 4}
        __bank_4: >
          NONE

    enc_4:
      binding:
        __bank_1: >
          SEL / SEND B
        __bank_2: >
          DEV(SEL) B1 P${me.Index}
        __bank_3: >
          DEV(SEL) B1 P${me.Index + 4}
        __bank_4: >
          NONE
```
