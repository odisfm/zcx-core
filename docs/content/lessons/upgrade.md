# upgrading your zcx installation

To get access to the latest features and bugfixes, you should keep your zcx installation(s) up to date.
If you use multiple zcx installations (for different controllers), you need to upgrade each install separately.

!!! danger
    ![Snake from 'The Simpsons' saying 'Oh, no! Beta.'](/lessons/img/oh-no-beta.jpg)
    
    zcx is pre v1. This means it's very likely a new version will have **breaking changes**.
    'Breaking changes' basically means that if you upgrade, your old config might rely on features that work differently now.
    You may even have to move, rename, or delete certain files to make your old config compatible.
    
    To see if you are affected by any breaking changes, read the [releases page](https://github.com/odisfm/zcx-core/releases) on GitHub.

## automatic upgrade

Starting from v0.5, you can use the Python script `upgrade.py` to get the latest release from GitHub.

This script will:

- backup your existing installation to `Remote Scripts/__zcx_backups__`
- Download the newest release
- Replace all application code with the newest version
- Restore your configuration files
- Install or upgrade the [zcx user action](/lessons/zcx-user-action).

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

