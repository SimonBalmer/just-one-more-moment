![Just One More Moment - Simon Balmer / PHKI / HSLU](hardware/diagrams/project-banner.svg)

**How does a machine's plea for more time change the way we care for it?**

With **Just One More Moment**, I explore how AI-generated emotional language changes empathy and responsibility. I am developing this physical installation for **PHKI - Philosophy, Art and AI**, HSLU, 2026.

## The experience

My device has a countdown, a screen and a button. Visitors can give it more time or let its remaining runtime run out. I want them to notice how a simple technical decision can start to feel like a moral choice.

I combine a Raspberry Pi, a custom 3D-printed enclosure and physical controls. My mode selector **SW01** is labelled **Local AI / Cloud AI + Cam**; **SW02** selects **EN / DE**. A USB webcam provides visual context in Cloud AI + Cam mode so the model can respond to visitors and their surroundings.

## My question

> How does an AI device's technical or emotional language affect visitors' empathy, sense of responsibility and willingness to extend its runtime?

I am also interested in the broader question of how we could recognize genuine consciousness or know whether an AI experiences anything. My installation invites reflection through people's reactions to a device that appears to have feelings.

Read more in my [project concept](docs/concept.md).

## My wiring

![My labelled Raspberry Pi 5 wiring overview](hardware/diagrams/wiring-overview.svg)

[Open the SVG](hardware/diagrams/wiring-overview.svg) · [PNG](hardware/diagrams/wiring-overview.png) · [Printable PDF](hardware/diagrams/wiring-overview.pdf) · [Connection table](hardware/WIRING.md)

I use exactly **12 NeoPixels**. DIN connects to **physical pin 19 / GPIO10**. Their supply runs from **P4 / 5 V** through a **MIC 1N4001** diode, with its **cathode band facing the strip**. I select the free **P34 / GND** as the strip return in this documented layout.

## My enclosure

![Exploded view of my 13 printed enclosure parts](mechanical/assembly/exploded-overview.png)

[Download all 13 print files](mechanical/enclosure-print-pack.zip) · [Illustrated assembly guide (PDF)](mechanical/assembly/assembly-guide.pdf) · [Individual STL files and print notes](mechanical/README.md)

Each number in the drawings matches a numbered STL filename. Red labels E1-E7 show purchased parts: display, Pi, webcam, illuminated button, two switches and the 12 NeoPixels. The guide includes display, base and camera details with the confirmed mounting, gluing, wiring and closing steps. Purchased-component placeholders and the complete assembly mesh are excluded from the print pack.

My [A4 sticker sheet (PDF)](docs/assets/just-one-more-moment-sticker-card-a4.pdf) is available for the enclosure. I explain the deliberate retro appearance and use of anthropomorphism in [my design rationale](docs/design.md#why-i-deliberately-use-anthropomorphism).

## Where I am now

**Physical prototype in development / documentation in progress**

I have documented my concept, parts and connections and added a wiring illustration. I have added 13 enclosure STL files, a downloadable print pack and a four-page enclosure assembly guide. My application code, editable CAD exports, project photographs and tested build settings are separate project deliverables.

| Area | My current status |
| --- | --- |
| Concept | Documented |
| Parts and pin assignment | Recorded; some exact part details remain open |
| Wiring illustration | Final revision 03 available as SVG, PNG and PDF |
| NeoPixel strip | 12 LEDs; P4 / 5 V through MIC 1N4001, P34 / GND, P19 / GPIO10 data |
| Webcam | Connected by USB for Cloud AI + Cam mode; SW01 selects AI mode |
| Software and model setup | I still need to upload my working files and exact configuration |
| Enclosure | 13 numbered STLs, print pack and four-page illustrated assembly guide with confirmed fixings available |
| Photographs and editable CAD | Separate from the STL file set |
| Complete reproduction guide | In progress |

## Build your own

I want to make this installation reproducible, including printable parts, electronics, software and assembly instructions. I am assembling the guide here:

1. [Parts list](hardware/BOM.md)
2. [Wiring and pin assignment](hardware/WIRING.md)
3. [Printable enclosure and illustrated assembly guide](mechanical/README.md)
4. [Build guide](docs/build-guide.md)
5. [Software setup](software/README.md)
6. [Operation and interaction](docs/operation.md)

## Repository contents

| Path | What I keep here |
| --- | --- |
| [`software/`](software/) | My application and local model setup - files to follow |
| [`hardware/`](hardware/) | Parts, connections and wiring graphics |
| [`mechanical/`](mechanical/) | 13 enclosure STLs, print pack, numbered assembly drawings and source mapping |
| [`docs/`](docs/) | Concept, build guide, operation and remaining work |
| [`media/`](media/) | Project photos and demo material - files to follow |

My [publication checklist](docs/TODO.md) tracks the remaining work. For documentation gaps or build questions, [open an issue](https://github.com/SimonBalmer/just-one-more-moment/issues).

## Credits and licensing

I am Simon Balmer. I design and build this installation, and I use AI to support coding and generate the device's live responses. I will add the exact software and model credits with my implementation.

I have not selected the project licenses yet. I will document licenses for my code, mechanical design and documentation, along with the terms of third-party software, models and assets.
