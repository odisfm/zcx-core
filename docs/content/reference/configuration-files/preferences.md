---
weight: -1
---

# preferences.yaml

`preferences.yaml` allows you to customise various settings of the zcx script. 

## two levels of preferences

At the root of your zcx installation is a file `_global_preferences.yaml`.
Inside your `_config` folder, you may create the file `preferences.yaml`.

As zcx allows [per-set configs](../../lessons/using-multiple-configs.md), the purpose of having multiple files is to allow you to have certain preferences across all of your configs, and expand or modify those preferences per-config.
If you only use one zcx config, you may choose to use either of these files.

## preference reference

Each of these headings represents a top-level yaml entry.

### action_log

```yaml
action_log: true
```

When set to `true`, all triggered ClyphX Pro action lists will be logged.

### configs

**This setting must be set in `_global_preferences.yaml`**

Allows you to configure [per-set configs](../../lessons/using-multiple-configs.md).

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

### force_config

**This setting must be set in `_global_preferences.yaml`**

Override [pattern matching for per-set configs](#configs) and explicitly load the specified config, or the default config.

```yaml
force_config: dj
```

Load config from the folder `_config_dj/`

```yaml
force_config: null
```

Load the default config `_config/`

### initial_hw_mode
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

### log_failed_encoder_bindings

```yaml
log_failed_encoder_bindings: true
```

By default, when an [encoder](../encoder-reference.md) fails to bind to the specified target an error message is written to the log.
In some cases, it may be expected that bindings fail, so you may set this option to `false`.

### log_level

```yaml
log_level: info
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

See [full lesson](../../lessons/osc-output.md) for more details.

### plugins

```yaml
plugins:
  plugin_name:
    plugin_option_1: true
    plugin_option_2: false
```

Consult the documentation of your plugin to see the available options.
If the plugin came with zcx you will find this information in the [hardware reference](../hardware-reference/index.md) for your controller.

### session_ring
```yaml
session_ring:
  width: 8
  height: 8
```

Sets the dimensions of the [session ring](../../lessons/session-ring.md).
You may disable the ring by setting one or both of `width` and `height` to `0`.

### startup_command
```yaml
startup_command:
  mode_on: shift
  cxp: METRO
```

Fire a [command bundle](../command-reference.md#command-bundles) when the script is finished loading.

### startup_page

```yaml 
startup_page: 2
```

```yaml 
startup_page: home_page
```

```yaml
startup_page: ${2 if "dj" in song.name else 0}
```

Set the page that is active when the script loads.

**Alternatively:**

- Use a [startup_command](#startup_command)
- Set a [page order](pages.md#order)

## developer preferences

The following preferences are only useful when developing the 'core' of zcx.

### refresh_on_all_sysex

```yaml
refresh_on_all_sysex: false
```

When set to `true`, zcx will refresh all LED feedback upon receipt of **any** MIDI Sysex message.
This may be useful if you are trying to test controller-specific code for a controller you don't have access to.
