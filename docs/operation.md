# Operation and interaction

## Core experience

Visitors see the device's remaining runtime and generated language. They can press a physical button to extend its countdown or let the timer run out. The project explores the difference between technical and emotional language and its effect on empathy and responsibility.

## Visual context

A Logitech C270 is connected to the Raspberry Pi through USB. The builder reports that it provides visual context for the model, allowing responses to refer to spectators and their surroundings. Disabling this input through a physical switch is planned.

## Physical controls

| Control | Current documentation |
| --- | --- |
| Arcade button | Extends the countdown; exact increment and handling to document from code |
| Toggle switch 1 | GPIO22; actual function and position mapping pending |
| Toggle switch 2 | GPIO23; actual function and position mapping pending |

## Behavior to document with the implementation

- Startup and shutdown procedure.
- Initial runtime, time added per press, limits and reset behavior.
- Behavior at zero: this is not yet specified in the supplied material.
- Technical/emotional mode and any language selection.
- Webcam processing pipeline, update frequency and planned disable switch.
- Whether image frames are retained, how camera operation is indicated and how visitors are informed.
- Error behavior if the model or camera is unavailable.

This page distinguishes the interaction intent and builder-confirmed camera use from details awaiting the code.
