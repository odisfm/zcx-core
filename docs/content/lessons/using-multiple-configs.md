# Using multiple configurations

zcx allows you to have multiple configurations, and load a different one based on the name of your Live set (the name of your .als file).

To create an alternative config folder, first create a new folder in the same location as your old folder. This new folder must be prefixed with `_config_`, with a name of your choice following, e.g. `_config_dj`, `_config_solo_set`, `_config_mixing`.

Then, you will need to edit your preferences file, located in `<your zcx folder>/preferences/preferences.yaml`.

```yaml title="preferences.yaml"
configs:
  - config: dj
    pattern: dj_set
    
  - config: solo_set
    pattern: >
      [solo]

  - config: mixing
    pattern: MIX
```

The `config` field is the name of the config to load, while the `pattern` field is a [regex pattern](https://en.wikipedia.org/wiki/Regular_expression).

Regular expressions don't need to be complex — the above patterns will match if they are found anywhere in the set name, i.e. a set called `my cool song [solo]` would load the `solo_set` config. `!!!MIX! sound of the summer` will load the `mixing` config, etc.

If no pattern matches, the default config (`_config`) will be loaded.

!!! note
    zcx only checks the set name when the control surface is reloaded.

    After renaming the set, you may load the new config by [reloading zcx](reloading-control-surfaces.md)
