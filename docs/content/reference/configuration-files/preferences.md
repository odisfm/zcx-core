---
weight: -1
---

# preferences.yaml

`preferences.yaml` allows you to customise various settings of the zcx script. 

## two levels of preferences

At the root of your zcx installation is a file `_global_preferences.yaml`.
Inside your `_config` folder, you may create the file `preferences.yaml`.

As zcx allows [per-set configs](/lessons/using-multiple-configs/), the purpose of having multiple files is to allow you to have certain preferences across all of your configs, and expand or modify those preferences per-config.
If you only use one zcx config, you may choose to use either of these files.

## preference reference

Each of these headings represents a top-level yaml entry.

### action_log

```yaml
action_log: true
```

When set to `true`, all triggered ClyphX Pro action lists will be logged.

### configs

Allows you to configure [per-set configs](/lessons/using-multiple-configs/).

**This setting must be set in `_global_preferences.yaml`**

```yaml
configs:
  - config: dj
    pattern: dj_set

  - config: solo_set
    pattern: >
      [solo]

  - config: mixing
    pattern: MIX
```


### inital_hw_mode
```yaml
initial_hw_mode: zcx
```

Options:

- `zcx` - When zcx loads, switch the device to user mode.
- `live` - Do not attempt to take control of the hardware on set load.

### load_hardware_plugins

```yaml
load_hardware_plugins: true
```

Determines whether any hardware-specific plugins (located in `zcx/hardware/plugins`) will be loaded.

### load_user_plugins

```yaml
load_user_plugins: true
```

Determines whether any user plugins (located in `zcx/plugins`) will be loaded.

### log_level

```yaml
logging: info
```

Configures how detailed the zcx logs are. From most to least detailed, the options are:

- debug
- info
- warning
- error
- critical

### osc_output

```yaml
osc_output:
  encoders:
    name: true
    value: true
    int: true
    float: true
  page: true
  ring_tracks: true
  ring_pos: true
```

Configures what information is sent over OSC. 
`osc_output: false` disables all OSC output.

See [full lesson](/lessons/osc-output) for more details.

### plugins

```yaml
plugins:
  plugin_name:
    plugin_option_1: true
    plugin_option_2: false
```

Consult the documentation of your plugin to see the available options.
If the plugin came with zcx you will find this information in the [hardware reference](/reference/hardware-reference) for your controller.

### session_ring
```yaml
session_ring:
  width: 8
  height: 8
```

Sets the dimensions of the [session ring](/lessons/session-ring).
You may disable the ring by setting one or both of `width` and `height` to `0`.

## developer preferences

The following preferences are only useful when developing the 'core' of zcx.

### refresh_on_all_sysex

```yaml
refresh_on_all_sysex: false
```

When set to `true`, zcx will refresh all LED feedback upon receipt of **any** MIDI Sysex message.
This may be useful if you are trying to test controller-specific code for a controller you don't have access to.
