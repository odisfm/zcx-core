# modes.yaml

Simply a list of the names of the [modes](../../lessons/getting-started/zcx-concepts.md#modes) you would like to use in your config.

```yaml title="modes.yaml"
- shift
- select
- my_mode
```


For more info, see the sub-section of [zcx concepts](../../lessons/getting-started/zcx-concepts.md#modes).

## Firing command bundles on mode changes

You may fire a [command bundle](../command-reference.md#command-bundles) when a mode is enabled, disabled, or toggled.
Instead of specifying just the mode name as a string, you should specify an object like so:

```yaml title="modes.yaml" hl_lines="2-6"
- shift
- mode: select
  on_enter: METRO ON
  on_leave: METRO OFF
  on_toggle:
    msg: metro toggled
- my_mode
```
