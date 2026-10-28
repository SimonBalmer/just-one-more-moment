![Just One More Moment](../hardware/diagrams/project-banner.svg)

# My enclosure and assembly guide

**Simon Balmer · Revision 02 · 28 October 2026**

I use the same retro style as my [wiring guide](../hardware/WIRING.md): pixel titles, mono labels, and black, white, red and grey. All guide pages and part names are in simple English.

My enclosure has **13 printed parts**, one of each. My **six-page assembly guide** shows how they fit together and where the purchased parts sit. A black circle identifies a printed part. A red E-label identifies a purchased part.

[Download the complete print pack](enclosure-print-pack.zip) · [Six-page assembly guide (PDF)](assembly/assembly-guide.pdf) · [Individual STL files](stl/)

![Exploded enclosure with purchased components](assembly/exploded-overview.png)

## Print one of each

The numbers below match the drawings and the filename prefixes. Left and right refer to the device seen from the front.

| No. | STL file | Part | Qty. |
| --- | --- | --- | --- |
| 01 | [01-base-housing.stl](stl/01-base-housing.stl) | Base housing | 1 |
| 02 | [02-base-bottom-cover.stl](stl/02-base-bottom-cover.stl) | Bottom and rear cover | 1 |
| 03 | [03-base-front-trim-left.stl](stl/03-base-front-trim-left.stl) | Front trim, left | 1 |
| 04 | [04-base-front-trim-right.stl](stl/04-base-front-trim-right.stl) | Front trim, right | 1 |
| 05 | [05-rear-cable-guide-upper.stl](stl/05-rear-cable-guide-upper.stl) | Cable guide, upper | 1 |
| 06 | [06-rear-cable-guide-lower.stl](stl/06-rear-cable-guide-lower.stl) | Cable guide, lower | 1 |
| 07 | [07-display-main-bracket.stl](stl/07-display-main-bracket.stl) | Display main bracket | 1 |
| 08 | [08-display-inner-bezel.stl](stl/08-display-inner-bezel.stl) | Display inner bezel | 1 |
| 09 | [09-display-outer-frame.stl](stl/09-display-outer-frame.stl) | Display outer frame | 1 |
| 10 | [10-display-rear-cover.stl](stl/10-display-rear-cover.stl) | Display rear cover | 1 |
| 11 | [11-camera-lower-shell.stl](stl/11-camera-lower-shell.stl) | Camera lower shell | 1 |
| 12 | [12-camera-upper-shell.stl](stl/12-camera-upper-shell.stl) | Camera upper shell | 1 |
| 13 | [13-camera-lens-ring.stl](stl/13-camera-lens-ring.stl) | Camera front ring | 1 |

## Purchased parts in the guide

These shapes show position and orientation. **Do not print them.** They are not included as STL files in the print pack.

| Label | Purchased part | Position |
| --- | --- | --- |
| **E1** | Raspberry Pi Touch Display 2 | In front of main bracket 07, behind bezels 08/09; screen facing forwards |
| **E2** | Raspberry Pi 5 with cooler | Behind the display, inside rear cover 10 |
| **E3** | Logitech C270 webcam | Between camera shells 11/12; lens facing ring 13 |
| **E4** | Illuminated 33 mm arcade button, including its LED | Large hole in the base front |
| **E5** | SW01: Local AI / Cloud AI + Cam switch | Left small front hole in this guide |
| **E6** | SW02: EN / DE switch | Right small front hole in this guide |
| **E7** | WS2812B NeoPixels, **12 LEDs** | Fixed to the inside ceiling of the base; light shines through the side ventilation slots |

The button LED is part of E4. E7 is the separate 12-LED strip. I match the E5/E6 labels to SW01/SW02 in my [wiring guide](../hardware/WIRING.md). The exact switch model does not affect the simplified shapes in these drawings.

I use the supplied CAD envelopes for the display and Pi. The Pi chips and ports are symbols. The webcam body, switches and rear button body are rough shapes; their openings set their positions. I confirmed the NeoPixels are inside the base, under its ceiling. Their spacing in the drawing is schematic. The reference shapes explain the build; they do not replace measured models for checking part fit.

