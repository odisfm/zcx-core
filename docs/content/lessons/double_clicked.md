# understanding the double_click gesture

The `double_click` [gesture](../reference/command.md#gestures) is cool, but it behaves somewhat peculiarly.

## the problem

To perform a double tap, you perform the following actions in quick succession:

- press the control
- release the control
- press the control again
- **release the control again** (the double click)

If we take this control definition:

```yaml
my_control:
  gestures:
    press:
      log: press
    release:
      log: release
    double_click:
      log: double_click
```

After a double tap, the log would read:

```
press
release
press
release
double_click
```

This behaviour means the use case you imagined for the double tap might not be possible.

## interesting uses

### compatible gestures

`long_press` and `double_click` are mutually exclusive, so you can make use of either of them without triggering the other.

```yaml
my_control:
  gestures:
    long_press: SETPLAY
    double_click: SETSTOP
```

### compatible actions

With clever design, you can find a combination of actions that complement each other:

```yaml
my_control:
  gestures:
    press: >
      "my track" / SEL
    long_press: >
      "my track" / MUTE
    double_click: >
      "my track" / PLAY
```

We can use a single press to select `my track`, and optionally execute one of two additional actions depending on the gesture.
For our purposes, there is no harm in selecting `my track` once or twice before performing the alternative actions.
