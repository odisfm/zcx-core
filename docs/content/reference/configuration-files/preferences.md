# preferences.yaml

`preferences.yaml` allows you to customise various settings of the zcx script. 

## two levels of preferences

At the root of your zcx installation is a file `_global_preferences.yaml`.
Inside your `_config` folder, you may create the file `preferences.yaml`.

As zcx allows [per-set configs](/lessons/using-multiple-configs/), the purpose of having multiple files is to allow you to have certain preferences across all of your configs, and expand or modify those preferences per-config.
If you only use one zcx config, you may choose to use either of these files.

## preference reference

Each of these headings represents a top-level yaml entry.

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

### session_ring
```yaml
session_ring:
  width: 8
  height: 8
```

Sets the dimensions of the [session ring](/lessons/using-the-zcx-session-ring).
You may disable the ring by setting one or both of `width` and `height` to `0`.

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

### allow_python_command

```yaml
allow_python_command: false
```

Enables the [Python command type](/reference/command-reference#python).
