# Dynamic encoders

Encoders in zcx can be mapped to a [variety of targets](../reference/encoder.md#mapping-targets).
By using [templating](../reference/template.md) we can define many targets at once.

These examples will use the encoders `enc_1` through `enc_8` in a [group](../reference/template.md#encoder-groups).
If you're not sure what names to use, check the [hardware reference](../reference/hardware).
You may use a different number of encoders, but you may have to tweak some of the values.

## Controlling the selected device

By using [template strings](../reference/template.md#template-strings) and targeting [best-of-bank](../reference/encoder.md#devd-bb-pp) device parameters we can control the first eight parameters on any device with only four lines of yaml:


```yaml title="encoders.yaml"
__encoder_group:
  includes: [enc_1, enc_2, enc_3, enc_4, enc_5, enc_6, enc_7, enc_8]
  binding: >
    DEV(SEL) B1 P${me.Index}
```

By adding a `shift` [mode](../lessons/getting-started/zcx-concepts.md#modes) we can access the _next_ eight parameters:

```yaml title="encoders.yaml"
__encoder_group:
  includes: [enc_1, enc_2, enc_3, enc_4, enc_5, enc_6, enc_7, enc_8]
  binding:
    default: >
      DEV(SEL) B1 P${me.Index}
    __shift: >
      DEV(SEL) B2 P${me.Index}
```

## Controlling the selected track

### Compact mode

This config give us access to the track's volume, pan, first two sends, and first four parameters on the selected device.
With the `shift` mode active we get access to the next two sends and the next four device parameters.
In this scenario it's easier to ungroup the first four encoders, but it's possible to keep them grouped if you'd prefer.

```yaml title="encoders.yaml"
enc_1:
  binding: >
    SEL / VOL

enc_2:
  binding: >
    SEL / PAN

enc_3:
  binding:
    default: >
      SEL / SEND A
    __shift: >
      SEL / SEND B

enc_4:
  binding:
    default: >
      SEL / SEND C
    __shift: >
      SEL / SEND D

__device_encoders:
  includes: [enc_5, enc_6, enc_7, enc_8]
  binding:
    default: DEV(SEL) B1 P${me.Index}
    __shift: DEV(SEL) B1 P${me.Index + 4}
```

### Sends

This config give us access to the track's first eight sends:

```yaml title="encoders.yaml"
__encoder_group:
  includes: [enc_1, enc_2, enc_3, enc_4, enc_5, enc_6, enc_7, enc_8]
  binding: >
    SEL / SEND ${me.index}
```

### Mix mode

In this mode we have access to the track's volume, pan, and first six sends.
With `shift` active we get access to the track's left and right [split-stereo panning](https://help.ableton.com/hc/en-us/articles/360000103324-Split-Stereo-Pan-Mode) and the next six sends:

```yaml title="encoders.yaml"
__encoder_group:
  includes: [enc_1, enc_2, enc_3, enc_4, enc_5, enc_6, enc_7, enc_8]
  binding:
    default: >
      SEL / SEND ${send_num(me.index - 2)}
    __shift: >
      SEL / SEND ${send_num(me.index - 2 + 6)}
  encoders:
    enc_1:
      binding:
        default: >
          SEL / VOL
        __shift: >
          SEL / PANL
    enc_2:
      binding:
        default: >
          SEL / PAN
        __shift: >
          SEL / PANR
```

## Controlling ring tracks

By using the [RING() syntax](../reference/encoder.md#targeting-the-session-ring) we can target tracks inside the [session ring](../lessons/session-ring.md).
Any [track target](../reference/encoder.md#mapping-targets) can be used with the `RING()` syntax:

### Volume

```yaml title="encoders.yaml"
__encoder_group:
  includes: [enc_1, enc_2, enc_3, enc_4, enc_5, enc_6, enc_7, enc_8]
  binding: >
    RING(${me.index}) / VOL
```

### Pan

```yaml title="encoders.yaml"
__encoder_group:
  includes: [enc_1, enc_2, enc_3, enc_4, enc_5, enc_6, enc_7, enc_8]
  binding: >
    RING(${me.index}) / PAN
```

### Sends

```yaml title="encoders.yaml"
__encoder_group:
  includes: [enc_1, enc_2, enc_3, enc_4, enc_5, enc_6, enc_7, enc_8]
  binding:
    default: >
      RING(${me.index}) / SEND A
    __shift: >
      RING(${me.index}) / SEND B
```

## See also

- [Encoder banks](encoder-banks.md)

