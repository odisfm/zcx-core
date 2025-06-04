# OSC output from zcx

zcx will send [Open Sound Control](https://en.wikipedia.org/wiki/Open_Sound_Control) (OSC) messages on certain events.
This may be useful for interfacing with other systems, such as [TouchOSC](https://hexler.net/touchosc).

## Configuring the OSC server

zcx uses the existing OSC server provided by ClyphX Pro.
Thus, to configure the server, you must modify the [ClyphX Pro configuration file](https://www.cxpman.com/manual/core-concepts/#settings-foldersfiles) `Preferences.txt`.

Near the bottom of this file, under the label `OSC SETTINGS`, you should have a line like:

`INCOMING_OSC_PORT = 7005`

You must add two lines below this line:

``` title="Preferences.txt" hl_lines="4-5"
*** [OSC SETTINGS] ***

INCOMING_OSC_PORT = 7005
OUTGOING_OSC_PORT = 7000
OSC_DEVICE_IP_ADDRESS = 127.0.0.1
```

!!! warning
    The above settings are an example only; they will need to be set according to your network and situation.

## OSC namespace

An OSC message sent from zcx will use an address like this:

`zcx/zcx_push_1/enc/enc_1/value`

The first part, `zcx`, indicates that the message comes from a zcx script, which is useful when using an external tool to route messages.

The second part, `zcx_push_1`, is the name of the particular zcx script sending the message.
This is useful when using multiple zcx scripts simultaneously, as it allows you to route messages per-script.

One such routing tool is [OSCRouter](https://github.com/ETCLabs/OSCRouter) from ETC Labs.
    
## Available outputs

### Encoder mappings

For encoders, zcx will send the name of the mapped parameter, as well as the value as several datatypes.
You may configure the datatypes sent in [preferences.yaml](/reference/configuration-files/preferences/#osc_output).

#### name

The name of the mapped parameter, as it appears in the Live UI:

Address: `zcx/<script name>/enc/<encoder name>/name`

Value: string

#### value

The value of the mapped parameter, as it appears in the Live UI:

Address: `zcx/<script name>/enc/<encoder name>/value`

Value: string

#### int

The value of the mapped parameter, as an integer between 0-127:

Address: `zcx/<script name>/enc/<encoder name>/int`

Value: int

#### float

The value of the mapped parameter, as a float between 0.0 - 1.0:

Address: `zcx/<script name>/enc/<encoder name>/float`

Value: float

### Page changes

zcx will send messages when the page is changed.

#### page number

Address: `zcx/<script name>/page/number/<current page number>`

Value: int

#### page name

Address: `zcx/<script name>/page/name/<current page name>`

Value: string
