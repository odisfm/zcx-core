# Screensaver

Have you seen the videos where people create [lightshows on their Launchpads?](https://www.youtube.com/watch?v=EUW480TtH1M)

Let's make a button that turns one on!

## The lightshow

Creating a lightshow from scratch is out of the scope of this recipe.
We'll be using a really cool, free, Max for Live Device called [SS4V-PushIllumination.](https://maxforlive.com/library/device/3231/ss4v-pushillumination)

!!! note "Don't have Max?"
    If you don't have Max for Live, check out [one of these videos](https://www.youtube.com/results?search_query=create+launchpad+lightshow) about creating a lightshow manually.

Download that device and add it to a track.
Set the MIDI out of that track to the zcx script you want to light.

Select a preset from the dropdown ("Gradation" and "Psychedelic" are cool), and click the "Preview" button.
Your matrix should now play the lightshow.

## The problem

So the lightshow works, but what about turning it off?
We can set up a control to toggle the lightshow device on and off, but when turning it off, our matrix LEDs turn off.
Also, pressing the matrix will still fire the normal commands, and we'd prefer if it did nothing.

## The solution

Let's create a [matrix page](../lessons/getting-started/zcx-concepts.md#pages) dedicated to the lightshow.
First, we'll need a [matrix section](../lessons/getting-started/zcx-concepts.md#matrix-sections), so we'll make a full size one called `lightshow`:

```yaml title="matrix_sections.yaml"
lightshow:
  row_start: 0
  row_end: 7
  col_start: 0
  col_end: 7
  template:
    suppress_animations: true
```

!!! tip
    Since we're using a [section template](../reference/template.md#section-templates), we don't need to create the file `lightshow.yaml` unless we want to define gestures for when the lightshow is playing.

Then, add a new page, also called `lightshow`:

```yaml title="pages.yaml" hl_lines="4-6"
pages:
  blank_page:
    - blank_section
  lightshow:
    sections:
      - lightshow
```

Now we can use this page's [on_enter and on_leave commands](../reference/file/pages.md#on_enter-on_leave) to turn the lightshow device on and off.
To simplify (or complicate) things, let's rename the lightshow device to `lightshow`, and the track containing it to `lightshow` as well.

```yaml title="pages.yaml" hl_lines="7-14"
pages:
  blank_page:
    - blank_section
  lightshow:
    sections:
      - lightshow
    on_enter: >
      "lightshow" / DEV("lightshow") "preview" 127
    on_leave: >
      "lightshow" / DEV("lightshow") "preview" 0 ;
      WAIT 1 ;
      ZCX ${this_cs} REFRESH ; 
```

For `on_leave`, we're using the ClyphX Pro [WAIT](https://www.cxpman.com/action-reference/global-actions/#wait-x) action to wait 100 milliseconds, then the [zcx user action](../lessons/zcx-user-action.md#refresh) to force zcx to refresh all LED feedback.

If you don't already have some buttons set up as a page changer, you'll need to set a button up to activate the lightshow page:

```yaml title="named_controls.yaml"
quantize:
  gestures:
    pressed_delayed:
      page: lightshow
```

## Extra credit

- Use the lightshow device to generate a bunch of clips, then create a [group of controls](../reference/template.md#group-templates) dedicated to firing those clips, triggering a different lightshow.
    - You'll want to change your action lists to mute and un-mute the lightshow track.
- Put a [velocity device](https://www.ableton.com/en/manual/live-midi-effect-reference/#velocity) or two on the track and [map some encoders](../reference/encoder.md) to alter the lightshow's colors.
