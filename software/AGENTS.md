# Agent guide — Just One More Moment

Current user instructions take priority. Keep changes focused and preserve the working Raspberry Pi installation.

## Start here

- Read [Software setup](README.md), [Build](../build/README.md) and, for prompt changes, [Prompt notes](docs/PROMPTS.md).
- Communicate with Simon in German. Write public documentation in simple English, from Simon Balmer's perspective.
- Keep the existing retro style, local VT323 font and red/black/white/grey palette.
- Keep runtime paths together in `software/`; launchers, imports and browser assets depend on them.

## Architecture

- `main.py`: loopback HTTP server, hardware loop and camera updates.
- `life_runtime.py`, `local_runtime.py`: authoritative state and one cancellable model worker.
- `model.py`, `cloud_model.py`, `cloud_config.py`, `prompts.py`: local/cloud requests, private configuration and EN/DE prompts.
- `hardware_pins.py`, `hardware_io.py`, `life_hardware.py`, `pixel_lock.py`: GPIO, synchronised feedback and shared SPI access.
- `web/`: local interface, font and code-generated graphics; no external assets or build step.
- `startup.py`, `autostart/`, `boot/`: separate decorative opening and optional setup.
- `screen_pixels.py`: optional Wayland desktop ambient light; yields to the installation's pixel lock.

## Behaviour to preserve

- A fresh button press starts 10 statements. Only after the full budget and reading buffer is used, a 20-second offer allows a gift of 5 more. Accept gifts on release; holding for 3 seconds cancels and takes priority.
- SW01 OFF: local Gemma without camera; ON: optional cloud/camera mode. SW02 OFF: English; ON: German. During a life, changes apply to the next life.
- Each life keeps its original prompts and accepted text history. Errors retry the same text prompt. Do not assume an unconfirmed gift or tell the model about later lives.
- Joy/curiosity develops towards fear and final words; a gift brings relief, then development towards the new ending. These are fictional emotions, not evidence of consciousness. Do not introduce threats or blame.
- Backend IDs and confirmed visible browser time govern progress, screen and light. Preserve stale-event rejection, refresh continuity and pause behaviour; no unseen next statement or catch-up after disconnect.
- Clear application-held conversation/image buffers on end or cancellation and unload the local model. Keep the memory guard: 900 MiB available RAM / 512 MiB free swap. Do not silently change system swap.
- Preserve the locally served UI, structured response parsing, two-sentence / 600-character display limit and relative emotion shares totalling 100%.

## Hardware and data

- BCM pins: button 17, button LED 27, SW01 22, SW02 23; NeoPixels use GPIO10 / SPI0.0. There are 11 RGB pixels, grouped `3 | 3 | 1 | 1 | 3` from DIN.
- Switches: closed/LOW = OFF, open/HIGH = ON; use `hardware_io.switch_on()`. Use the context managers and pixel lock; no parallel direct SPI writers.
- Local inference uses loopback Ollama with `gemma4:e2b`. System Python, Chromium and OS hardware packages are used; no downloads on application startup.
- Cloud inference needs enabled private configuration and a deliberate online START. The fixed endpoint is OpenAI Responses over HTTPS; use `store=false`. Reachability checks are separate from inference.
- API keys stay outside Git, chat, browser and logs. Use `configure-openai.py`; private config/secret files need user-only permissions. Do not silently change an existing model or configuration.
- Cloud requests use one fresh 320 × 240 image, no image history or video upload. Close the camera and discard buffers on end, cancellation or loss of the browser. Local cleanup is not a provider-side deletion guarantee.

## Changes and checks

- Do not run live model/API, camera, GPIO or LED tests as routine checks. Use simulation; arrange deliberate hardware tests with a person present.
- Do not alter existing SPI, network, sudo, login, boot files, services or swap as a routine repair. Optional system setup needs an explicit user request; follow [Maintenance](docs/MAINTENANCE.md) and preserve its undo path.
- Do not interrupt an active life, reboot or shut down the Pi without a user request. Respect Escape: no automatic reopening. Documentation-only changes need no application or model run.
- After application changes, reopen once only if the installation is idle and has not been closed with Escape; do not interrupt an active life.
- Run relevant simulated checks from this folder on Linux:

```bash
python3 -m unittest discover -q
python3 -m compileall -q .
bash -n start-installation.sh install-autostart.sh start-screen-pixels.sh install-network-setup.sh
```

Optional Chromium checks: `MOMENT_BROWSER_TEST=1 python3 -m unittest -q tests.test_browser tests.test_startup_browser`. Native Windows lacks `fcntl`; distinguish platform limits from test failures. No extra packages or live inference are needed for the normal test suite.
