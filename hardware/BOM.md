![Just One More Moment](diagrams/project-banner.svg)

# My parts list

These are the components I have collected for my prototype. I keep the [Galaxus shopping list - PHKI P1 Materials](https://www.galaxus.ch/de/shopping-list/OdSpfGWFvwsEgOHc0J7WXnqzFrZIh4Vq) as a purchasing reference. I have added the two toggle switches there; I still need to copy their exact model details into this list.

## Main components

| Component | Quantity / use | My notes |
| --- | --- | --- |
| Raspberry Pi 5, 8 GB | 1 | Main computer |
| Raspberry Pi Official fan/heat sink for 5 | 1 cooling assembly listed | I still need to confirm the exact installed cooler |
| Raspberry Pi Official Touch Display 2 | 1 | I still need to record the exact variant and mounting details |
| Logitech C270, 0.90 Mpx | 1 | USB webcam for visual context |
| SanDisk Ultra microSDXC, 128 GB, U1, UHS-I, SD adapter | 1 card listed | I still need to record my installed OS/image |
| Raspberry Pi Official 5 power supply, 27 W USB-C | 1 supply listed | Power for my Pi |

## Controls and lighting

| Component | Quantity / use | My notes |
| --- | --- | --- |
| Purecrea illuminated arcade button, 33 mm, white | 1 | Separate switch and LED connections |
| Toggle switches | 2 | SW01: Local AI / Cloud AI + Cam; SW02: EN / DE. Exact part model and contacts still to document |
| Purecrea WS2812B NeoPixel strip | **12 LEDs** | I use P19 / GPIO10 for DIN, P4 / 5 V through D1, and P34 / GND in my documented layout |
| MIC 1N4001 diode | 1 in the NeoPixel 5 V lead | Anode to P4 / 5 V; cathode band toward strip +V |
| Purecrea jumper wires | As used | I still need to record connectors, lengths and quantity |

I have counted **12 LEDs on my actual strip**. I use that count for the build and software configuration, regardless of the length in the shopping-list product wording.

## Enclosure fixings and adhesive

I use these with my [four-page assembly guide](../mechanical/assembly/assembly-guide.pdf):

| Item | Quantity / use |
| --- | --- |
| Screws supplied with the Touch Display 2 | Mount the Pi on the display, then the display/Pi unit on the four outer points of bracket 07 |
| 2.9 x 9.5 mm sheet-metal or wood screws, or a similar fitting type | **3** to close the screen unit onto rear cover 10 |
| Suitable screws/bolts with matching nuts | **2 screws/bolts + 2 nuts** to close bottom/rear cover 02 onto base 01; size to fit the printed holes |
| UHU Kraftkleber (strong adhesive) | Glue 10 to 01 before wiring |
| Adhesive | Glue trims 03/04 into their guides and front ring 13 into place |
| Glue or tape | Secure the camera in shell 11 |
| NeoPixel self-adhesive backing | Fix the **12 LEDs** under the inside ceiling of the base so light exits the side vents |

## Printed parts and assembly materials

My enclosure uses [13 numbered print files, one of each](../mechanical/README.md). The [print pack](../mechanical/enclosure-print-pack.zip) includes the matching four-page illustrated enclosure guide. Purchased-component placeholders are excluded.

| Material | My listed product | What I still need to add |
| --- | --- | --- |
| Dark filament | Bambu Lab PLA Matte - Charcoal, 1.75 mm, 1000 g spool | Black trims, cable guides, inner bezel and camera ring; material use depends on slicing |
| Light filament | Bambu Lab PLA Matte - Ivory White, 1.75 mm, 1000 g spool | Light housings, covers, outer frame and bracket; material use depends on slicing |
| Fixings and connectors | My actual assembly materials | Enclosure fixings are listed above; record the remaining connector and insulation quantities |

A spool's 1000 g weight is its purchase size, not the material needed for one enclosure. I will calculate a useful build cost once I have recorded the quantities and actual consumption.

## What I still need to record

- Exact toggle switch models.
- Display signal cable type, length and actual CAM/DISP socket.
- Remaining connector quantities, tools and print settings.
