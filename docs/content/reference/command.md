---
weight: -10
---

# Command Reference

In zcx, a **command** is something that happens when a control is interacted with. Usually this means firing a ClyphX Pro action list.

## gestures

Gestures are physical actions you can perform on a control to trigger a command. There are six gestures supported by zcx:

- **pressed** always fired immediately after a control is pressed
- **pressed_delayed** fires after the control is held for a short time
- **released** always fired immediately after a control is released
- **released_delayed** fired after a held control is released — will only fire after a `pressed_delayed` event
- **released_immediately** fired after a control that was **not** being held is released
- **double_clicked** fired after a control is pressed twice in quick succession

!!! note

    The `double_clicked` gesture may be unituitive.
    See [the lesson](../lessons/double_clicked.md) to undestand how it works.

### gesture syntax

To define gestures on a control, add a `gestures` key, with key/value pairs of gesture/command.

```yaml
my_control:
  color: green
  gestures:
    pressed: SEL / PLAY
    released: SEL / STOP
```

#### quotes in strings

Very often, ClyphX action lists include quotation marks, e.g. `"my track" / SEL`. This causes a small problem with yaml:

```yaml
  gestures:
    pressed: "my track" / SEL
```

Because of the quotes around `my track`, yaml interprets `my track` as the value for `pressed`, and then freaks out when it sees the rest of the action list (` / SEL`). There are two ways to deal with this.

##### block scalar syntax
```yaml
gestures:
  pressed: >    # this `>` character indicates a block scalar
    "my track" / SEL
```

This is the recommended method. Yaml will interpret the whole line `"my track" / SEL` as the action list.

This syntax also makes it easy to spread out long action lists over multiple lines for clarity:

```yaml
pressed: >
  "my track" / ARM ON ;
  "my track" / MON AUTO ;
  "my track" / RECFIX 8
```

##### quotes within quotes

By wrapping the entire action list in single quotes, we can freely use double quotes. This works, but is harder to read.

```yaml
gestures:
  pressed: '"my track" / SEL'
```

### modes syntax

