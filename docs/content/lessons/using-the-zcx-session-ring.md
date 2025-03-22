# Using the zcx session ring

Like other control surface scripts, zcx provides a 'session ring' — a colored box that can be moved around the session to target different tracks or screens.

![A screenshot of the zcx session ring in Ableton Live 12](/lessons/img/session-ring-1.png)


While zcx cannot display a representation of Live's session view (i.e., the session view on Push, Launchpad, and others), it is useful to be able to move the ring around the set, and use [template strings](/reference/template-reference/#template-strings) to target tracks or refer to scenes enclosed within the ring.

## Resizing the ring

You may resize the session ring via [preferences.yaml](/reference/configuration-files/preferences#session-ring).

## Moving the ring

A script's ring may be positioned with the [ring command](/reference/command-reference#ring) or the ClyphX Pro [ring actions](https://www.cxpman.com/action-reference/control-surface-actions/#cs-n-ring-tx-sy).

## ClyphX Pro control surface actions

ClyphX Pro includes a variety of [control surface actions](https://www.cxpman.com/action-reference/control-surface-actions/), which can be used to interact with control surfaces. Many of these actions are compatible with zcx scripts.

## Referencing the ring from template strings

You can use the built in `ring` variable within template expressions to perform actions on tracks or scenes at a certain position within the ring.

`ring` has two attributes: `tracks` and `scenes`. We can index into either and retrieve the name of the track at that position of the ring, or the **zero-indexed** scene number at that position of the ring.

### Dynamic scene controls

```yaml
__scene_controls:
  includes: [
    scene_1, scene_2, scene_3, scene_4, scene_5, scene_6, scene_7, scene_8
  ]
  gestures:
    pressed: >
      SCENE ${ring.scenes[me.group_index] + 1}
```

Looking at [the above screenshot](#using-the-zcx-session-ring), if `scene_1` was pressed the action list `SCENE 1` would be executed, launching scene one.

If we [move the ring](#moving-the-ring) down two scenes, pressing `scene_1` would trigger the action list `SCENE 3`. `scene_2` would do `SCENE 4`.

### Dynamic track controls
```yaml
__state_controls:
  includes: [
    state_1, state_2, state_3, state_4, state_5, state_6, state_7, state_8
  ]
  gestures:
    pressed: >
       "${ring.tracks[me.group_index]}" / MUTE
```

Looking at [the above screenshot](#using-the-zcx-session-ring), if `state_1` was pressed, the action list `"fx gtr 2" / MUTE` would be executed.

### Out of bounds references

It is often valid to refer to tracks or scenes outside of the session ring by using a negative index, or an index that is greater than or equal to the width and height of the ring. For example:

- Using `"${ring.tracks[-1]}" / MUTE` will mute the track one to the left of the left edge of the ring.
- Using `"${ring.tracks[8]}" / MUTE` on a 8-track ring will mute the track one to the right of the right edge of the ring.
- Using `"SCENE ${ring.scenes[-8]}"` while the top edge of the ring is at scene 9 will launch scene 1.
