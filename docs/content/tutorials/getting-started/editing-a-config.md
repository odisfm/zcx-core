---
weight: 3
---

# editing a config

Alright, time to actually get started!

When you downloaded zcx, it should have come with a pre-populated `_config` folder. The files in here were lovingly designed by your hardware maintainer so that when you load zcx for the first time it actually does something.

Now it's time to make the something that it does be the something that we want it to do.

Because every MIDI controller has different physical controls, each config is slightly different. The demo config we'll follow along with comes from the Ableton Push 1. You can follow along with the demo config you have, and it should be fairly similar.


## important files

Inside the `_config` folder are quite a few files. We won't need most of them today. The files we're touching are these:

```
zcx/
├─ _config/
│  ├─ matrix_sections/
│  │  ├─ actions_top_left.yaml
│  ├─ matrix_sections.yaml
│  ├─ modes.yaml
│  ├─ named_controls.yaml
│  ├─ pages.yaml
```

_If you have a smaller matrix, the file `actions_top_left` might be called something like `actions_left`._


## pages.yaml

```yaml title="pages.yaml"
pages:
  main:
    - big_colors
  test_page:
    - actions_top_left
    - actions_bottom_right
    - actions_bottom_left
    - actions_top_right
  track_page:
    - actions_top_left
    - mega_launcher
    - track_half
```

Your `pages.yaml` probably looks something like this. The page `main` contains the section `big_colors`, which is the pretty gradient that appears when you load zcx. The section we'll be working on is `actions_top_left`, which appears on `test_page` and `track_page`.

To navigate between pages, you use one of the predefined controls on your hardware. The hardware-specific docs you received with your installation should explain which button(s) do this. On the Push 1, its the `state_row`, which is the second row of buttons below the display. **Note:** you can always redefine the page controls (or add more, or not engage with the pages system at all).

The order that pages appear in `pages.yaml` is their internal order within zcx. **Note:** pages in zcx are zero-indexed, so `main` is page 0, `test_page` is page 1, and `track_page` is page 2.

Feel free to change the order of pages:

```yaml title="pages.yaml"
pages:
  test_page:
    - actions_top_left
    - actions_bottom_right
    - actions_bottom_left
    - actions_top_right
  main:
    - big_colors
  track_page:
    - actions_top_left
    - mega_launcher
    - track_half
```

You also have the option to add an `order` key to your `pages.yaml` like so:

```yaml title="pages.yaml"
order:
  - test_page
  - track_page
  - main
```

The order here will take precedence.

And that's where we'll leave `pages.yaml` for this lesson.

## named controls

```yaml title="named_control.yaml"
mute:
  gestures:
    pressed: MUTE

solo:
   gestures:
     pressed: SOLO

metronome:
  gestures:
     pressed: METRO

new:
  gestures:
    pressed: ADDSCENE

duplicate:
  gestures:
    pressed: SCENEDUPE
```

Inside `named_controls.yaml` you'll find some control definitions that look like this. There will probably be some that look quite scary, but once you get the basics down you'll be able to easily read and compose them yourself (if you want!).

Lets have a look at the definition for `mute`:

```yaml title="named_controls.yaml"
mute:
  gestures:
    pressed: MUTE
```

Pretty simple. As you might have guessed, when we press the button labeled 'Mute' on the Push, zcx fires the ClyphX action `MUTE`, which mutes the currently selected track.

We can add more functionality to this button: what if when we held it down briefly, it muted all tracks in the set?

```yaml title="named_controls.yaml"
mute:
  gestures:
    pressed: MUTE
    pressed_delayed: ALL / MUTE
```

Make that edit, then [reload zcx](/docs/lessons/reloading-control-surfaces.md).

Now, when you hold down `mute`, every track in the set gets muted. Well, actually, as soon as you press `mute` the selected track is muted, then after a moment every other track is muted. This might not be what you want.

```yaml title="named_controls.yaml"
mute:
  gestures:
    released_immediately: MUTE
    pressed_delayed: ALL / MUTE
```

We've changed the [key](/docs/lessons/reading-zcx-configurations.md#keys-and-values) `pressed` to `released_immediately`. zcx supports six gestures, five of which you'll be familiar with if you've used G-Controls:

```
zcx_gestures:
  - pressed
  - pressed_delayed
  - released
  - released_immediately
  - released_delayed
  - double_clicked
```

