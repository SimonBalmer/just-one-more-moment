![Just One More Moment](../hardware/diagrams/project-banner.svg)

# How my installation works

## The core experience

Visitors see my device's remaining runtime and generated language. They can press the physical button to extend its countdown or let the timer run out. I use this interaction to explore the effect of technical or emotional language on empathy and responsibility.

## Visual context

I connect a Logitech C270 to my Raspberry Pi through USB. It provides visual context so the model can respond to visitors and their surroundings. I plan to make this input optional through a physical switch.

## My controls

| Control | What I have documented |
| --- | --- |
| Arcade button | Extends the countdown; I still need to document the exact increment and handling from my code |
| Toggle switch 1 | GPIO22; I still need to record its actual function and position mapping |
| Toggle switch 2 | GPIO23; I still need to record its actual function and position mapping |

## Behavior I still need to document

- My startup and shutdown procedure.
- Initial runtime, time added per press, limits and reset behavior.
- What happens when the countdown reaches zero.
- The technical/emotional mode and any language selection.
- My webcam processing pipeline, update frequency and planned disable option.
- Whether I retain image frames, how I indicate camera operation and how I inform visitors.
- What the device does when the model or camera is unavailable.

I keep the experience I intend to create separate from the details I still need to check in my implementation.
