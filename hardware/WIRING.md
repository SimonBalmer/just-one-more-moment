![Just One More Moment](diagrams/project-banner.svg)

# My wiring and pin assignment

This is my final documented wiring layout for **Just One More Moment**, revision 04, **28 October 2026**.

**All numbered header pins are physical positions on the Pi's 40-pin header. GPIO labels use BCM numbering.** I group the main drawing by component so each connection runs directly between its two labelled terminals. The Pi block is a connection view, not the physical order of the pins. The separate **J8 physical pin locator** shows the actual 40-pin arrangement in a top view with USB ports on the right; pin 1 is at the lower left.

![My labelled Raspberry Pi 5 wiring](diagrams/wiring-overview.svg)

[SVG](diagrams/wiring-overview.svg) · [PNG](diagrams/wiring-overview.png) · [A3 landscape PDF](diagrams/wiring-overview.pdf) · [Drawing source](diagrams/README.md)

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
| NeoPixel supply + | **4** | Pi 5 V through D1 to strip +V |
| NeoPixel supply - | **34** | Pi GND directly to strip GND |
| SW01 signal | **15** | GPIO22 - Local AI / Cloud AI + Cam selector |
| SW01 return | **20** | GND |
| SW02 signal | **16** | GPIO23 - EN / DE selector |
| SW02 return | **25** | GND |
| Logitech C270 | USB | Visual context for Cloud AI + Cam mode |
| Display video/touch | DSI / FFC | Separate ribbon connection to a CAM/DISP port |

I have selected the unused **physical pin 34** as the NeoPixel ground in this documented layout. All GND pins share the same electrical ground inside the Pi.

## D1: my MIC 1N4001 diode

I use a **MIC 1N4001** in series with the NeoPixel **5 V supply lead**:

- **Physical pin 4 / 5 V** connects to the unbanded **anode (A)**.
- The **cathode (K), marked by the ring**, connects to the strip's **+V** input.
- **Physical pin 34 / GND** connects directly to strip **GND**.
- **Physical pin 19 / GPIO10** connects directly to **DIN**. The diode is not in the data lead.

### Why it helps

I use the [diode method described by Adafruit](https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring). The diode lowers the strip's supply voltage, which also lowers its input-HIGH threshold. This helps the strip recognize the Pi's **3.3 V** data signal. For example, a 0.7 V forward drop would reduce 5 V to about 4.3 V; a threshold of 70% of that supply would be about 3.0 V.

The actual forward drop depends on operating conditions. This is a supply-voltage workaround, not an active level shifter: GPIO10 still outputs 3.3 V. Adafruit also notes that the diode must carry the strip's total current and that reduced supply voltage can reduce brightness.

## My mode selectors

| Control | Label | GPIO / physical pin |
| --- | --- | --- |
| **SW01** | **Local AI / Cloud AI + Cam** | GPIO22 / P15, return P20 |
| **SW02** | **EN / DE** | GPIO23 / P16, return P25 |

These are software mode inputs. The webcam connects by USB; SW01 does not switch its USB supply or data wires.

## How I read the drawing

- Red leads carry the 5 V supply. The strip side of D1 is labelled +V because the diode reduces its voltage.
- Black leads are ground connections.
- Black leads with white dashes are GPIO signals.
- Each GPIO lead has its component terminal name at one end and its physical pin plus function at the Pi end. The leads do not cross.
- Wide grey cables are USB or DSI connections, labelled at both ends.
- I use the J8 locator to find the physical pins. Component shapes and port positions in the main connection view are grouped for clarity, rather than drawn to scale.
- I disconnect power before changing connections.

## References

- [Adafruit: NeoPixels on Raspberry Pi - wiring and diode method](https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring)
- [Raspberry Pi: GPIO header documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#gpio-and-the-40-pin-header)
- [Raspberry Pi: Touch Display 2 connection](https://www.raspberrypi.com/documentation/accessories/touch-display-2.html)
