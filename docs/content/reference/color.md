---
weight: -7
---

# Color reference

zcx allows you to define the color of a control in multiple formats.

## MIDI value

Pass a MIDI value in the range 0-127 to light the control with a color corresponding to that value.

```yaml
my_control:
  color: 42
```

## Name

There are several colors that you can reference by name


```yaml
my_control:
  color: purple
```
```yaml
my_control:
  color: half_blink_slow
```

### RGB controls

Controls with full color feedback.

- `white`
- `grey`
- `dark_grey`
- `red`
- `orange`
- `yellow`
- `green`
- `play_green`
- `lime`
- `blue`
- `sky`
- `cyan`
- `purple`
- `magenta`
- `indigo`
- `pink`

### Basic controls

Controls with single-color feedback.

- `on`
- `off`
- `half`
- `half_blink_slow`
- `half_blink_fast`
- `full_blink_slow`
- `full_blink_fast`

### BiLed controls

Controls with red, green, and yellow feedback.

- `green`
- `green_half`
- `green_blink_slow`
- `green_blink_fast`
- `red`
- `red_half`
- `red_blink_slow`
- `red_blink_fast`
- `yellow`
- `yellow_half`
- `yellow_blink_slow`
- `yellow_blink_fast`
- `amber`
- `amber_half`
- `amber_blink_slow`
- `amber_blink_fast`

## Animated colors

If your hardware supports it, you may define one of two available animations for your control.
To sync these animations with Live's tempo, you must enable `Sync` on the MIDI out port of your hardware in Live's MIDI preferences.

The available animations are `pulse` and `blink`.
`pulse` blends between the two colors, while `blink` quickly alternates between them.

For each animation type, you must define an `a` and `b` color, and optionally a `speed` between 1-5 (slowest to fastest).
You may omit the `speed` option to accept the default of 1.

```yaml
my_control:
  pulse:
    a: 49
    b: 5
    speed: 3

my_other_control:
  blink:
    a: red
    b: blue
```
