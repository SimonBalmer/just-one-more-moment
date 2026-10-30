# Software setup

[Overview](../README.md) · [Build](../build/README.md) · [Product & design](../docs/product-design.md)

**Simon Balmer · HSLU PHKI HS26**

The application is Python plus local HTML/CSS/JavaScript. It has no Node build, web framework or pip runtime dependencies. Hardware access uses OS packages. All commands below run on the Pi unless marked as a computer preview.

## 1. Preview without hardware

Use a Linux computer with Python **3.13** and Git, then:

```bash
git clone https://github.com/SimonBalmer/just-one-more-moment.git
cd just-one-more-moment/software
python3 main.py --simulate
```

On Windows, run these commands inside a Linux environment such as WSL. Native Windows Python is unsupported because `startup.py` imports Linux `fcntl` file locks. Open [http://127.0.0.1:8765/](http://127.0.0.1:8765/) in a browser. The preview provides virtual switches and a button. Wait until START blinks, then press and release. Hold the virtual button for three seconds to cancel a life. Ctrl+C stops the server.

Simulation uses generated test data and synthetic camera images. It does not open GPIOs, Ollama, the real camera or the cloud API. An alternative port is available with `--port 8766`.

## 2. Prepare a fresh Raspberry Pi

1. Use **Raspberry Pi 5, 8 GB**, cooling and the official 27 W supply. Flash **64-bit Raspberry Pi OS with Desktop** using [Raspberry Pi Imager](https://www.raspberrypi.com/software/). Use a release with Python 3.13; this is the Python version recorded by the source handover. Configure your own user and initial network in Imager. The desktop is required for the kiosk.
2. Mount and connect the Touch Display 2 while power is disconnected, following the [official display guide](https://www.raspberrypi.com/documentation/accessories/touch-display-2.html). Start the Pi, complete setup and set the display to **landscape, 1280 × 720** in the desktop display settings. Check the image and touch before adding the enclosure controls.
3. In a Pi terminal, install the runtime packages:

   ```bash
   sudo apt update
   sudo apt install git curl python3 python3-gpiozero python3-lgpio python3-spidev chromium util-linux ffmpeg
   python3 --version
   ```

   `ffmpeg` is needed for the USB camera. The Python web server uses only the standard library. Use system Python, without a virtual environment.
4. Enable **SPI** using `sudo raspi-config` → Interface Options → SPI, following the [Pi configuration guide](https://www.raspberrypi.com/documentation/computers/configuration.html#spi). Arrange a normal reboot if requested. The exhibition source records `dtoverlay=spi0-1cs,no_miso`; a fresh setup must provide **SPI0.0** without conflicting overlays. Do not blindly append both configurations.
5. Check the device and access:

   ```bash
   ls -l /dev/spidev0.0 /dev/gpiochip0
   id
   ```

   On standard Pi OS, add your user to the hardware groups if needed:

   ```bash
   sudo usermod -aG gpio,spi,video "$USER"
   ```

   Log out and back in after changing groups. Do not run the application as root.

For kiosk startup after boot, enable **Desktop Autologin** in `raspi-config` if appropriate for your installation. The application installer does not change desktop login or system services.

## 3. Get the source

From your home directory on the Pi:

```bash
git clone https://github.com/SimonBalmer/just-one-more-moment.git
cd just-one-more-moment/software
chmod +x start-installation.sh install-autostart.sh start-screen-pixels.sh
python3 -c "import gpiozero, lgpio, spidev; print('Hardware packages available')"
```

Keep the `software/` files together. The launch scripts resolve their own folder. If downloading a GitHub ZIP instead, extract it, open its `software/` folder and run the same `chmod` command.

## 4. Install the local model

Install Ollama using its [official Linux instructions](https://docs.ollama.com/linux). This downloads and runs the provider's installer; review it before running it:

```bash
curl -fsSL https://ollama.com/install.sh -o /tmp/ollama-install.sh
sh /tmp/ollama-install.sh
sudo systemctl enable --now ollama
ollama pull gemma4:e2b
ollama --version
ollama list
curl -fsS http://127.0.0.1:11434/api/tags
```

The required tag is [`gemma4:e2b`](https://ollama.com/library/gemma4:e2b). Model weights are not in this repository. The application does not download them at startup. The final command should list the installed model without generating a response. The application uses the loopback Ollama API on port 11434; it does not need this service exposed to the network.

The local settings are in [model.py](model.py): 6,144-token context, output limit 420 tokens, thinking disabled, temperature 1, batch 128 and memory mapping enabled. These settings are part of the project, not proof that every Ollama release or replacement model will work identically.

## 5. Start and operate

Finish the [hardware wiring and checks](../build/README.md#6-install-and-check-before-closing), then run from the graphical Pi desktop in `software/`:

```bash
./start-installation.sh
```

The launcher opens a dedicated Chromium kiosk at `http://127.0.0.1:8765/`. It prevents a second launcher from opening another copy. **Escape** closes the application; **F11** changes fullscreen. Closing the kiosk also stops its backend. It does not automatically reopen after Escape.

| Action | Result |
| --- | --- |
| SW01 OFF / ON | Local Gemma without camera / cloud mode with camera |
| SW02 OFF / ON | English / German |
| Wait for blinking START, then press | Explanation, appearance animation and a life with 10 statements |
| Press and release during the 20-second offer | +5 statements; another offer follows at 15, 20, etc. |
| Do nothing during the offer | Final breakup, local conversation cleanup and return to the start screen |
| Hold for 3 seconds during a life | Cancel, clear the local conversation and return to the start screen |

Changes made to the switches during a life are queued for the next one. Release the button before starting again. There is no microphone, text input or speech output. Browser refresh restores the current state rather than starting a new life.

The server owns the state. Animations and offers use confirmed visible browser time; a missing browser pauses progression. The hardware long press remains available. Each model response contains text and emotion labels/values; the displayed bars are relative shares, not measured feelings.

Stop with Escape, then use the desktop's shutdown menu before unplugging the Pi.

## 6. Optional cloud mode

Cloud mode needs an API account, a compatible image-capable model, internet and the C270 camera. It can incur API charges. Before use, explain that current camera images and generated conversation context can be sent to OpenAI. Local mode works without this configuration.

From `software/`, run locally:

```bash
python3 configure-openai.py
```

Enter the key only into the private terminal prompt. The helper writes `~/.config/just-one-more-moment/openai.json` and a separate `openai.key`, both with user-only permissions. `XDG_CONFIG_HOME` can change this location. No test API call is made. [openai.example.json](openai.example.json) is a disabled example, not a key file to commit.

The shipped helper defaults to `gpt-6.1-terra`, reasoning `none` and 1,024 output tokens. This is a source default, not a guarantee of API availability for your account. To select an available compatible model explicitly:

```bash
python3 configure-openai.py --model YOUR_MODEL_ID
```

Replace `YOUR_MODEL_ID` with your actual model ID and verify that it supports image input, Responses streaming and the structured output schema in [cloud_model.py](cloud_model.py). A private existing key file can instead be referenced with `--key-file /absolute/path/openai.key`. Never put a key in a command, Git, browser or log.

Restart the application, select SW01 ON and press START. The application checks HTTPS reachability first. Without a usable API configuration it only offers the online introduction; it cannot generate a cloud life.

The camera is selected from `/dev/v4l/by-id/*-video-index0`, falling back to `/dev/video0`. `ffmpeg` reads 320 × 240 colour frames into RAM. The intro shows an 80 × 60 red pixel preview at 5 FPS. For each cloud generation, the adapter sends **one fresh PNG**; earlier images are not kept in the request history. Text history remains for that life. A missing image prevents the model request. The camera closes on end, cancellation or loss of the browser.

Requests use the fixed HTTPS Responses endpoint and `store=false`. Local cleanup clears application-held text and image buffers; it is not secure RAM erasure or a guarantee of provider-side deletion. See the [provider data controls](https://platform.openai.com/docs/guides/your-data).

## 7. Optional automatic startup

Once manual operation works and the repository is at its final location:

```bash
./install-autostart.sh
```

This creates the current user's `~/.config/autostart/just-one-more-moment.desktop`. It requires an existing graphical login. Re-run the installer after moving the repository. To disable it, remove that desktop entry. Autostart includes the decorative opening once per OS boot; ordinary manual launch goes straight to the start screen.

The [maintenance notes](docs/MAINTENANCE.md) cover optional black boot graphics, the smartphone hotspot helper, ambient lighting and reversal steps. These are optional system customisations, not required to run the artwork.

## Troubleshooting

| Problem | Check |
| --- | --- |
| Kiosk will not open | Run from a graphical session; check Chromium is installed and port 8765 is free |
| Hardware permission error | Check `/dev/gpiochip0`, `/dev/spidev0.0`, SPI and your `gpio`/`spi` groups; log in again after changes |
| Wrong selector position | OFF is closed to GND, ON is open. Check the two wired switch contacts |
| Local model will not load | Check `ollama list`, the exact tag, loopback API and available RAM/swap |
| Memory protection stops a life | Code requires at least 900 MiB available RAM and 512 MiB free swap; check `free -h`, close other apps and retry. The app does not create swap |
| Online mode cannot start | Check internet, account/model access, private config permissions, key and camera; setup is read on application launch |
| Camera unavailable | Check USB, `ffmpeg`, `/dev/video*`, video-group access and whether another app owns it |
| Pixels stay off | Check DIN, diode direction, common ground, SPI0.0 and that another SPI writer is not running; the source drives 11 pixels |
| Blank display | Check ribbon orientation and matching CAM/DISP setup with power disconnected; follow the display guide |

Launcher logs are in `${XDG_STATE_HOME:-~/.local/state}/just-one-more-moment/`, in `autostart.log` and `autostart.previous.log`. Conversation content is not intentionally logged. Keep logs private when diagnosing errors.

## Checks

From `software/`:

```bash
python3 -m unittest discover -q
```

The tests use simulated hardware and model responses. Optional Chromium checks on Linux:

```bash
MOMENT_BROWSER_TEST=1 python3 -m unittest -q tests.test_browser tests.test_startup_browser
bash -n start-installation.sh install-autostart.sh start-screen-pixels.sh install-network-setup.sh
```

These tests check the software with simulated hardware and model responses. Use the [build checks](../build/README.md#6-install-and-check-before-closing) for the assembled device. A fresh-Pi installation was not rerun during this documentation update. Model outputs vary between runs and model versions.


## Source map and process

| Files | Purpose |
| --- | --- |
| `main.py`, `life_runtime.py`, `local_runtime.py` | Loopback server, state, statement budget and cancellable model worker |
| `model.py`, `cloud_model.py`, `cloud_config.py`, `prompts.py` | Local/cloud requests, private settings and EN/DE prompts |
| `hardware_pins.py`, `hardware_io.py`, `life_hardware.py`, `pixel_lock.py` | Pin assignment, SPI pixels and synchronised feedback |
| `web/` | Complete interface, graphics and local VT323 font |
| `startup.py`, `autostart/`, `boot/` | Startup presentation and optional templates |
| `tests/` | Regression tests |

The [prompt notes and process evidence](docs/PROMPTS.md) are optional reading. The build and setup do not require reading the development history.
