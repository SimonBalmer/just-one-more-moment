![Just One More Moment - Simon Balmer / PHKI / HSLU](hardware/diagrams/project-banner.svg)

**How does a machine's plea for more time change the way we care for it?**

With **Just One More Moment**, I explore how AI-generated emotional language changes empathy and responsibility. I am developing this physical installation for **PHKI - Philosophy, Art and AI**, HSLU, 2026.

## The experience

My device has a countdown, a screen and a button. Visitors can give it more time or let its remaining runtime run out. I want them to notice how a simple technical decision can start to feel like a moral choice.

I combine a Raspberry Pi, local AI, a custom 3D-printed enclosure and physical controls. A USB webcam gives the model visual context so it can respond to visitors and their surroundings. I plan to make this input optional through a physical switch.

## My question

> How does an AI device's technical or emotional language affect visitors' empathy, sense of responsibility and willingness to extend its runtime?

I am also interested in the broader question of how we could recognize genuine consciousness or know whether an AI experiences anything. My installation invites reflection through people's reactions to a device that appears to have feelings.

Read more in my [project concept](docs/concept.md).

## My wiring

![My labelled Raspberry Pi 5 wiring overview](hardware/diagrams/wiring-overview.svg)

[Open the SVG](hardware/diagrams/wiring-overview.svg) · [PNG](hardware/diagrams/wiring-overview.png) · [Printable PDF](hardware/diagrams/wiring-overview.pdf) · [Connection table](hardware/WIRING.md)

I use exactly **12 NeoPixels**. Their data input connects to **physical pin 19 / GPIO10**. I place the diode in the **5 V supply lead**, with its **cathode band facing the LED strip**. I still need to record the exact NeoPixel supply pins and diode model.

## Where I am now

**Physical prototype in development / documentation in progress**

I have documented my concept, parts and connections and added a wiring illustration. I still need to upload my application code, CAD/STL files and project photographs, then complete the build instructions.

| Area | My current status |
| --- | --- |
| Concept | Documented |
| Parts and pin assignment | Recorded; some exact part details remain open |
| Wiring illustration | SVG, PNG and PDF available; open details labelled |
| NeoPixel strip | 12 LEDs, working from my Pi's 5 V/GND supply with a diode in the 5 V lead |
| Webcam | Connected by USB and used for visual context; physical disable switch planned |
| Software and model setup | I still need to upload my working files and exact configuration |
| Enclosure and photographs | I still need to add my files |
| Complete reproduction guide | In progress |

## Build your own

I want to make this installation reproducible, including printable parts, electronics, software and assembly instructions. I am assembling the guide here:

1. [Parts list](hardware/BOM.md)
2. [Wiring and pin assignment](hardware/WIRING.md)
3. [Build guide](docs/build-guide.md)
4. [Software setup](software/README.md)
5. [Operation and interaction](docs/operation.md)

## Repository contents

| Path | What I keep here |
| --- | --- |
| [`software/`](software/) | My application and local model setup - files to follow |
| [`hardware/`](hardware/) | Parts, connections and wiring graphics |
| [`mechanical/`](mechanical/) | Printable and editable enclosure files - files to follow |
| [`docs/`](docs/) | Concept, build guide, operation and remaining work |
| [`media/`](media/) | Project photos and demo material - files to follow |

My [publication checklist](docs/TODO.md) tracks the remaining work. For documentation gaps or build questions, [open an issue](https://github.com/SimonBalmer/just-one-more-moment/issues).

## Credits and licensing

I am Simon Balmer. I design and build this installation, and I use AI to support coding and generate the device's live responses. I will add the exact software and model credits with my implementation.

I have not selected the project licenses yet. I will document licenses for my code, mechanical design and documentation, along with the terms of third-party software, models and assets.