This change means that a quick press and release of `mute` will mute the selected track, but if you press and hold, after a moment all tracks will be muted, without the in-between step of muting the selected track.

Cool, lets do a little more!


## modes

What if we wanted to have that `mute` button double as a solo button? We could add a `double_clicked` gesture with the action list `SOLO`, but its a small button and that's a bit tricky. 

The Push 1 has a `shift` button. We can make it so the `mute` button mutes by default, but solos when `shift` is held.

```yaml title="named_controls.yaml"
mute:
  gestures:
    released_immediately: MUTE
    pressed_delayed: ALL / MUTE
    pressed__shift: SOLO
```

That's all we need to do to add mode functionality to our control. By taking a default gesture and adding the suffix `__shift`, we're telling zcx to do a special action when the `shift` mode is active. Now obviously the `shift` mode is in effect while we hold the `shift` control, but how does that work? The logic for that is actually in this same file:


```yaml title="named_controls.yaml"
shift:
  gestures:
     pressed:
       mode_on: shift
     released:
       mode_off: shift
```

The only other thing we need is to have `shift` listed in our `modes.yaml`:

```yaml title="modes.yaml"
- shift
- select
```


You can have as many modes as you like. This config has a `select` mode configured, triggered when we hold the `select` button. We can even have an extra-special function that triggers when *multiple* modes are active:

```yaml title="named_controls.yaml"
mute:
  gestures:
    released_immediately: MUTE
    pressed_delayed: ALL / MUTE
    pressed__shift: SOLO
    pressed__shift__select: ALL / SOLO
    # for when you want to listen closely to EVERY track
```


## matrix controls

Let's take a look at the `actions_top_left` section. Its config file is `_config/matrix_sections/actions_top_left.yaml`.

```yaml title="_config/matrix_sections/actions_top_left.yaml"
#row 1  
#col 1  
- color: green  
  gestures:  
    pressed:  
    # pressed_delayed:  
    # released_immediately:    
    # double_clicked:
#col 2  
- color: grey  
  gestures:  
    pressed:  
    # pressed_delayed:  
    # released_immediately:    
    # double_clicked:
#col 3  
- color: grey  
  gestures:  
    pressed:  
    # pressed_delayed:  
    # released_immediately:    
    # double_clicked:
#col 4  
- color: grey  
  gestures:  
    pressed:  
    # pressed_delayed:  
    # released_immediately:    
    # double_clicked:
#row 2  
#col 1  
- color: grey  
  gestures:
```


This section was defined as a 4x4 quarter of the 8x8 pad matrix. This means it has 4 rows of controls, with 4 columns per row, for 16 controls total. This config file is pre-filled with a skeleton definition for each control, as well as helpful `#comments` indicating which control is which. 

The data structure you're looking at is called a [list](/docs/lessons/reading-zcx-configurations.md#lists). When you see a `-` that begins the line, that is the start of a new item (control) that belongs to this list.
```yaml title="actions_top_left.yaml"
# row 1
# col 1
-
    color: green
    gestures:
      pressed:
# col 2
-
    color: grey
    gestures:
      pressed:
```

If you like, you can start each list item with an empty line. You may find this easier to read.

