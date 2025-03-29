# understanding the double_clicked gesture

The `double_clicked` [gesture](/reference/command-reference#gestures) is cool, but it behaves somewhat peculiarly.

## the problem

To perform a double tap, you perform the following actions in quick succession:

- press the control
- release the control
- **press the control again** (the double click)
- release the control again

If we take this control definition:

```yaml
my_control:
  gestures:
    pressed:
      log: pressed
    released:
      log: released
    double_clicked:
      log: double_clicked
```

After a double tap, the log would read:

```
pressed
released
pressed
double_clicked
released
```

This behaviour means the use case you imagined for the double tap might not be possible.

## interesting uses

### compatible gestures

`pressed_delayed` and `double_clicked` are mutually exclusive, so you can make use of either of them without triggering the other.

```yaml
my_control:
  gestures:
    pressed_delayed: SETPLAY
    double_clicked: SETSTOP
```

### compatible actions

With clever design, you can find a combination of actions that complement each other:

```yaml
my_control:
  gestures:
    pressed: >
      "my track" / SEL
    pressed_delayed: >
      "my track" / MUTE
    double_clicked: >
      "my track" / PLAY
```

We can use a single press to select `my track`, and optionally execute one of two additional actions depending on the gesture.
For our purposes, there is no harm in selecting `my track` once or twice before performing the alternative actions.
