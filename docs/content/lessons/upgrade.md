# upgrading your zcx installation

To get access to the latest features and bugfixes, you should keep your zcx installation(s) up to date.
If you use multiple zcx installations (for different controllers), you need to upgrade each install separately.

## automatic upgrade

Starting from v0.5, you can use the Python script `upgrade.py` to get the latest release from GitHub.

This script will:

- Backup your existing installation to `Remote Scripts/__zcx_backups__`
- Download the newest release
- Replace all application code with the newest version
- Restore your configuration files
- Install or upgrade the [zcx user action](zcx-user-action.md).

### running the script

To run the script, you will need to [download and install Python](https://www.python.org/downloads/).
Once you've done that, open a terminal or PowerShell window and navigate to your zcx installation, and run the script.

**macOS**
```shell
cd "~/Music/Ableton/User Library/Remote Scripts/<your zcx folder>"
python3 upgrade.py
```

**Windows**
```commandline
cd "\Users\<username>\Documents\Ableton\User Library\Remote Scripts\<your zcx folder>"
python upgrade.py
```

!!! note
    The paths above are the defaults. You will need to modify them if your User Library is in a different location.

## manual upgrade

- Copy your entire install (i.e. `User Library/Remote Scripts/_zcx_<hardware name>`) to a safe place, such as your desktop
- Follow the [installation procedure](getting-started/installation.md) for the latest zcx version
- Inside the newly installed zcx folder, delete the folder `_config` and the file `_global_preferences.yaml`
- From your old install, copy and paste `_config` and `_global_preferences.yaml` into the new install
