---
weight: -1000
---

# Troubleshooting

This lesson explains some common issues you may face with zcx, and steps you can take to troubleshoot.

!!! note "Reporting bugs"
    If you think you've found a bug, see [the lesson](reporting-bugs.md) to learn how to report it.

## Reading logs

zcx writes logs to two locations: [log.txt](../reference/file/log.md), located in your zcx folder, and Live's own log file.
The zcx log file only contains messages pertaining to that particular zcx script, while Live's log features messages from Live, ClyphX Pro, and any zcx scripts.
The zcx log file is helpful if you have multiple zcx scripts and/or a busy Live log, though some serious errors that prevent zcx from loading will only be written to Live's log, so check there if in doubt.

Live's log file can be found at:

**Windows:** `\Users\[username]\AppData\Roaming\Ableton\Live x.x.x\Preferences\Log.txt`
**Mac:** `/Users/[username]/Library/Preferences/Ableton/Live x.x.x/Log.txt`

You may configure the detail level of the log in [preferences.yaml](../reference/file/preferences.md#log_level).

### Reading logs in real time

#### Terminal commands

These terminal commands allow you to view the log without installing additional software.

##### macOS / Linux

From Terminal:

```bash
tail -f /path/to/logfile
```

Same as above, but takes a regex pattern that will be highlighted in a different color.

```bash
tail -f /path/to/logfile | grep --color=always -E 'regex-pattern|$'
```

##### Windows

From Powershell:

```ps1
Get-Content -Path "/path/to/logfile" -Wait
```

#### Apps

##### GUI 
- [Log-Viewer (macOS)](https://apps.apple.com/au/app/log-viewer/id1543753042?mt=12)

##### TUI
- [lnav (macOS/Linux)](https://lnav.org/)

## Common issues

### zcx doesn't appear in Live's control surface list

- Double-check you have correctly followed the [installation instructions](../lessons/getting-started/installation.md).
    - This includes making sure the script's MIDI ports are [properly assigned](../lessons/getting-started/installation.md#activate-the-script).
- If you are installing zcx for the first time, make sure to quit and re-open Live.
- Check Live's [Log.txt](#reading-logs) for errors relating to the script.

### Live shows a dialog saying zcx failed to load

- Try to make sense of the error message.
    - In many cases, the error is due to a misconfiguration. Where possible, the error will tell you the name of the file that is causing the error, the particular section of the file, and, potentially, steps to fix it.
- In many cases, the [log](#reading-logs) will have more detailed information.
- If the error has appeared right after making a change to your configuration, double-check your changes against the documentation to make sure you have followed it correctly.

### My configuration isn't working how I expect it to

- Double-check your configuration against the documentation to make sure you have followed it correctly.
    - If a particular control isn't working, check the [control reference](../reference/control/standard.md) to make sure you are spelling things correctly and supplying valid values.

### zcx is not registering input and/or is not displaying LED feedback

- If **neither** input nor output seems to work, check the [log](#reading-logs).
- Otherwise, ensure the script's MIDI ports are [properly assigned](../lessons/getting-started/installation.md#activate-the-script).

## Getting help

Feel free to ask for help in [the Discord](https://discord.zcxcore.com) by creating a new thread in `#help`.

### Providing information

You may be asked to provide either of the [log files](#reading-logs), and in some cases a complete copy of your zcx folder.
Locate your zcx folder, right-click, and select "Compress" (macOS) or "Compress to -> ZIP File" (Windows).
You may then drag this .zip file into your Discord message.

#### Attaching a single file

Simply drag-and-drop the file into your Discord message.

#### Pasting configuration snippets into Discord

If you simply paste yaml or ClyphX Pro code into Discord, it will not be properly formatted, and so will be very hard to read.
You can help by ensuring any code you send is enclosed in a [code block](https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline#h_01GY0DAKGXDEHE263BCAYEGFJA).

#### Privacy

When providing the log file, this will often contain the username of your computer account.
When providing a copy of your installation and config, this necessarily contains your intellectual property.
Keep in mind that the Discord server is essentially public.

If any of these issues is a concern, feel free to ask for help via direct message instead.