When using [modes](../lessons/getting-started/zcx-concepts.md#modes) in zcx, the syntax is extended:
```yaml
gestures:
  pressed: SREC FIX 4
  pressed__shift: SREC FIX 8
  pressed__shift__select: SREC FIX 16
```

Gesture definitions always start with one of the [six supported gestures](#gestures). Modes can be added by appending the name of each mode prefixed with a double underscore (`__`). 

#### multiple matching gestures

If you have a configuration like above, where there are multiple variations on the `pressed` gesture, only the **most specific** definition will be executed.

E.g. if `shift` is active, the action list `SREC FIX 8` will fire but `SREC FIX 4` will not. If both `shift` and `select` are active, only `SREC FIX 16` will fire.

##### cascading gestures

You may [configure a control](control/standard.md#cascade) to execute all matching command bundles in sequence. 
This is done by setting the control's `cascade` option to `up` or `down`:

```yaml
my_control:
  cascade: down
```

This will execute command bundles in order of least-specific to most-specific, i.e `pressed`, `pressed__shift`, and `pressed__shift__select`.

Setting `cascade: up` will reverse this order.

## command syntax

The default command fires a ClyphX action list:
```yaml hl_lines="3"
my_control:
  gestures:
    pressed: SEL / MUTE
```

This is equivalent to:
```yaml hl_lines="4"
my_control:
  gestures:
    pressed: 
      cxp: SEL / MUTE
```

The `cxp` key is specifying the [command type](#command-types). Because `cxp` is the default command type, it's usually not necessary to specify it.

### command bundles

You may 'bundle' a combination of [command types](#command-types) and execute them sequentially when a gesture is performed:

```yaml
my_control:
  gestures:
    pressed:
      cxp: METRO
      msg: activated the metronome
      log: activated the metronome
```

## command types

### cxp

Accepts an action list as a string and triggers it in ClyphX.

```yaml hl_lines="3"
gestures:
  pressed: 
    cxp: SETPLAY
```

```yaml
gestures:
  pressed: >
    "my track" / SEL; 
    "my track" / ARM ON;
    SREC 8
```

### page

Accepts a page name, page number, or keyword, and switches to that page:

```yaml hl_lines="3 5 7"
gestures:
  pressed:
    page: 0
  pressed__shift:
    page: my_cool_page
  pressed__select:
    page: next
```

#### keywords

**next**
```yaml
page: next
```

Goes to the next page.

**prev**
```yaml
page: prev
```

Goes to the previous page.

**last**
```yaml
page: last
```

Goes back to the page that was active before the current one.

### mode_on, mode_off, mode

Enables, disables, or toggles the given mode:

```yaml hl_lines="3 5"
gestures:
  pressed:
    mode_on: shift
  released:
    mode_off: shift
```

### msg

Shows a message briefly at the bottom of Live's UI:
```yaml hl_lines="3"
gestures:
  pressed:
    msg: Look at my super cool message!
```

This is, in most cases, functionally equivalent to doing:
```yaml hl_lines="2"
pressed: >
  MSG "Look at my super cool message!"
```

### log

Prints a message directly to Live's Log.txt:

```yaml hl_lines="2"
pressed:
  log: failed successfully
```

### color

Change the color of the activated control.

```yaml
pressed:
  color: green
released:
  color: initial
```

See also:

- [Color reference](color.md)
- [Change color via user action](../lessons/zcx-user-action.md)

### ring

Move the [session ring](../lessons/session-ring.md) of the script.

#### relative moves

Move the ring along its x (track) or y (scene) axis.

```yaml hl_lines="4 5 10 11 16 17 22 23"
up:
  gestures:
    pressed:
      ring:
        y: -1

right:
  gestures:
    pressed:
      ring:
        x: 1
        
down:
  gestures:
    pressed:
      ring:
        y: 1

left:
  gestures:
    pressed:
      ring:
        x: -1
```

##### simplified syntax

You can simply specify a direction rather than using x and y values.

```yaml
left:
  gestures:
    pressed:
      ring: left
    pressed__shift:
      ring: left 2
```

#### absolute moves

Directly position the left-most or top-most edge of the ring to a particular track or scene.

##### by track

Specify a track name (recommended) or number. When specifying a number, the number is zero-indexed.

```yaml
my_button:
  ring:
    track: my cool track
```

```yaml
my_button:
  ring:
    track: 0
```

##### by scene

Specify a scene name (recommended) or number. When specifying a number, the number is zero-indexed.

When targeting an [X-Scene](https://www.cxpman.com/manual/core-concepts/#x-scenes) by name, you must use the X-Scene's [identifier](https://www.cxpman.com/manual/core-concepts/#identifiers). E.g., with a scene name like `[my cool scene] ALL / MUTE; METRO ON`, you would use `my cool scene` as the scene name.

```yaml
my_button:
  ring:
    scene: 7
```

```yaml
my_button:
  ring:
    scene: my cool scene
```

### pseq / rpseq

Emulates [sequential action lists](https://www.cxpman.com/manual/core-concepts/#sequential-action-lists) from ClyphX Pro.

```yaml
my_control:
  gestures:
    pressed:
      pseq:
        - >
          "my first track" / SEL
        - >
          "my second track" / SEL
```

The value of a `pseq` or `rpseq` key must be a list, with each list item being a command bundle (or action list).
`pseq` will step through each command in order, while `rpseq` will trigger a random command (repeat commands are possible).

### python

Execute Python code in a [limited execution context](../lessons/python-context.md).

```yaml
my_control:
  gestures:
    pressed:
      python: |
        for i, track in enumerate(song.tracks):
          if i != 0 and i % 15 == 0:
            print("fizzbuzz")
          elif i != 0 and i % 5 == 0:
            print("buzz")
          elif i != 0 and i % 3 == 0:
            print("fizz")
          else:
            print(track.name)
```

### hardware_mode

For a multimode controller (e.g. Push), force the controller back into 'Live' mode.

```yaml
my_control:
  gestures:
    pressed:
      hardware_mode: live
```

### refresh

Force zcx to refresh all LED feedback.

```yaml
my_control:
  gestures:
    pressed:
      refresh: true
```

!!! note

    Generally, it should not be necessary to use this command.
    If you are using this command to work around an issue you're having, please consider [reporting a bug](../lessons/reporting-bugs.md).

### hot_reload

Perform a [hot reload](../lessons/reloading-control-surfaces.md#hot-reload).

```yaml
my_control:
  gestures:
    pressed:
      hot_reload: true
```

### special commands

Some control types may feature unique command types.
You can find information on these commands on each control's reference page.