And from here, editing controls is pretty much exactly the same as what we did for the [named controls](#named-controls). 

Most pad matrices have RGB feedback, so we can can set them to display many different colors:

```yaml
# col 2
- color: red
...
```

Make that change and reload - the pad is now red. 

Now scroll through all three pages of the matrix. You'll see that **two** pages now have a red button at x2y1. That's because in `pages.yaml`, we set the section `actions_top_left` to appear on multiple pages.

!!! tip

    The [strings](/docs/lessons/reading-zcx-configurations.md#strings) we've used so far have been free of 'single quotes' and "double quotes". ClyphX uses double quotes quite a bit, and this can cause a small problem with yaml:

    ```yaml
    gestures:
      pressed: "my cool track" / MUTE
    ```

    Because quotes have special significance in programming languages, this definition isn't valid yaml: it expects `my cool track` to be a complete string (without the quotes), and then freaks out a bit when it encounters `/ MUTE`. But we can easily work around that:
    
    ```yaml
    gestures:
      pressed: >
        "my cool track" / MUTE
    ```
    
    By writing our action list as above (putting a `>` after the key and writing the value on a new line), we're telling yaml that the entire line is the value we want to associate with `pressed`.



## ZEncoders

We define [encoder mappings](/docs/lessons/zcx-concepts.md#zencoders) in `encoders.yaml`.

```yaml title="encoders.yaml"
enc_master:
  binding:
    default: MST / VOL
    __shift: MST / CUE
```

By now, you should have a pretty good idea of what this definition does. By default, the `master` encoder is mapped to the volume on the master track, but when `shift` is held the encoder maps to the cue volume.

## A note on templating

Throughout these configuration files, you will have come across several quite complex definitions that look like this:

```yaml title="encoders.yaml"

__encoder_row:
  includes: [
    enc_1, enc_2, enc_3, enc_4, enc_5, enc_6, enc_7, enc_8
  ]
  binding:
    default: >-
      ${me.Index} / VOL
    __shift: >-
      ${me.Index} / PAN
    __device: >-
      SEL / DEV(1) P${me.Index}
  encoders:
    - binding:
        __sends: >-
          SEL / SEND A
    - binding:
        __sends: >-
          SEL / SEND B
    - binding:
        __sends: >-
          SEL / SEND C
    - binding:
        __sends: >-
          SEL / SEND D
    - binding:
        __sends: >-
          SEL / SEND E
    - binding:
        __sends: >-
          SEL / SEND F
    - binding:
        __sends: >-
          SEL / SEND G
    - binding:
        __sends: >-
          SEL / SEND H
```

A full explanation of what is happening above will be delivered in a future tutorial series. But the gist is:

We define a group of controls:

```yaml
__encoder_row:
  includes: [
    enc_1, enc_2, enc_3, enc_4, enc_5, enc_6, enc_7, enc_8
  ]
```

The name of the group is `__encoder_row`. We can tell it's a group at a glance by the leading double underscore `__`. This group name is completely arbitrary, but it **must** start with `__`.

A group of controls must also have the key `includes`. This is a [list](/docs/lessons/reading-zcx-configurations.md#lists) of named controls or encoders that form the group. You must use the [canonical](/docs/lessons/zcx-concepts.md#named-controls) names for each group member.

Here we have 'grouped' the Push's 8 main encoders. This lets us do two things.

### define common functionality
```yaml
binding:
    default: >-
      ${me.Index} / VOL
    __shift: >-
      ${me.Index} / PAN
    __device: >-
      SEL / DEV(1) P${me.Index}
```

All 8 encoders have the same* binding when in the `default`, `shift`, and `device` modes.

### rapidly prototype configs
The default binding is `${me.Index} / VOL`. `${me.Index}` will be unfamiliar syntax. When you see `${<some.value>}` you are looking at a zcx template string. 

Everywhere we use this syntax, behind the scenes zcx will resolve these template values. For `enc_1`, the final binding target will be `1 / VOL`, or the first track in the set. `enc_2` will resolve to `2 / VOL` and so on. Note: this is according to each control's position in the `encoders` key.

```
me: the control
Index: fancy word for position
```

The binding in `device` mode is `SEL / DEV(1) P${me.Index}`. This resolves as above, so `enc_7` will bind to `SEL / DEV(1) P7`.

We can actually put whole expressions inside template strings:
```yaml
__select: >
  ${me.Index + 8} / VOL
```
Now `enc_1` maps to `9 / VOL` when mode `select` is active.

## overriding group definitions

This config also has an `encoders` key:
```yaml title="encoders.yaml"
encoders:
    - binding:
        __sends: >-
          SEL / SEND A
    - binding:
        __sends: >-
          SEL / SEND B
    - binding:
        __sends: >-
          SEL / SEND C
```
Here, for each group member, we can define any number of properties to 'override' on the group definition.

```yaml title="encoders.yaml"
encoders:
    - 
    - null
    - binding:
        __sends: >-
          SEL / SEND C
```
You can leave a list entry blank, or write `null`, and no override will be applied for that control.

!!! quote ""I'd rather not use groups""

    You don't have to. You can remove or comment out the whole group definition, and define each control separately:

    ```yaml
    enc_1:
      binding:
        default: >
          "drums" / VOL
    
    enc_2:
      binding:
        default: >
          "keys" / VOL
    ```

# congratulations!

Well done! You now understand the basics of configuring zcx! Feel free to experiment!
