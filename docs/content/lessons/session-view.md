# Session view

zcx can be configured to show an interactive representation of Live's session view, as found on controllers like the Launchpad, Push, and APC.


!!! note "Session ring"

    Session view shows clips within the session ring.
    See the [session ring lesson](session-ring.md) to learn about configuring and controlling the session ring.

## Configuration

The zcx session view is actually a specialized [matrix section](getting-started/zcx-concepts.md#matrix-sections).
To configure it, add a new section called `__session_view` to your `matrix_sections.yaml`:

```yaml title="matrix_sections.yaml"
__session_view:
  row_start: 0
  row_end: 7
  col_start: 0
  col_end: 7
```

There is no need to create the file `matrix_sections/__session_view.yaml`.

Once the section is created, [add it to a page](getting-started/zcx-concepts.md#pages).

!!! note
    The `__session_view` section's dimensions must be no greater than the [height and width](../reference/configuration-files/preferences.md#session_ring) of your session ring. 

## Commands

The session view comes with some default functionality: pressing a pad will fire the corresponding clip slot.
Pressing a pad with a `select` mode active will select the corresponding clip slot.

This is achieved with ClyphX Pro action lists:

```yaml
gestures:
  pressed: >
    "${track_name}" / PLAY ${scene_number}
  pressed__select: >
    "${track_name}" / SEL ${scene_number}
```

For a pad belonging to track `my track` and scene 2, these commands would evaluate to:

```
"my track" / PLAY 2
"my track" / SEL 2
```

!!! note "Template strings"
    To understand this syntax, see the [template reference](../reference/template.md)

### Altering defaults

We can change the default functionality by adding a [section template](../reference/template.md#section-templates):

```yaml title="matrix_sections.yaml" hl_lines="6-9"
__session_view:
  row_start: 0
  row_end: 7
  col_start: 0
  col_end: 7
  template:
    gestures:
      released_delayed: >
        "{track_name}" / STOPNQ
```

In addition to the two previous commands, releasing after a long press will immediately stop the playing clip.

#### Special properties

You can use several unique properties in session view commands:

**`track_name`**

The name of the track to which the control belongs.
Good for use with [track actions](https://www.cxpman.com/action-reference/track-actions/).

**Example:**
```
"${track_name}" / MUTE
```

---

**`scene_number`**

The **one-indexed** scene number to which the control belongs.

**Example:**
```
"${track_name}" / PLAY ${scene_number}
```

---

**`clip_target`**

A convenience property for use with [clip actions](https://www.cxpman.com/action-reference/clip-actions/).

**Example:**
```
${clip_target} DEL

# evaluates to something like:
"my cool track" / CLIP(6) DEL
```
---

**`user_clip_target`**

As above, but for use with [user clip actions](https://www.cxpman.com/manual/core-concepts/#user-actions), which require a special syntax.

**Example:**

```
${user_clip_target} MY_USER_ACTION

# evaluates to something like:
"my cool track" / USER_CLIP(6) MY_USER_ACTION
```
