In zcx, a **command** is something that happens when a control is interacted with. Usually this means firing a ClyphX Pro action list.

## gestures

Gestures are physical actions you can perform on a control to trigger a command. There are six gestures supported by zcx:

- **pressed** always fired immediately after a control is pressed
- **pressed_delayed** fires after the control is held for a short time
- **released** always fired immediately after a control is released
- **released_delayed** fired after a held control is released — will only fire after a `pressed_delayed` event
- **released_immediately** fired after a control that was **not** being held is released
- **double_clicked** fired after a control is pressed twice in quick succession

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

Because of the quotes around `my track`, yaml interprets `my track`, as the value for `pressed`, and then freaks out when it sees the rest of the action list (` / SEL`). There are two ways to deal with this.

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

When using [modes](/tutorials/getting-started/zcx-concepts/#modes) in zcx, the syntax is extended:
```yaml
gestures:
  pressed: SREC FIX 4
  pressed__shift: SREC FIX 8
  pressed__shift__select: SREC FIX 16
```

Gesture definitions always start with one of the [six supported gestures](#gestures). Modes can be added by appending the name of each mode prefixed with a double underscore (`__`). 

!!! note
    If you have a configuration like above, where there are multiple variations on the `pressed` gesture, only the **most specific** definition will be executed.

    E.g. if `shift` is active, the action list `SREC FIX 8` will fire but `SREC FIX 4` will not. If both `shift` and `select` are active, only `SREC FIX 16` will fire.

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

### mode_on, mode_off

Enables or disables the given mode:

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

This is, in most cases, functionally equivelant to doing:
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
