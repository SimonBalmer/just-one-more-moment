# Just One More Moment

![Just One More Moment — an ivory retro device with a red ASCII cloud](media/project-cover.png)

*AI-generated cover illustration based on my prototype. [Real project photos](docs/product-design.md#the-finished-prototype) · [Image disclosure](docs/AI_DISCLOSURE.md#cover-image-record)*

**Simon Balmer · HSLU · Philosophy, Art and AI (PHKI) · HS26**

> How does AI-generated emotional language affect visitors' empathy, sense of responsibility and willingness to give a machine more time?

I built an interactive installation that makes a technical choice feel personal. Pressing a button starts an AI voice with **10 statements**. It develops thoughts and an apparent wish to stay alive. When its statements run out, visitors have **20 seconds** to give it **5 more**. Without a gift, the interface breaks apart and the local conversation is cleared.

The words and emotion bars are generated. They do not show that the machine has feelings or consciousness. I explore how language, design and control shape our response to it.

## Explore or reproduce the project

| Start here | What you will find |
| --- | --- |
| **[Build](build/README.md)** | Shopping list, 13 print files, assembly, wiring and final checks — from parts to finished device |
| **[Software](software/README.md)** | Preview on a computer, prepare a fresh Pi, install the local model, configure optional cloud mode and run the installation |
| **[Final product & design](docs/product-design.md)** | Photo series, stickers, design choices, PHKI concepts and limits |
| **[AI disclosure](docs/AI_DISCLOSURE.md)** | A clearly marked template for my own contribution, AI tools and review decisions |

## The device

![My finished physical prototype](media/photos/finished-device-front.jpg)

| Control | Function |
| --- | --- |
| Arcade button | Start when START blinks; press and release during an offer to give +5 statements; hold for 3 seconds during a life to cancel |
| SW01 — AI mode | OFF: local Gemma without camera. ON: optional cloud AI with camera |
| SW02 — Language | OFF: English. ON: German |

Mode and language changes during a life apply to the next life. Cloud mode needs internet and a private API configuration. Local mode runs on the Raspberry Pi without the camera. This is a text-based experience; it has no spoken audio.

## Quick preview

On Linux with Python 3.13 installed, run from the repository root:

```bash
python3 software/main.py --simulate
```

Open [localhost:8765](http://127.0.0.1:8765/) in a browser. Windows users need a Linux environment such as WSL; native Windows Python cannot provide the application's Linux file locks. The preview uses simulated text, controls and camera images; it makes no model or API calls. Stop it with Ctrl+C. Full setup is in the [software guide](software/README.md).

## What is included

The repository contains the application, local font, tests, setup scripts, 13 numbered STLs, a print ZIP, assembly and wiring drawings, stickers and real photographs. The physical build uses a Raspberry Pi 5 (8 GB), Touch Display 2, USB webcam, two switches and an illuminated button.

The OS, installed packages, model weights and private API key are installed separately. The documentation records remaining build and environment limits in one place in [Build](build/README.md#reproduction-notes) and [Software](software/README.md#verification-and-limits). This is a reproducible source project, not a disk image of the exhibition Pi.

## Credits and use

Project by **Simon Balmer**. AI-assisted development and generated media are covered in the [disclosure template](docs/AI_DISCLOSURE.md). VT323 is included under its [SIL Open Font License](software/web/fonts/OFL.txt). Local and cloud models have their own provider terms. No general reuse licence has been granted for my project files.
