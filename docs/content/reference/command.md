---
weight: -10
---

# Command Reference

In zcx, a **command** is something that happens when a control is interacted with. Usually this means firing a ClyphX Pro action list.

## gestures

Gestures are physical actions you can perform on a control to trigger a command. There are six gestures supported by zcx:

- **press** always fired immediately after the control is pressed
- **short_press** fires after the control is pressed then released in quick succession
- **long_press** fires after the control is held for a brief period
- **release** always fires immediately after the control is released
- **long_release** fires after the held control is released — will only fire after a `long_press` event
- **double_click** fires after the control is pressed twice in quick succession

!!! note
    Previous versions of zcx used different names for these gestures: `pressed`, `released_immediately`, `pressed_delayed`, `released`, `released_delayed`, and `double_clicked`.
    You may continue to use these names if you prefer.

!!! note

    The `double_click` gesture may be unituitive.
    See [the lesson](../lessons/double_clicked.md) to undestand how it works.

### gesture syntax

To define gestures on a control, add a `gestures` key, with key/value pairs of gesture/command.

```yaml
my_control:
  color: green
  gestures:
    press: SEL / PLAY
    release: SEL / STOP
```

#### quotes in strings

Very often, ClyphX action lists include quotation marks, e.g. `"my track" / SEL`. This causes a small problem with yaml:

```yaml
  gestures:
    press: "my track" / SEL
```

Because of the quotes around `my track`, yaml interprets `my track` as the value for `pressed`, and then freaks out when it sees the rest of the action list (` / SEL`). There are two ways to deal with this.

##### block scalar syntax
```yaml
gestures:
  press: >    # this `>` character indicates a block scalar
    "my track" / SEL
```

This is the recommended method. Yaml will interpret the whole line `"my track" / SEL` as the action list.

This syntax also makes it easy to spread out long action lists over multiple lines for clarity:

```yaml
press: >
  "my track" / ARM ON ;
  "my track" / MON AUTO ;
  "my track" / RECFIX 8
```

##### quotes within quotes

By wrapping the entire action list in single quotes, we can freely use double quotes. This works, but is harder to read.

```yaml
gestures:
  press: '"my track" / SEL'
```

### modes syntax

