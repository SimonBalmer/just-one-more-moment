![Just One More Moment](diagrams/project-banner.svg)

# My wiring and pin assignment

This is the connection layout for my prototype, updated on **28 October 2026**.

**All numbered header pins are physical positions on the Pi's 40-pin header. GPIO labels use BCM numbering.** In the drawing I show a top view with the GPIO header above the board and USB ports on the right. Pin 1 is the lower-left pin of that header.

![My labelled Raspberry Pi 5 wiring](diagrams/wiring-overview.svg)

[SVG](diagrams/wiring-overview.svg) · [PNG](diagrams/wiring-overview.png) · [A3 landscape PDF](diagrams/wiring-overview.pdf) · [Drawing source and notes](diagrams/README.md)

## My connections

| Component / lead | Physical header pin | Function |
| --- | --- | --- |
| Touch Display 2 power + | **2** | 5 V |
| Touch Display 2 power - | **6** | GND |
| Arcade button COM | **9** | GND |
| Arcade button NO | **11** | GPIO17 |
| Button LED+ | **13** | GPIO27 |
| Button LED- | **14** | GND |
| NeoPixel DIN, **12 LEDs** | **19** | GPIO10 directly to DIN |
| NeoPixel supply + | **Still to record** | Pi 5 V through the diode to strip +V |
| NeoPixel supply - | **Still to record** | Pi GND directly to strip GND; common ground |
| Toggle switch 1 signal | **15** | GPIO22 |
| Toggle switch 1 return | **20** | GND |
| Toggle switch 2 signal | **16** | GPIO23 |
| Toggle switch 2 return | **25** | GND |
| Logitech C270 | USB | Visual context for the model |
| Display video/touch | DSI / FFC | Separate ribbon cable; I still need to record the actual CAM/DISP socket |

## My NeoPixel supply

My strip contains exactly **12 LEDs**. It works with data on **physical pin 19 / GPIO10** and power from my Pi's 5 V/GND header connections.

I put the diode **in series with the 5 V lead**. Its **ring / cathode (K) faces the LED strip**. The unbanded anode (A) faces the Pi's 5 V supply. Ground connects directly to the strip's GND. The diode is **not in the data lead**.

I still need to record the diode model and the exact physical pins I use for NeoPixel 5 V and GND. The drawing labels those connections as **PIN TBD** rather than assigning unconfirmed pin numbers.

## How I read the drawing

- Red leads carry the 5 V supply. The strip side of the diode is labelled +V because its voltage is reduced by the diode's forward drop.
- Black leads are ground connections.
- Black leads with white dashes are GPIO signals.
- Line crossings are not electrical junctions.
- Component shapes and USB/DSI port positions are illustrative. I use the numbered header pins and connection labels as the wiring reference.
- I disconnect power before changing connections.

## Details I am still completing

- My exact NeoPixel supply pins and diode model.
- A photograph of the wiring in the finished enclosure.
- The display's actual CAM/DISP socket and cable details.
- Each switch's function, contact selection, position mapping and software pull configuration.
- The button LED rating and actual drive arrangement.
- The LED driver and required Pi 5 interfaces from my code.

## Technical references

I use Raspberry Pi's [GPIO documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#gpio-and-the-40-pin-header) to check physical/BCM numbering, and its [Touch Display 2 documentation](https://www.raspberrypi.com/documentation/accessories/touch-display-2.html) for the separate display data connection. My table records my own project connections.
