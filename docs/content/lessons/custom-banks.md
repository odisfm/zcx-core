# Custom parameter banks

When using [encoders](../reference/encoder.md) and [param controls](../reference/control/param.md) you may target [best-of-bank device parameters](../reference/encoder.md#devd-bb-pp).
This is useful when we don't know what device we'll be targeting, e.g, when targeting the selected device, or the first device on a track.

When using best-of-bank, your controls will map to a pre-defined list of banks and parameters.
Take EQ Eight for instance:
bank one is the on/off state of each filter, bank two is the frequency, bank three is the gain, and bank four is the resonance (Q).

You may find that these defaults aren't very useful.
For the EQ Eight example, you'll likely find yourself dancing between banks two, three, and four to do simple EQ changes.

One solution would be to rack our EQ Eight device and map the rack macros to the exact parameters we want.
An alternative is to use custom parameter banks, allowing us to define this behaviour directly in our zcx config.

## Defining custom banks

Custom banks are defined in the file `_config/custom_banks.yaml`.
If you don't have this file, create it.

`custom_banks.yaml` is a [list](getting-started/reading-zcx-configurations.md#lists) of [objects](getting-started/reading-zcx-configurations.md#objects).
Each object must have at least a `banks` key, as well as either a `class_name` or `instance_name`.

### class_name / instance_name

Here we provide the name of the device to target.
If providing `class_name`, only the official, English name of the device (as it appears in the UI) is considered.
If providing `instance_name`, both the official name and any custom name you have given the device is considered.

```yaml title="custom_banks.yaml"
- class_name: EQ Eight
```
```yaml title="custom_banks.yaml"
- instance_name: my eq
```

### banks

Now we provide `banks`, a [list of lists](getting-started/reading-zcx-configurations.md#lists), where each outer list is a bank, and each inner list is the name of up to eight device parameters.

```yaml title="custom_banks.yaml"
- class_name: EQ Eight
  banks:
      - [
            2 Frequency A,
            2 Gain A,
            3 Frequency A,
            3 Gain A,
            4 Frequency A,
            4 Gain A,
            5 Frequency A,
            5 Gain A,
      ]
```

!!! note ""
    The parameter names used are the same names you would use in your ClyphX Pro action lists.
    You can right-click any parameter and click `Copy parameter name` to get the correct name.


Now, targeting an EQ Eight device with `DEV("EQ Eight") B1 P1` will map to the frequency of band 2, `B1 P2` the gain of band 2.

We haven't defined any other banks, so doing `B2 P1` would [fallback](#fallback) to the default.

#### banks continued

Inside a bank definition, you may list a parameter as `null` to accept the [fallback](#fallback) parameter.

```yaml title="custom_banks.yaml"
- class_name: EQ Eight
  banks:
      - [
            2 Frequency A,
            null,
            3 Frequency A,
            null,
            4 Frequency A,
            null,
            5 Frequency A,
            null,
      ]
```

You may list less than eight parameters in a bank to accept the default for the rest:

```yaml title="custom_banks.yaml"
- class_name: EQ Eight
  banks:
      - [
        2 Frequency A,
        2 Gain A,
      ]
```

You may leave a bank definition as an empty list to accept defaults for the entire bank:

```yaml title="custom_banks.yaml" hl_lines="7"
- class_name: EQ Eight
  banks:
      - [
            2 Frequency A,
            2 Gain A,
      ]
      - [] # bank 2
      - [
            3 Frequency A,
            3 Gain A,
      ]
```

You may list the same parameter multiple times, including in the same bank:

```yaml title="custom_banks.yaml"
- class_name: EQ Eight
  banks:
    -
      [
        2 Frequency A,
        2 Gain A,
        3 Frequency A,
        3 Gain A,
        4 Frequency A,
        4 Gain A,
        5 Frequency A,
        5 Gain A,
      ]
    -
      [
        2 Resonance A,
        2 Gain A,
        3 Resonance A,
        3 Gain A,
        4 Resonance A,
        4 Gain A,
        5 Resonance A,
        5 Gain A,
      ]
```

### Additional options

#### fallback
```yaml title="custom_banks.yaml" hl_lines="2"
- class_name: EQ Eight
  fallback: true
  banks: [
```
_Default is `true`_

When `true`, if a particular bank or parameter is not defined (or does not exist), use the default parameter.
When `false`, leave that control unmapped.

