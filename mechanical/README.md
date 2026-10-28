# My enclosure files

**Simon Balmer · Just One More Moment · revision 2026-10-28**

I provide **13 numbered STL parts**, one of each for a complete enclosure, with a four-page illustrated assembly guide. The part numbers in the drawings match the filename prefixes. The guide is in German; the files use descriptive English names.

[Download the complete print pack](enclosure-print-pack.zip) · [Printable assembly guide (PDF)](assembly/assembly-guide.pdf) · [Individual STL files](stl/)

![Exploded enclosure overview](assembly/exploded-overview.png)

## What to print

Print each numbered part **once**. Left and right refer to the device seen from the front. The rear cable guide is split into an upper and a lower half; the original CAD names `PlugL` and `PlugR` refer to those two halves, not to left/right positions on the device.

| No. | Download | Part name in my drawings | Group | Qty. |
| --- | --- | --- | --- | --- |
| 01 | [01-base-housing.stl](stl/01-base-housing.stl) | Basisgehäuse | Basis | 1 |
| 02 | [02-base-bottom-cover.stl](stl/02-base-bottom-cover.stl) | Bodenabdeckung | Basis | 1 |
| 03 | [03-base-front-trim-left.stl](stl/03-base-front-trim-left.stl) | Front-Zierleiste links | Basis | 1 |
| 04 | [04-base-front-trim-right.stl](stl/04-base-front-trim-right.stl) | Front-Zierleiste rechts | Basis | 1 |
| 05 | [05-rear-cable-guide-upper.stl](stl/05-rear-cable-guide-upper.stl) | Kabeldurchführung oben | Basis | 1 |
| 06 | [06-rear-cable-guide-lower.stl](stl/06-rear-cable-guide-lower.stl) | Kabeldurchführung unten | Basis | 1 |
| 07 | [07-display-main-bracket.stl](stl/07-display-main-bracket.stl) | Display-Haupthalter | Display | 1 |
| 08 | [08-display-inner-bezel.stl](stl/08-display-inner-bezel.stl) | Display-Innenrahmen | Display | 1 |
| 09 | [09-display-outer-frame.stl](stl/09-display-outer-frame.stl) | Display-Aussenrahmen | Display | 1 |
| 10 | [10-display-rear-cover.stl](stl/10-display-rear-cover.stl) | Display-Rückschale | Display | 1 |
| 11 | [11-camera-lower-shell.stl](stl/11-camera-lower-shell.stl) | Kamera-Unterschale | Kamera | 1 |
| 12 | [12-camera-upper-shell.stl](stl/12-camera-upper-shell.stl) | Kamera-Oberschale | Kamera | 1 |
| 13 | [13-camera-lens-ring.stl](stl/13-camera-lens-ring.stl) | Kamera-Frontring | Kamera | 1 |

## Import into the slicer

- Use **millimetres** and **100% scale** for every part. STL does not encode a physical unit; these exported coordinates are interpreted as mm.
- The STL files retain their **CAD assembly coordinates**. Centre and place each part on the print bed individually, and choose its print orientation in the slicer. Their exported pose is not a recommended print orientation.
- As a scale check, part **01** has an axis-aligned envelope of **125 × 225 × 50 mm** in the CAD X/Y/Z axes. The assembled printed enclosure spans approximately **138 × 225 × 237.3 mm**.
- My materials list includes Bambu Lab PLA Matte Charcoal and Ivory White. The illustration colours identify parts; they do not prescribe filament colours.
- These meshes do not define a tested layer height, support arrangement, wall count, infill or shrink compensation. Choose the printing profile for the printer and material, inspect the sliced preview, and check mating surfaces after printing.

## What is excluded

I exclude the original `Assembled` file and the Pi, button and Touch Display 2 reference models from the print pack and the STL folder. The display is a purchased component even though its reference filename does not contain “Placeholder”. **K1** in the guide is a simplified display envelope, not a printable part.

The Pi, cooler, webcam, switches, button, wiring, screws and other purchased parts are listed in my [bill of materials](../hardware/BOM.md). The diagrams omit most purchased components to keep the enclosure relationships visible.

## Assembly drawings

The drawings use the original shared CAD coordinates. Only the illustration offsets separate the parts; the mesh geometry is not translated for printing. Dashed lines relate the exploded positions to their assembled locations. Explosion distances are illustrative and have no dimensional meaning.

1. [Complete exploded overview](assembly/exploded-overview.png): all 13 printed parts and display reference K1.
2. [Display detail](assembly/display-assembly.png): from rear to front, rear cover **10**, main bracket **07**, display **K1**, inner bezel **08**, outer frame **09**. Fit the Pi and route the display connections before closing the rear cover.
3. [Base detail](assembly/base-assembly.png): base housing **01**, bottom cover with rear closing wall **02**, front trims **03/04**, and the two rear cable-guide halves **05/06**. Route the rear cable before bringing the two guide halves together. Align the bottom cover's closing wall with the rear of the housing.
4. [Camera detail](assembly/camera-assembly.png): lower shell **11**, upper shell **12** and front ring **13** around the webcam position. Align the objective opening and keep the USB cable clear of the shell edges.

Mount the display housing on the base and align the lower camera shell with the top of the display housing as shown in the overview. Test-fit the parts and purchased components before closing the shells. The drawings document **geometric placement** inferred from the CAD geometry and my supplied assembled views. They do not specify an experimentally verified assembly sequence, screw sizes, insert types, adhesives or webcam disassembly procedure. Choose fixings against the actual mounting features and check clearance to the electronics.

For the electrical connections, use my [wiring documentation](../hardware/WIRING.md).

## Mesh checks and traceability

I checked the 13 distributed meshes for valid binary-STL record lengths, finite coordinates, positive signed volume, duplicate triangles and edge incidence. In each distributed STL every unique undirected edge belongs to exactly two triangles. These checks do not certify self-intersection freedom, tolerances or successful printing.

In the supplied display rear-cover export, two tiny pairs of coincident triangles had opposite winding and caused two edges with four incident faces. I removed **only those four redundant facet records** from `10-display-rear-cover.stl` (5,850 → 5,846 triangles). Every retained facet record and coordinate is unchanged. The [original rear-cover export](source/10-display-rear-cover-original.stl) is retained for traceability and is not in the print pack. The other 12 print files are byte-for-byte identical to their supplied originals.

My [parts manifest](parts-manifest.json) records the original filenames, distributed filenames, quantities, coordinate envelopes and SHA-256 hashes. It also records the original and cleaned hashes for part 10. The upload date identifies this file set; it is not a claim that a print test has been completed.

## Folder map

| Path | Contents |
| --- | --- |
| `stl/` | Exactly the 13 files to print, one of each |
| `enclosure-print-pack.zip` | The 13 STLs, parts manifest, print notes and illustrated PDF |
| `assembly/` | PDF, four PNG drawings and their generation script |
| `source/` | The unmodified rear-cover export, retained only for traceability |
| `parts-manifest.json` | Part mapping, counts, sizes, processing note and checksums |

To regenerate the illustrations, install `numpy`, `Pillow`, `reportlab` and `PyMuPDF`, then run `python mechanical/assembly/generate_assembly.py` from the repository root. The script uses the distributed meshes and a procedural, simplified envelope for the purchased display. It uses DejaVu Sans from `/usr/share/fonts/truetype/dejavu/` by default; adjust the two font paths for other systems.

**Design and documentation: Simon Balmer.**
