---
title: reading zcx configurations
weight: 1
---

# reading zcx configurations

If you're coming from the [X and G controls in ClyphX Pro](https://www.cxpman.com/manual/using-midi-controllers/), looking at the configuration files in your zcx folder may feel overwhelming. Don't stress — you don't need to have any sort of programming knowledge to get started with zcx! 

Having said that, just like ClyphX, zcx expects to receive its configuration files in a particular format.

## X-Controls and ZControls

To define X-controls, ClyphX uses a custom format, designed for simplicity:

```ClyphX
RECORD = CC, 1, 79, 127, 0, SRECFIX 8
```

ClyphX also has G-controls, which have more complex functionality, and so need more complex configuration:

```ClyphX
RECORD = CC, 1, 79, 127, 0, FALSE,
RECORD PRESSED = SEL / ARM
RECORD PRESSED_DELAYED = SRECFIX 8
```

Here's the same button, defined as a ZControl:

```yaml
play:
  color: green
  gestures:
    pressed: SEL / ARM
    pressed_delayed: SRECFIX 8
```

At the same time, the above definition may look more complex, yet easier to read. Notice that your web browser is color coding certain words. This is because zcx makes heavy use of an existing format called [YAML](https://en.wikipedia.org/wiki/YAML)

## YAML
> "yam-il"

So what is yaml? Put simply, yaml is a format for organising data in a structured way, making it easy for humans to write, and easy for machines to understand. We'll explain the most important stuff you need to get started with zcx in a moment, but if you'd prefer to watch a video, [this one](https://www.youtube.com/watch?v=cdLNKUoMc6c) does a great job of explaining the basics (watch until about 5:30).

## keys and values

`key: value`

Yaml works by associating __keys__ with __values__. Take `color: green`. `color` is the **key**, and `green` is the **value**. Easy, right? We can represent an X-control in yaml like this:

```yaml
control_name: record
message_type: cc
midi_channel: 1
cc_number: 79
on_color: 127
off_color: 0
action_list: SRECFIX 8
```

Instead of putting everything on one long line, separated by commas, we label the data with a **key**, and pair it with a **value**.

## data types

Yaml is capable of representing many different categories of data. With zcx, you'll only need a few:
#### numbers
`color: 127`

You know what numbers are.
### strings
`color: green`

The word 'string' is a bit scarier, but it really just means that the data is a word, or a name, or a sentence, or an action list. Basically, it's got letters.

### booleans
`repeat: true`

Either true or false.

### lists
`includes: [scene_1, scene_2, scene_3, scene_4]`

Literally just a list of values. Those values could be numbers, strings, both, or something else entirely.

### # comments
```yaml
octave_up:
  # repeat: True
  gestures:
    pressed: METRO # I can write whatever I want here
```

When you see a  `#` on a line of yaml, anything to the right of that `#` will be totally ignored. If you put a `#` before the key, like with `# repeat` above, this line essentially 'disappears' from your config when zcx loads it. So, not actually a data type, but important to know.

### nested yaml

We can also 'nest' yaml **objects** inside each other:

```yaml
color:
  pulse:
    a: red
    b: purple
    speed: 1
```

And what is an **object**? Just another set of key-value pairs. 😎

# easy, right?

Don't stress if this doesn't immediately 'click'. Soon, you'll see a lot of examples of zcx definitions and configuration files, which will help to solidify these concepts!

**One more thing:**

Yaml files are plain old text, which means you can read and edit them with any text editor, like Notepad or TextEdit. However, it is recommended that you use a more sophisticated editor, such as [Microsoft Visual Studio Code](https://code.visualstudio.com/), which is free. Using an editor like this will give you that groovy color coding you see above, and the editor will warn you when you make common yaml errors.