## Assembly pages

1. [Exploded enclosure](assembly/exploded-overview.png): all 13 printed parts and purchased references E1-E7.
2. [Display and Pi](assembly/display-assembly.png): cover 10, Pi E2, bracket 07, display E1, inner bezel 08 and outer frame 09.
3. [Base and front controls](assembly/base-assembly.png): housing 01, bottom/rear cover 02, trims 03/04, cable-guide halves 05/06 and front controls E4-E6.
4. [Camera](assembly/camera-assembly.png): webcam E3 between lower shell 11 and upper shell 12, with front ring 13.
5. [Installed display and camera positions](assembly/electronics-placement.png): covers hidden, parts in their original assembly positions.
6. [Button, switches and LEDs](assembly/controls-and-leds.png): front controls in place and a cutaway from below showing all 12 NeoPixels under the base ceiling. Cover 02 and the lower base lip are hidden in this illustration.

The drawings keep the original CAD assembly positions. Only the exploded views move the parts apart. Dashed lines link their positions; explosion distances are not dimensions. Grey fills and red accents identify parts, not filament colours.

Fit the purchased components and route cables before closing the shells. Put the cable between guide halves 05 and 06 before fitting them into the rear outlet. The original CAD name `PlugL` is the upper half 05; `PlugR` is the lower half 06. Mount the display housing on the base and align the camera housing with the top of the display housing, as shown in the overview.

The meshes define the printed shapes and their positions. Screw sizes, insert types, adhesives, camera changes and a tested printer profile are not defined by these files. Select fixings to match the real parts and check the sliced preview and mating surfaces before final assembly. Use my [wiring guide](../hardware/WIRING.md) for the electrical connections.

## Slicer import

- Use **mm** and **100% scale** for every part. STL does not store a physical unit; these coordinates are interpreted as mm.
- The exports keep their CAD assembly coordinates. Centre, orient and place each part on the bed on its own. The exported pose is not a chosen print orientation.
- Scale check: part **01** has a CAD X/Y/Z envelope of **125 × 225 × 50 mm**. The assembled printed enclosure is about **138 × 225 × 237.3 mm**.
- My materials list includes Bambu Lab PLA Matte Charcoal and Ivory White. Choose settings and supports for the printer and material.
- The full assembly model and the Pi, display and button placeholder STLs are excluded from the print folder and ZIP.

## File checks and source mapping

I checked all 13 distributed meshes: valid binary STL length, finite coordinates, positive signed volume, no duplicate triangles, and two faces at every unique edge. These checks do not prove a successful print or rule out every possible geometry issue.

Part 10 had two pairs of opposite duplicate triangles in the supplied export. I removed only those four extra facet records (5,850 to 5,846 triangles). Every retained facet and coordinate is unchanged. I keep the [original rear-cover export](source/10-display-rear-cover-original.stl) outside the print pack. The other 12 files are unchanged.

My [parts manifest](parts-manifest.json) records English part names, original source filenames, counts, sizes, hashes and the seven purchased references. Original source filenames stay as supplied so the mapping is traceable.

## Files and drawing source

| Path | Contents |
| --- | --- |
| `stl/` | Exactly 13 files to print, one of each |
| `enclosure-print-pack.zip` | STLs, part manifest, print notes and the six-page PDF |
| `assembly/` | PDF, six PNG pages and their generator |
| `source/` | Original part-10 export for traceability |
| `parts-manifest.json` | Part mapping, file checks and purchased-reference notes |

To regenerate the drawings, install `numpy`, `Pillow`, `reportlab` and `PyMuPDF`, then run:

```bash
python3 mechanical/assembly/generate_assembly.py
```

The default label font is DejaVu Sans Mono. I can set `JOMM_MONO_FONT` and `JOMM_MONO_BOLD_FONT` to compatible font files on another system. The pixel title matches my wiring illustration.

**Design and documentation: Simon Balmer.**
