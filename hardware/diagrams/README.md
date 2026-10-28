![Just One More Moment](project-banner.svg)

# My wiring illustration

I use a labelled breadboard-style illustration to document the connections in my prototype. The drawing follows my pin assignment and uses a top view of the Pi with the GPIO header above the board and the USB ports on the right.

![My Raspberry Pi 5 wiring, including the diode in the NeoPixel 5 V lead](wiring-overview.svg)

## Formats

- [SVG - vector illustration](wiring-overview.svg)
- [PNG - raster preview](wiring-overview.png)
- [PDF - one A3 landscape page](wiring-overview.pdf)

The component shapes and USB/DSI port positions are illustrative, not mechanical drawings. The physical GPIO pin numbers and the connection labels are the reference for my wiring. The HTML/SVG text paths keep the mono typeface intact without requiring a font installation to view the drawing.

## How I generate the files

I keep the [Python generator](generate_wiring.py) alongside the exports so I can update the drawing when my setup changes.

The generator requires Python 3, `reportlab`, `fonttools`, a monospaced TrueType font and the `pdftoppm` command from Poppler. Its default font is DejaVu Sans Mono at the common Linux system path. I can set `JOMM_MONO_FONT` to another compatible font file if needed.

```bash
python3 hardware/diagrams/generate_wiring.py
```

I use custom pixel lettering for the title and monospaced labels for technical details. The text in the SVG exports is outlined; the PDF retains embedded, selectable mono text.

## Details I still need to record

- The exact NeoPixel 5 V and GND header pins.
- The diode model. Its position is confirmed: in series with the 5 V supply, cathode band toward the strip.
- The display's actual CAM/DISP socket.
- The final function and position mapping of both toggle switches.
