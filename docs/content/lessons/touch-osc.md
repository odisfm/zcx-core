# Using TouchOSC as a zcx controller

[TouchOSC from Hexler](https://hexler.net/touchosc) is a great app that lets you create a virtual MIDI controller which can be used on devices like tablets, phones, and touchscreen computers.

It is possible to use a TouchOSC controller as the input to a zcx script.
To do so, you will need to [create a port](porting.md), with specifications that match your TouchOSC layout.

!!! note
    Instructions on creating a TouchOSC layout are outside the scope of this lesson.
    See [the official documentation](https://hexler.net/touchosc/manual/introduction).

## Live's control surface settings

Follow the [official manual](https://hexler.net/touchosc/manual/getting-started-midi) to establish a MIDI connection between Live and your TouchOSC device.
Once set up, set `TouchOSC Bridge` as the input and output of your zcx script.

## OSC output from zcx

zcx features [OSC output](osc-output.md).
By following the [TouchOSC manual](https://hexler.net/touchosc/manual/editor-messages-osc), you can bring this information into TouchOSC.

**Note:** OSC cannot be used as an **input** to zcx, only MIDI.

## Notes

* When using the TouchOSC Grid control to create a button matrix, you must set the `Start` [property](https://hexler.net/touchosc/manual/controls#grid) to `BOTTOM LEFT`.
* Feedback from zcx is designed to work with hardware controllers, and may produce unexpected results with TouchOSC. One workaround is to set a [global control template](../reference/template.md#control-templates) with the option `suppress_animations: true`.
