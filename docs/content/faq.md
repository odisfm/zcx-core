---
title: faq
hide:
  - navigation
---

# frequently asked questions

### What's all this then?

Have a look at the [about page](index.md), or check out [the source on GitHub](https://www.github.com/odisfm/zcx-core).

### What do I need to use zcx?

* Ableton Live 12.1 or above <sup>[why?](#why-does-zcx-require-live-121)</sup>
* ClyphX Pro 1.3.1 or above
* [Supported hardware](index.md#hardware)
* A heart full of dreams

### Does zcx change the default functionality of my control surface

For most zcx-enabled controllers, there are two modes: Live mode, which is the default control surface script, and user mode, designed for custom mapping, or scripts like zcx.

zcx only works on the user mode of your controller.
This means that the default functionality of your controller is unaffected.
You may use the default script and zcx simultaneously on one controller, switching between modes with the controller's `User` button.
Doing so requires two control surface slots; one for each script.
If you don't want to use the default functionality, you can unassign the default script.

### Do I need to be a coder to use zcx?

No programming knowledge is necessary to configure zcx. zcx configurations **do** make extensive use of a format called [yaml](lessons/getting-started/reading-zcx-configurations.md/#yaml), but it's pretty easy to pick up.

See also: [reading zcx configurations](lessons/getting-started/reading-zcx-configurations.md).

### What hardware is zcx available for?

[See here.](lessons/getting-started/installation.md#get-a-distribution)

### Does zcx replace ClyphX Pro?

Nope. zcx provides a way to interact with ClyphX Pro that greatly expands your possibilities for performing with hardware controllers.

### Does zcx replace X-controls and G-controls

That's up to you. zcx can be used to create a far more complex interface than is practical with native ClyphX Pro. However, that power comes with a learning curve. Only you can decide whether this tradeoff is worth it.

**Note:** You can absolutely use X/G Controls alongside a zcx script. It is recommended that you use zcx for any matrix controllers, and native ClyphX Pro controls for non-matrix controllers.

### Can I use zcx with a non-matrix controller?

zcx is designed for matrix-equipped controllers. You could [make a port](lessons/porting.md) for your hardware, and just not use the matrix features. That's up to you. Remember: each zcx script requires its own control surface slot.

### Why does zcx require Live 12.1?

zcx is written in the Python programming language. With newer versions of Python, developers have access to more features when writing code. 

The Python environment that zcx runs in is provided by Live. With Live 12.1 came an upgrade to Python 3.11.6. 
This newer version of Python includes several features that are very useful for zcx, and so early in development, a decision was made to target Live 12.1 as the minimum version compatible with zcx.


### Is there a Discord?

[But of course.
](https://discord.zcxcore.com)

### How can I contribute?

[See here](dev/contributing.md).

### What does 'zcx' stand for?

**Z**really<br>
**C**ool<br>
**X**thingo
