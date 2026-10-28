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

## Printed parts and assembly materials

| Material | My listed product | What I still need to add |
| --- | --- | --- |
| Dark filament | Bambu Lab PLA Matte - Charcoal, 1.75 mm, 1000 g spool | Part/color mapping and grams used |
| Light filament | Bambu Lab PLA Matte - Ivory White, 1.75 mm, 1000 g spool | Part/color mapping and grams used |
| Fixings and connectors | My actual assembly materials | Screws, inserts, brackets, insulation and any adhesives used |

A spool's 1000 g weight is its purchase size, not the material needed for one enclosure. I will calculate a useful build cost once I have recorded the quantities and actual consumption.

## What I still need to record

- Exact toggle switch models.
- Display signal cable type, length and actual CAM/DISP socket.
- Fasteners, connectors, tools and print settings.
