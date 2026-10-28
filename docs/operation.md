![Just One More Moment](../hardware/diagrams/project-banner.svg)

# How my installation works

## The core experience

Visitors see my device's remaining runtime and generated language. They can press the physical button to extend its countdown or let the timer run out. I use this interaction to explore the effect of technical or emotional language on empathy and responsibility.

## Visual context

I connect a Logitech C270 to my Raspberry Pi through USB. In **Cloud AI + Cam** mode it provides visual context so the model can respond to visitors and their surroundings. **SW01** selects **Local AI / Cloud AI + Cam**.

## My controls

| Control | What I have documented |
| --- | --- |
| Arcade button | Extends the countdown; I still need to document the exact increment and handling from my code |
| SW01 | Local AI / Cloud AI + Cam - GPIO22 / P15, GND / P20 |
| SW02 | EN / DE - GPIO23 / P16, GND / P25 |

## Behavior I still need to document

- My startup and shutdown procedure.
- Initial runtime, time added per press, limits and reset behavior.
- What happens when the countdown reaches zero.
- The technical/emotional mode and any language selection.
- My webcam processing pipeline and update frequency in Cloud AI + Cam mode.
- Whether I retain image frames, how I indicate camera operation and how I inform visitors.
- What the device does when the model or camera is unavailable.

I keep the experience I intend to create separate from the details I still need to check in my implementation.
