# page control

The `page` control is identical to the `standard` control, except it has a required `page` property. This control's LED feedback will reflect whether its bound page is currently active. As such, the `color` property is ignored. 

**Note:** standard controls are already capable of changing pages, and page controls still require you to manually define the page change commands.


## yaml schema

```yaml
page: string, int
# color: not implemented
```

### page
`string | int`

The page name or number this control is bound to. Passing a string value means that the binding is resistant to page order changes, while passing an int may be suitable for a dedicated 'page row'.

**Note:** page numbers are always zero-indexed.

___
### color
`not implemented`

LED feedback is based on whether the control's bound page is active.
