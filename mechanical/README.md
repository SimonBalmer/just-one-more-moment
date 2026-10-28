![Just One More Moment](../hardware/diagrams/project-banner.svg)

# My enclosure and assembly guide

**Simon Balmer · Revision 03 · 28 October 2026**

My **four-page guide** combines the exploded drawings with my mounting, gluing, wiring and closing steps. I use the same retro title and mono labels as my [wiring guide](../hardware/WIRING.md). All instructions are in simple English.

Printed parts use **white, grey and black**. Every purchased component **E1-E7 is red**, including its drawn shape. Red is a diagram code, not the component's real colour. Print parts **01-13 once each**; do not print the E-parts.

[Download the complete print pack](enclosure-print-pack.zip) · [Four-page assembly guide (PDF)](assembly/assembly-guide.pdf) · [Individual STL files](stl/)

![Exploded enclosure and purchased components](assembly/exploded-overview.png)

## Print one of each

The numbers match the drawings and the filename prefixes. Left and right refer to the device seen from the front. Grey shading shows depth on the light printed parts.

| No. | STL file | Part | Drawing colour | Qty. |
| --- | --- | --- | --- | --- |
| 01 | [01-base-housing.stl](stl/01-base-housing.stl) | Base housing | White / light grey | 1 |
| 02 | [02-base-bottom-cover.stl](stl/02-base-bottom-cover.stl) | Bottom and rear cover | White / light grey | 1 |
| 03 | [03-base-front-trim-left.stl](stl/03-base-front-trim-left.stl) | Front trim, left | Black | 1 |
| 04 | [04-base-front-trim-right.stl](stl/04-base-front-trim-right.stl) | Front trim, right | Black | 1 |
| 05 | [05-rear-cable-guide-upper.stl](stl/05-rear-cable-guide-upper.stl) | Cable guide, upper | Black | 1 |
| 06 | [06-rear-cable-guide-lower.stl](stl/06-rear-cable-guide-lower.stl) | Cable guide, lower | Black | 1 |
| 07 | [07-display-main-bracket.stl](stl/07-display-main-bracket.stl) | Display main bracket | White / light grey | 1 |
| 08 | [08-display-inner-bezel.stl](stl/08-display-inner-bezel.stl) | Display inner bezel | Black | 1 |
| 09 | [09-display-outer-frame.stl](stl/09-display-outer-frame.stl) | Display outer frame | White / light grey | 1 |
| 10 | [10-display-rear-cover.stl](stl/10-display-rear-cover.stl) | Display rear cover | White / light grey | 1 |
| 11 | [11-camera-lower-shell.stl](stl/11-camera-lower-shell.stl) | Camera lower shell | White / light grey | 1 |
| 12 | [12-camera-upper-shell.stl](stl/12-camera-upper-shell.stl) | Camera upper shell | White / light grey | 1 |
| 13 | [13-camera-lens-ring.stl](stl/13-camera-lens-ring.stl) | Camera front ring | Black | 1 |

## Purchased parts

These are simple position references, not printable models.

| Label | Purchased part | Position |
| --- | --- | --- |
| **E1** | Raspberry Pi Touch Display 2 | In bracket 07, behind the clipped-together frames 08/09 |
| **E2** | Raspberry Pi 5 with cooler | Screwed to the back of E1, inside rear cover 10 |
| **E3** | Logitech C270 camera | Front half of shell 11, reaching only to the middle divider; lens faces ring 13 |
| **E4** | Illuminated 33 mm arcade button, including its LED | Inserted from the front into the large base opening |
| **E5** | SW01: Local AI / Cloud AI + Cam | Inserted from inside into the left small front hole, secured with its nut |
| **E6** | SW02: EN / DE | Inserted from inside into the right small front hole, secured with its nut |
| **E7** | WS2812B NeoPixels, **12 LEDs** | Self-adhesive backing fixed under the base ceiling; light shines through the side vents |

The button LED belongs to E4. E7 is the separate 12-LED strip. The display and Pi envelopes follow the supplied CAD references; the camera and controls are simplified shapes. LED spacing is schematic. Match SW01/SW02 to my [wiring guide](../hardware/WIRING.md).

## Assembly order

**Prepare the camera and base controls before the final Pi connections. Finish every Pi connection before closing display cover 10. Close base cover 02 last.** This keeps the Pi accessible until every lead is connected.

The guide has four pages:

1. [Exploded overview](assembly/exploded-overview.png): cable-guide halves **05/06 are at the far left, outside rear plate 02**.
2. [Display and Pi](assembly/display-assembly.png): mounting screws, clipped frames, gluing 10 to 01, cable routing and three-screw display closure.
3. [Base and front controls](assembly/base-assembly.png): glued trims, front-inserted button, rear-inserted switches, LEDs, cable management and final closure of 02.
4. [Camera](assembly/camera-assembly.png): shallow camera in 11, rear cable exit, shell fit and glued front ring 13.

The exploded distances are illustrative. The mounting, wiring and fixing steps follow below.

### Display and Pi — page 02

**Mount the pi on the display.** Screw Pi E2 to display E1 using the supplied display screws and its threaded mounting points. Connect the display power and data cables to the Pi now. Follow the official Touch Display 2 instructions.

**Build the front screen unit.** Use the display screws to attach the display/Pi unit to bracket 07 at the four outer threaded mounting points. Slide 08 and 09 into each other, then click this pair onto 07. The front screen unit is complete.

