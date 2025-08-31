---
title: reading zcx configurations
weight: 1
---

# reading zcx configurations

If you're coming from the [X and G controls in ClyphX Pro](https://www.cxpman.com/manual/using-midi-controllers/), looking at the configuration files in your zcx folder may feel overwhelming. Don't stress — you don't need to have any sort of programming knowledge to get started with zcx! 

Having said that, zcx expects to receive its configuration files in a particular format, just as ClyphX does.
It's important to understand this format, otherwise your zcx script may fail to load, or behave in undesirable ways.

## X-Controls vs ZControls

You'll already be familiar with X-Controls from ClyphX:

```ClyphX
RECORD = CC, 1, 79, 5, 0, SRECFIX 8
```

ClyphX also has G-controls, which have more complex functionality, and need more detailed configuration:

```ClyphX
RECORD = CC, 1, 79, 5, 0, FALSE
RECORD PRESSED = SEL / ARM
RECORD PRESSED_DELAYED = SRECFIX 8
```

To define this G-control in zcx, we'd write it like so:

```yaml
record:
  color: red
  hold_color: off
  repeat: false
  gestures:
    pressed: SEL / ARM
    pressed_delayed: SRECFIX 8
```

At the same time, the above definition may look more complex, yet easier to read. Notice that your web browser is color coding certain words. This is because zcx makes heavy use of an existing format called [YAML](https://en.wikipedia.org/wiki/YAML)

## YAML
> "yam-il"

So what is yaml? Put simply, yaml is a format for organising data in a structured way, making it easy for humans to write, and easy for machines to understand. We'll explain the most important stuff you need to get started with zcx in a moment, but if you'd prefer to watch a video, [this one](https://www.youtube.com/watch?v=cdLNKUoMc6c) does a great job of explaining the basics (watch until about 5:30).

<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/cdLNKUoMc6c?si=kwPVI7QHkK9zygx3" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
 

## keys and values

`key: value`

Yaml works by associating __keys__ with __values__. Take `color: green`. `color` is the **key**, and `green` is the **value**. We can imagine an X-Control in yaml like this:

```yaml
control_name: record
message_type: cc
midi_channel: 1
cc_number: 79
on_color: 5
off_color: 0
action_list: SRECFIX 8
```

Instead of putting everything on one long line, separated by commas, we label the data with a **key**, and pair it with a **value**.

When we have a collection of key-value pairs, we call it an **object**.

## data types

Yaml is capable of representing many different categories of data. With zcx, you'll only need a few:

#### numbers
`color: 127`

When you provide a number, it will usually be a whole number.
In these docs you might see the term "integer" or "int" — this just means a whole number.

Less commonly, you might provide decimal number values:

`midpoint: 55.3`

### strings
`color: green`

The word "string" just means the data is some textual value.

```yaml hl_lines="2 3 5"
my_control:
  color: green
  alias: my_cool_control
  gestures:
    pressed: METRO ON ; SEL / ARM ;
```

It might be a word, sentence, or a ClyphX Pro action list.

#### complex strings

In many zcx configs, you will see a peculiar format:

```yaml
pressed: >
  "my cool track" / SEL ; "my cool track" / ARM
```

This is still a string.
When we have strings with special characters (like "double-quotes"), we need to format them differently or yaml will fail to process them.
Here we have put a `>` character after the key: `pressed: >`, and put the value below, on its own line.


You may also use this format:

```yaml
pressed: '"my cool track" / SEL ; "my cool track" / ARM'
```

Here, we have wrapped the entire action list in 'single quotes', which achieves the same result.

### booleans
`repeat: true`

Either `true` or `false`.

### lists
`includes: [scene_1, scene_2, scene_3, scene_4]`

A list of values. 
Those values could be numbers, strings, objects, or even a mix of different data types.

You may see lists formatted in a few different ways:

```yaml
my_list: [scene_1, scene_2, scene_3, scene_4]
```
```yaml
my_list: [
  scene_1, scene_2, scene_3, scene_4
]
```
```yaml
my_list:
  - scene_1
  - scene_2
  - scene_3
  - scene_4
```

These three examples are functionally identical.

### # comments
```yaml
octave_up:
  # repeat: True
  gestures:
    pressed: METRO # I can write whatever I want here
```

When you see a  `#` on a line of yaml, anything to the right of that `#` will be totally ignored. If you put a `#` before the key, like with `# repeat` above, this line essentially 'disappears' from your config when zcx loads it. So, not actually a data type, but important to know.

### objects

We can also 'nest' yaml **objects** inside each other:

```yaml
color:
  pulse:
    a: red
    b: purple
    speed: 1
```

You can identify a nested object by the **indentation**.
Indentation means how much space there is on the left of the line.

To demonstrate, here's the above object with `#`s where there should be spaces:

```
color:
##pulse:
####a: red
####b: purple
####speed: 1
```

In this example, the top-level object is `color`.
```yaml hl_lines="1-5"
color:
  pulse:
    a: red
    b: purple
    speed: 1
```

`color` has one key-value pair, `pulse`.
```yaml hl_lines="2-5"
color:
  pulse:
    a: red
    b: purple
    speed: 1
```

`pulse` is an object too, and it has three key-value pairs, `a: red`, `b: purple`, and `speed: 1`.

```yaml hl_lines="3-5"
color:
  pulse:
    a: red
    b: purple
    speed: 1
```

#### lists of objects

You will often see [lists](#lists) of objects:

```yaml
controls:
  - color: red
    repeat: true
  - color: blue
    repeat: false
```

This is a list of two objects.
The first object has `color: red` and `repeat: true`.
The second has `color: blue` and `repeat: false`.

You may use different formatting to distinguish different items in the list:

```yaml
controls:
  - color: red
    repeat: true
    
  - color: blue
    repeat: false
```

Or even:

```yaml
controls:
  -
    color: red
    repeat: true
  -  
    color: blue
    repeat: false
```

## using a code editor

Yaml files are plain old text, which means you can read and edit them with any text editor, like Notepad or TextEdit. 
However, it is **highly** recommended that you use a more sophisticated editor, such as [Microsoft Visual Studio Code](https://code.visualstudio.com/), which is free. 
Using an editor like this will give you that groovy color coding you see above.
The editor will also warn you when you make common yaml errors.

## conclusion

Don't stress if this doesn't immediately 'click'. 
Soon, you'll see a lot of examples of zcx definitions and configuration files, which will help to solidify these concepts!
