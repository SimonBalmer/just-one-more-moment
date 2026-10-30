# Project guide — Just One More Moment

**Simon Balmer · PHKI, Lucerne University of Applied Sciences and Arts · 2026**

This is the original running software for the interactive installation. The operating code stays in the project root on purpose: the launcher, imports, browser assets, startup templates, and test suite refer to these paths. Moving modules into a new Python package without changing their imports and launcher would make an existing device stop working.

## Where to start

| Goal | File or folder |
| --- | --- |
| Understand the artwork and its purpose | `README.md`, and the separate public repository's `docs/concept.md` and `docs/design.md` |
| Reproduce the physical enclosure | Public repository: `mechanical/` |
| Assemble and wire electronics | `HARDWARE.md` and public repository `hardware/WIRING.md` |
| Start on a Raspberry Pi | `start-installation.sh` |
| Preview without hardware | `python3 main.py --simulate`, then open `http://127.0.0.1:8765/` |
| Understand interaction and session logic | `main.py`, `life_runtime.py`, `local_runtime.py` |
| Inspect model calls and language | `model.py`, `cloud_model.py`, `prompts.py` |
| Inspect hardware connections | `hardware_pins.py`, `hardware_io.py`, `life_hardware.py` |
| Inspect the graphical interface | `web/` |
| Install autostart | `install-autostart.sh`, `autostart/` |
| Understand boot presentation | `docs/STARTUP.md`, `boot/`, `install-startup-boot.py` |
| Examine design iteration | `docs/DEVELOPMENT.md`, `docs/PROMPTS.md` |
| Run checks | `python3 -m unittest discover -s tests -q` |

## Behavior and scope

The current source uses ten generated statements in a life, with offers of five extra statements. A long press cancels the life. The two physical switches select local/online mode and English/German; they are not software settings in a configuration file. Local inference uses Ollama and the installed `gemma4:e2b` model. Online inference is optional and requires private OpenAI credentials; the local USB camera is only used in the online mode. The installation's language does not demonstrate actual sentience or emotions.

**Privacy:** Never commit `openai.json`, `openai.key`, `.env` or other local secrets. The example configuration is deliberately disabled. Cloud calls may transmit images to an external service when explicitly configured.

## Preservation and testing

This repository snapshot has intentionally not been refactored. No modules, routes, GPIO assignments, timings, prompts, model names, or runtime filenames have been renamed. The archive preserves source files and their relative paths. `AGENTS.md` and `ARCHIV-SHA256.txt` are retained as development/provenance documents, not runtime dependencies. Historic prompts and cloud experiment records are retained under `docs/` for transparency, but they are not read by the running software.

The standard test suite was run in a Linux environment on 30 October 2026: 121 tests, 2 skipped, no failures. This is a **simulated test**, not a Raspberry Pi hardware, camera, Ollama-model or live OpenAI API certification. A real installation requires the relevant hardware and services.

The full public GitHub repository also contains the physical build documentation, printable mechanical files and design documentation. Keep the existing repository's hardware and mechanical resources when publishing this source snapshot; do not replace its root tree with only the software archive.

## AI-use transparency

The artwork intentionally uses AI-generated dialogue. AI assistance has also supported software development and documentation. Hardware design, physical assembly, interaction decisions, selection and responsibility for the final project belong to Simon Balmer. The exact development history is recorded in `docs/DEVELOPMENT.md` and `docs/PROMPTS.md`.
