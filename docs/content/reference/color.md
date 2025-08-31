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

There are several colors that you can reference by name:

- white
- grey
- dark_grey
- red
- orange
- yellow
- green
- play_green
- lime
- blue
- sky
- cyan
- purple
- magenta
- indigo
- pink

```yaml
my_control:
  color: purple
```

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
