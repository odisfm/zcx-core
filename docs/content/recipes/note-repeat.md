# Note repeat overlay

Let's recreate the note repeat feature on the Ableton Push, where after pushing the `Repeat` button we can use the scene buttons to change the keyboard's repeat rate.


## Instructions


First, create the necessary [overlay](../lessons/overlays-layers.md#overlays).
Call it `note_repeat` and leave it as an empty object:

```yaml title="overlays.yaml"
overlays:
  note_repeat: {}
```

Now create the file `overlays/note_repeat.yaml`.
We'll use the buttons `scene_1` through `scene_8` in a [group](../reference/template.md#group-templates):

```yaml title="overlays/note_repeat.yaml"
__repeat_group:
  includes:
    [scene_1, scene_2, scene_3, scene_4, scene_5, scene_6, scene_7, scene_8]
```

We'll also set up a control to [activate the overlay](../lessons/overlays-layers.md#enabling-overlays):

```yaml title="named_controls.yaml"
repeat:
  type: overlay
  overlay: note_repeat
  gestures:
    pressed:
      overlay:
        toggle: note_repeat
```

Setting `type: overlay` isn't necessary, it's just for [LED feedback](../reference/control/overlay.md).

<br>

By using the [keyboard control](../reference/control/keyboard.md) we can get feedback about the zcx keyboard's note repeat setting.
We need to set the keyboard control's [function](../reference/control/keyboard.md#function) option to `repeat_rate: 1/4`, or whichever rate.
This is tedious to do for eight controls, so we will use [template strings](../reference/template.md#template-strings) and [vars](../reference/template.md#complex-expressions) to automate it somewhat:

```yaml title="overlays/note_repeat.yaml" hl_lines="6-8 12"
__repeat_group:
  includes:
    [scene_1, scene_2, scene_3, scene_4, scene_5, scene_6, scene_7, scene_8]
  vars:
    repeat_rates: ["1/32t", "1/32", "1/16t", "1/16", "1/8t", "1/8", "1/4t", "1/4"]
  type: keyboard
  function:
    repeat_rate: ${repeat_rates[me.index]}
  gestures:
    pressed:
      keyboard:
        repeat_rate: ${repeat_rates[me.index]}
```

!!! note
    These particular repeat rates are chosen because they are printed on the Push's buttons.
    You may use as many buttons and any [repeat rates](../lessons/keyboard.md#note-repeat) you like.

<br>

The overlay is now functional!
But we can make it a bit cooler:

```yaml title="overlays.yaml" hl_lines="3-9"
overlays:
  note_repeat:
    on_enter:
      keyboard:
        repeat_rate: on
    on_leave:
      keyboard:
        repeat_rate: off
    pages_out: true
```

By setting an [on_enter and on_leave](../lessons/overlays-layers.md#on_enter-on_leave) command, we can have the repeat turn on and off with the overlay.
The [pages_out](../lessons/overlays-layers.md#pages_in-pages_out) option means that if the [page](../lessons/getting-started/zcx-concepts.md#pages) changes while the overlay is active, the overlay is automatically dismissed.


## Final output

```yaml title="overlays.yaml"
overlays:
  note_repeat:
    on_enter:
      keyboard:
        repeat_rate: on
    on_leave:
      keyboard:
        repeat_rate: off
    pages_out: true
```

```yaml title="named_controls.yaml"
repeat:
  type: overlay
  overlay: note_repeat
  gestures:
    pressed:
      overlay:
        toggle: note_repeat
```


```yaml title="overlays/note_repeat.yaml"
__repeat_group:
  includes:
    [scene_1, scene_2, scene_3, scene_4, scene_5, scene_6, scene_7, scene_8]
  vars:
    repeat_rates: ["1/32t", "1/32", "1/16t", "1/16", "1/8t", "1/8", "1/4t", "1/4"]
  type: keyboard
  function:
    repeat_rate: ${repeat_rates[me.index]}
  gestures:
    pressed:
      keyboard:
        repeat_rate: ${repeat_rates[me.index]}
```

