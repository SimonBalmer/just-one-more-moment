![Just One More Moment](project-banner.svg)

# My wiring illustration

This is the final documented wiring layout for my installation, revision 03. I show a top view of the Pi with the GPIO header above the board and USB ports on the right. Every GPIO attachment is labelled by physical pin number, and the component terminals also identify the relevant BCM GPIO.

![My Raspberry Pi 5 wiring, including the MIC 1N4001 in the NeoPixel supply](wiring-overview.svg)

## Formats

- [SVG - vector illustration](wiring-overview.svg)
- [PNG - raster preview](wiring-overview.png)
- [PDF - one A3 landscape page](wiring-overview.pdf)

The component shapes and USB/DSI port positions are illustrative, not mechanical drawings. The physical GPIO pin numbers and terminal labels define my documented connections. I selected free **GND pin 34** for the NeoPixel return in this layout; it is electrically equivalent to the other GND pins.

## My controls and supply

- **SW01:** Local AI / Cloud AI + Cam, P15 / GPIO22 and P20 / GND.
- **SW02:** EN / DE, P16 / GPIO23 and P25 / GND.
- **NeoPixels:** 12 LEDs, DIN on P19 / GPIO10, supply from P4 / 5 V through D1, return on P34 / GND.
- **D1:** MIC **1N4001**, cathode ring toward strip +V.

I explain the [Adafruit diode method in my wiring documentation](../WIRING.md#why-it-helps).

## How I generate the files

I keep the [Python generator](generate_wiring.py) alongside the exports. It requires Python 3, `reportlab`, `fonttools`, a monospaced TrueType font and `pdftoppm` from Poppler. Its default font is DejaVu Sans Mono at the common Linux system path. I can set `JOMM_MONO_FONT` to another compatible font file.

```bash
python3 hardware/diagrams/generate_wiring.py
```

I use custom pixel lettering for the title and monospaced technical labels. The SVG lettering is outlined; the PDF retains embedded, selectable mono text. I render and visually inspect the PDF export to check labels, spacing and connection visibility.
