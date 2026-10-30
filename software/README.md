# Software source — Just One More Moment

**Simon Balmer · HSLU PHKI · 2026**

The project is a Raspberry Pi 5 installation that explores the influence of emotional AI-generated language on empathy, responsibility, and user decisions. The device's simulated emotions do not prove consciousness.

## Current source snapshot (30 October 2026)

The complete application snapshot has been prepared and locally tested. Its original operating layout is intentionally preserved: entry point `main.py`, kiosk launcher `start-installation.sh`, life cycle `life_runtime.py`, Ollama integration `model.py`, optional OpenAI integration `cloud_model.py`, prompts `prompts.py`, GPIO modules `hardware_pins.py`, `hardware_io.py`, `life_hardware.py`, browser UI in `web/`, and regression tests in `tests/`.

**Important:** This page documents the source structure; it does not mean all application files have been published in this GitHub directory. The original source archive must be uploaded separately before a third party can reproduce the executable software from GitHub alone. Existing mechanical and electronics documentation remains available in the rest of the repository.

## Running the original source

From the root folder of the source snapshot:

```bash
python3 main.py --simulate
# Open http://127.0.0.1:8765/
```

On the Raspberry Pi (with graphical desktop, Chromium, GPIO support and locally installed Ollama model `gemma4:e2b`):

```bash
./start-installation.sh
```

Optional cloud mode requires deliberate configuration with `python3 configure-openai.py` and private credentials; do not commit credentials to GitHub. The source archive contains full setup and startup documentation.

## Functionality and verification

The current life cycle starts with ten generated statements, and visitors may grant further sets of five. Holding the physical button for three seconds ends a life early. Separate switches control local/cloud mode and English/German. The normal Linux simulation test run on 30 October 2026 completed **121 tests, no failures, two skipped**. This result does not verify the physical wiring, live model performance, or camera.

The runtime paths and filenames should remain stable when the files are transferred to GitHub. For the device documentation, see [wiring](../hardware/WIRING.md), [build guide](../docs/build-guide.md), and [design](../docs/design.md).

## Development and transparency

The completed source archive contains `docs/DEVELOPMENT.md`, `docs/PROMPTS.md`, prompt revisions and recorded evaluations. AI supported software development and documentation; Simon Balmer made the creative and physical design decisions and takes responsibility for the work.