When using [modes](../lessons/getting-started/zcx-concepts.md#modes) in zcx, the syntax is extended:
```yaml
gestures:
  press: SREC FIX 4
  press__shift: SREC FIX 8
  press__shift__select: SREC FIX 16
```

Gesture definitions always start with one of the [six supported gestures](#gestures). Modes can be added by appending the name of each mode prefixed with a double underscore (`__`). 

#### multiple matching gestures

If you have a configuration like above, where there are multiple variations on the `press` gesture, only the **most specific** definition will be executed.

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

##### conflicting gestures

Take this example:

```yaml
gestures:
  press__shift:
    log: shift
  press__select:
    log: select
```

With both the `shift` and `select` modes active, only the `pressed__select` gesture will fire.
This is because `pressed__select` is defined last.
You can use [cascading](#cascading-gestures) to fire them both.

## command syntax

The default command fires a ClyphX action list:
```yaml hl_lines="3"
my_control:
  gestures:
    press: SEL / MUTE
```

This is equivalent to:
```yaml hl_lines="4"
my_control:
  gestures:
    press: 
      cxp: SEL / MUTE
```

The `cxp` key is specifying the [command type](#command-types). Because `cxp` is the default command type, it's usually not necessary to specify it.

### command bundles

You may 'bundle' a combination of [command types](#command-types) and execute them sequentially when a gesture is performed:

```yaml
my_control:
  gestures:
    press:
      cxp: METRO
      msg: activated the metronome
      log: activated the metronome
```

## command types

### cxp

Accepts an action list as a string and triggers it in ClyphX.

```yaml hl_lines="3"
gestures:
  press: 
    cxp: SETPLAY
```

```yaml
gestures:
  press: >
    "my track" / SEL; 
    "my track" / ARM ON;
    SREC 8
```

### page

Accepts a page name, page number, or keyword, and switches to that [page](../lessons/getting-started/zcx-concepts.md#pages):

```yaml hl_lines="3 5 7"
gestures:
  press:
    page: 0
  press__shift:
    page: my_cool_page
  press__select:
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

Enables, disables, or toggles the given [mode](../lessons/getting-started/zcx-concepts.md#modes):

```yaml hl_lines="3 5"
gestures:
  press:
    mode_on: shift
  release:
    mode_off: shift
```

### overlay

Enable, disable, or toggle the given [overlay](../lessons/overlays-layers.md).

```yaml hl_lines="3 4 6 7"
gestures:
  press:
    overlay:
      enable: my_overlay
  release:
    overlay:
      disable: my_overlay
```

```yaml hl_lines="3 4"
gestures:
  press:
    overlay:
      toggle: my_overlay
```

### msg

Shows a message briefly at the bottom of Live's UI:
```yaml hl_lines="3"
gestures:
  press:
    msg: Look at my super cool message!
```

This is, in most cases, functionally equivalent to doing:
```yaml hl_lines="2"
press: >
  MSG "Look at my super cool message!"
```

### log

Prints a message directly to Live's Log.txt:

```yaml hl_lines="2"
press:
  log: failed successfully
```

### color

Change the control's color.

```yaml
press:
  color: green
release:
  color: initial
```

See also:

- [Color reference](color.md)
- [Change color via user action](../lessons/zcx-user-action.md)

### on_color, off_color

As [above](#color), but sets on/off or active/inactive colors.
Only available on controls with such feedback, including the [param control](../reference/control/param.md), [page control](../reference/control/page.md) and others.

```yaml
double_click:
  on_color: red
long_press:
  off_color: 127
```

### ring

Move the [session ring](../lessons/session-ring.md) of the script.

#### relative moves

Move the ring along its x (track) or y (scene) axis.

```yaml hl_lines="4 5 10 11 16 17 22 23"
up:
  gestures:
    press:
      ring:
        y: -1

right:
  gestures:
    press:
      ring:
        x: 1
        
down:
  gestures:
    press:
      ring:
        y: 1

left:
  gestures:
    press:
      ring:
        x: -1
```

##### simplified syntax

You can simply specify a direction rather than using x and y values.

```yaml
left:
  gestures:
    press:
      ring: left
    press__shift:
      ring: left 2
```

#### absolute moves

Directly position the left-most or top-most edge of the ring to a particular track or scene.

##### by track

Specify a track name (recommended) or number. When specifying a number, the number is zero-indexed.

```yaml
my_button:
  gestures:
    press:
      ring:
        track: my cool track
```

```yaml
my_button:
  gestures:
    press:
      ring:
        track: 0
```

##### by scene

Specify a scene name (recommended) or number. When specifying a number, the number is zero-indexed.

When targeting an [X-Scene](https://www.cxpman.com/manual/core-concepts/#x-scenes) by name, you must use the X-Scene's [identifier](https://www.cxpman.com/manual/core-concepts/#identifiers). E.g., with a scene name like `[my cool scene] ALL / MUTE; METRO ON`, you would use `my cool scene` as the scene name.

```yaml
my_button:
  gestures:
    press:
      ring:
        scene: 7
```

```yaml
my_button:
  gestures:
    press:
      ring:
        scene: my cool scene
```

### keyboard

Adjust the settings of the [melodic keyboard view](../lessons/keyboard.md#melodic-settings).

### pseq / rpseq

Emulates [sequential action lists](https://www.cxpman.com/manual/core-concepts/#sequential-action-lists) from ClyphX Pro.

```yaml
my_control:
  gestures:
    press:
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
    press:
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
    press:
      hardware_mode: live
```

### refresh

Force zcx to refresh all LED feedback.

```yaml
my_control:
  gestures:
    press:
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
    press:
      hot_reload: true
```

### special commands

Some control types may feature unique command types.
You can find information on these commands on each control's reference page.