**Glue the rear cover to the base.** Before wiring the device, glue rear cover 10 to base housing 01. I use UHU Kraftkleber (strong adhesive). Let the bond set as directed on the adhesive packaging.

**Connect and route the cables.** Prepare the camera and base controls as shown on pages 03-04. Connect all leads to the Pi using hardware/WIRING.md. Route the jumper leads, camera USB cable and Pi power cable through the lower opening in 10 into the base.

**Close the display housing.** Fit the front screen unit onto 10. Use its three screw guides and three 2.9 x 9.5 mm sheet-metal or wood screws, or similar screws that fit. Complete all Pi connections before this step; no further access is needed.

Display power and data connections: [official Raspberry Pi Touch Display 2 instructions](https://www.raspberrypi.com/documentation/accessories/touch-display-2.html).

### Base, controls and cables — page 03

**Prepare the control leads.** Prepare and solder the jumper leads in advance using hardware/WIRING.md. Insulate the solder joints as shown in the wiring guide.

**Glue trims and fit the controls.** Glue trims 03 and 04 into their guides. Insert the large arcade button E4 from the front. Insert switches E5 and E6 from inside the housing, then secure them with their mounting nuts.

**Place and wire the leds.** Use the self-adhesive backing to place the 12 NeoPixels E7 under the inside ceiling of 01. Spread them so their light shines through the side vents. Wire E4-E7 to the Pi using the wiring guide before closing the display housing.

**Store and route the cables.** With the wiring complete, loosely coil the spare camera USB cable inside the base. Lead the Pi power cable out through rear plate 02. Fit cable-guide halves 05 and 06 from the outside of 02 around the cable and secure it.

**Close the base.** Fit bottom/rear cover 02 to housing 01 and fasten it with two suitable screws or bolts and two matching nuts. Choose pairs that fit the printed fixing holes.

The cable guide is external: fit **05 above 06 on the outside of 02**, around the outgoing Pi power cable. The original CAD name `PlugL` maps to upper half 05; `PlugR` maps to lower half 06.

### Camera — page 04

**Fit and secure the camera.** Place camera E3 in lower shell 11, with the lens at the front opening. The shallow body reaches only to the middle divider in 11. Secure it with glue or tape, and lead its USB cable out through the rear.

**Click the two shells together.** Push 11 and 12 together. Slight pressure from the left and right sides of upper shell 12 makes it easier to fit.

**Glue the front ring.** Glue front ring 13 into place to join and finish the camera housing.

Part **12** is the camera upper shell. The separate front ring is **13**. Mount the camera housing at the top of the display housing as shown in the overview. Route its USB lead to the Pi and keep the spare length in the base.

## Fixings and adhesive

| Item | Quantity / use |
| --- | --- |
| Display kit screws | Pi to display, then display/Pi unit to the four outer points on 07 |
| 2.9 × 9.5 mm sheet-metal or wood screws, or a similar fitting type | **3** for closing the screen unit onto rear cover 10 |
| Suitable screws or bolts with matching nuts | **2 screws/bolts + 2 nuts** for 02 to 01; select a size that fits the printed holes |
| UHU Kraftkleber (strong adhesive) | I use it to glue 10 to 01 before wiring |
| Adhesive for trims and ring | Glue 03/04 into their guides, and glue ring 13 to finish the camera housing |
| Glue or tape | Secure the camera in shell 11 |

## Slicer import and file checks

- Use **mm** and **100% scale** for every STL. Centre, orient and place each part on the bed on its own; the exports keep the CAD assembly coordinates.
- Scale check for **01**: CAD X/Y/Z envelope **125 × 225 × 50 mm**. The assembled printed enclosure is about **138 × 225 × 237.3 mm**.
- My filament list includes Bambu Lab PLA Matte Charcoal and Ivory White. Choose the printing profile, supports and orientation for the printer and material.
- The full assembly model and original Pi, display and button placeholder STLs are excluded from the print folder and ZIP.
- This revision changes the illustrations and instructions. All **13 distributed STL files are unchanged** from revision 02.

I checked the distributed meshes for valid binary STL length, finite coordinates, positive signed volume, no duplicate triangles, and two faces at every unique edge. These checks do not replace checking the sliced preview and mating surfaces.

In the first print-file release I removed four opposite duplicate facet records from part 10 (5,850 to 5,846 triangles), leaving every retained coordinate unchanged. The [original rear-cover export](source/10-display-rear-cover-original.stl) remains outside the print pack. The other 12 source files are unchanged.

My [parts manifest](parts-manifest.json) records part names, original source filenames, quantities, sizes, hashes, purchased references and the confirmed assembly steps. Original source filenames stay as supplied for traceability.

## Files and drawing source

| Path | Contents |
| --- | --- |
| `stl/` | Exactly 13 files to print, one of each |
| `enclosure-print-pack.zip` | STLs, manifest, print/assembly notes and the four-page PDF |
| `assembly/` | PDF, four PNG pages and their generator |
| `source/` | Original part-10 export for traceability |
| `parts-manifest.json` | Part mapping, file checks, purchased references and assembly steps |

To regenerate the drawings, install `numpy`, `Pillow`, `reportlab` and `PyMuPDF`, then run:

```bash
python3 mechanical/assembly/generate_assembly.py
```

The default label font is DejaVu Sans Mono. Set `JOMM_MONO_FONT` and `JOMM_MONO_BOLD_FONT` to compatible font files on another system. The pixel title matches my wiring illustration.

**Design and documentation: Simon Balmer.**
