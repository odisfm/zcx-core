---
weight: -7
---
# param_g control

The `param_g` control is a variant of the [param control](param.md).
While `param` controls have only an `on_color` and `off_color`, `param_g` controls have a color gradient that can represent [continuous values](https://www.cxpman.com/manual/general-action-information/#continuous-parameters), rather than just binary values.

`param_g` controls should generally be preferred over `param` controls, unless you desire a binary representation, or if you are using non-RGB buttons.

This article only deals with the options specific to `param_g` controls.
See the [param control](param.md) article for options available on both.

## yaml schema

Inherits from [param control](param.md#yaml-schema).

```yaml
gradient: list[color definition]
q_gradient: list[color definition]
```

### gradient
`list[color defintion]`

A list of colors that should be used to represent a continuous parameter.
Colors at the start of the list represent higher values.
You can specify any number of colors.

By default, a red-pink-purple gradient will be used.

**Example:**
```yaml
gradient: ["yellow", 8, "green", 21, "pink", "purple"]
```

### q_gradient
`list[color definition]`

A list of colors that should be used to represent a quantized parameter.
A quantized parameter is one that has distinct options that, e.g. the `Amp` device's `Amp Type` parameter has options like `Clean`, `Lead`, and `Bass`, which cannot be blended between.

By default, a rainbow gradient will be used.
