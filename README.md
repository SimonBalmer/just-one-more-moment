# Just One More Moment

**How does a machine's plea for more time change the way we care for it?**

An interactive installation exploring AI-generated emotional language, empathy and responsibility.

Created by **Simon Balmer** for **PHKI — Philosophy, Art and AI**, HSLU, 2026.

## The experience

A small physical device has a countdown, a screen and a button. Visitors can give it more time or let its remaining runtime run out. Its generated language can make that simple technical decision feel like a moral choice.

The installation combines a Raspberry Pi, local AI, a custom 3D-printed enclosure and physical controls. A USB webcam gives the model visual context, allowing it to respond to visitors and their surroundings. Making this visual input optional through a physical switch is planned.

## The question

> How does an AI device's technical or emotional language affect visitors' empathy, sense of responsibility and willingness to extend its runtime?

The broader philosophical question is how we could recognize genuine consciousness or know whether an AI experiences anything. The installation invites reflection on that question through people's reactions to a device that appears to have feelings.

Read more in the [project concept](docs/concept.md).

## Project status

**Physical prototype in development · Documentation being assembled**

The hardware notes record the builder's working setup. This repository currently contains the documentation foundation; the application code, CAD/STL files, project photographs and complete build instructions are still to be added.

| Area | Current status |
| --- | --- |
| Project concept | Documented |
| Parts and pin assignment | Recorded; exact part details and circuit diagram still to complete |
| NeoPixel strip | 12 LEDs; builder confirms operation from the Pi's 5 V/GND supply with GPIO10 data and a diode in the setup |
| USB webcam | Connected and used for visual context; switch-controlled disabling planned |
| Application and model setup | Working files and exact configuration pending upload |
| Enclosure files and assembly photos | Pending upload |
| Complete reproduction guide | In progress |

## Build your own

The goal is to make the installation reproducible, including printable parts, electronics, software and assembly instructions. Start with these documents; the guide clearly marks what still needs to be supplied.

1. [Parts list](hardware/BOM.md)
2. [Wiring and pin assignment](hardware/WIRING.md)
3. [Build guide](docs/build-guide.md)
4. [Software setup](software/README.md)
5. [Operation and interaction](docs/operation.md)

## Repository contents

| Path | Contents |
| --- | --- |
| [`software/`](software/) | Application and local model setup — files to follow |
| [`hardware/`](hardware/) | Parts list and electrical connections |
| [`mechanical/`](mechanical/) | Printable and editable enclosure files — files to follow |
| [`docs/`](docs/) | Concept, build guide, operation and remaining work |
| [`media/`](media/) | Project photos and demo material — files to follow |

## Next steps

See the [publication checklist](docs/TODO.md) for the remaining inputs and verification work. For documentation gaps or build questions, [open an issue](https://github.com/SimonBalmer/just-one-more-moment/issues).

## Credits and licensing

Project by Simon Balmer. AI is used to support coding and to generate the device's responses; detailed software/model credits will be added with the implementation.

License selection for the original code, mechanical design and documentation is pending. Third-party software, models and assets will be documented with their respective licenses. No project license is included yet.
