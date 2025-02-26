In zcx, a **command** is something that happens when a control is interacted with. Usually this means firing a ClyphX Pro action list.

## syntax

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
