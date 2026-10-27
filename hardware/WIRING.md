# Wiring and pin assignment

This document records the builder's pin assignment and working-setup report from 27 October 2026. It will be expanded into a complete circuit diagram when assembly photographs and the application code are available.

**Header pin numbers below are physical positions on the Raspberry Pi's 40-pin header. GPIO labels use BCM numbering.**

## Connections

| Component / connection | Physical header pin(s) | Connection |
| --- | --- | --- |
| Touch Display 2 power | 2, 6 | 5 V / GND |
| Arcade button contacts | 9, 11 | COM to GND / NO to GPIO17 |
| Arcade button LED | 13, 14 | LED+ to GPIO27 / LED− to GND |
| NeoPixel data, **12 LEDs** | 19 | GPIO10 to the strip's DIN; exact diode arrangement to document |
| NeoPixel supply | Exact header positions to record | Connected to Pi 5 V and GND; builder confirms this setup works |
| Toggle switch 1 | 15, 20 | GPIO22 / GND |
| Toggle switch 2 | 16, 25 | GPIO23 / GND |
| Logitech C270 webcam | USB | Connected to a Pi USB port |

## NeoPixel setup

The installed strip contains exactly **12 LEDs**. Simon confirms that the strip works with data on physical pin 19 (GPIO10), supply from the Pi's 5 V/GND pins, and a diode in the setup.

The description does not yet establish the diode's exact location, type or orientation. No complete diode circuit is inferred here. The exact 5 V/GND header positions also remain to be recorded from the device. These are documentation details still to capture from the working build.

## Remaining circuit details

- Photograph the actual connections and add a diagram matching the finished device.
- Record display signal wiring separately: pins 2 and 6 describe power only.
- Map each toggle switch to its actual software function and document contact selection, active state and pull configuration.
- Record the arcade LED rating and actual drive arrangement.
- Add the exact NeoPixel circuit, diode details, supply pins and any other fitted components.
- Document the LED driver, required interfaces and Pi 5 setup from the code.

Disconnect power before changing wiring. Use both the physical pin number and BCM label when checking the device against the software.
