![Just One More Moment](../../hardware/diagrams/project-banner.svg)

# Optional setup & maintenance

[Software setup](../README.md) · [Build](../../build/README.md)

These options are separate from the normal installation. Run commands from `software/` on the Pi. None is needed for the computer simulation.

## Opening animation

Autostart includes an 18.4-second opening with ASCII characters, HSLU, PHKI HS26, Simon Balmer and the project logo. `startup.py` records only the OS boot ID in `~/.local/state/just-one-more-moment/startup-boot-id`. It claims the opening once per boot. It does not store conversation data or start a model life. Installation marks the current boot as seen, so the opening is armed for the next normal boot.

To preview without hardware or model calls:

```bash
python3 main.py --simulate --preview-startup --port 8766
```

Open `http://127.0.0.1:8766/`. To disable the opening, remove `--boot-animation` from the user's `~/.config/autostart/just-one-more-moment.desktop`. To disable all autostart, remove that desktop entry. The installer uses `XDG_CONFIG_HOME` if set.

## Black OS boot graphics

This changes Pi boot configuration and Plymouth, not just the application. It requires the Pi's existing `plymouth-set-default-theme` and `update-initramfs` tools. Preview the changes first:

```bash
python3 install-startup-boot.py
```

To apply the displayed plan deliberately:

```bash
sudo python3 install-startup-boot.py --apply
```

The script sets `disable_splash=1`, adds `logo.nologo`, installs the `moment-black` Plymouth theme and rebuilds initramfs. It saves affected files under `/var/backups/just-one-more-moment-boot-*`, reports the exact backup path and restores it on installation failure. It does not reboot, change SPI or configure desktop login.

To undo, use the **actual backup directory printed on your Pi**, not a path copied from another installation:

```bash
sudo python3 install-startup-boot.py --restore /var/backups/YOUR_BACKUP_DIRECTORY
```

The application opening is independent of this OS theme. Changing one does not disable the other.

## Smartphone hotspot helper

The online start checks HTTPS reachability of `api.openai.com` without a key or inference. If offline, the interface offers the configured smartphone hotspot. Ordinary Wi-Fi can be set up through the desktop instead.

To enable the helper deliberately on a Pi using NetworkManager:

```bash
sudo bash install-network-setup.sh "$USER"
```

It creates the profile `Just one more moment — smartphone`, SSID `just-one-more-moment`, password `hslu-phki-hs26`, and a Polkit rule allowing that user to activate/deactivate connections. It does not activate a connection during installation. These are public exhibition defaults, not private credentials. On the phone, create a hotspot with that SSID/password, then press the device button to connect and check again. A failed attempt tries to restore the previous Wi-Fi connection.

To remove this optional setup:

```bash
sudo nmcli connection delete 'Just one more moment — smartphone'
sudo rm -f /etc/polkit-1/rules.d/49-just-one-more-moment-network.rules
```

Removing the profile disconnects it if active; use another connection first. For private deployment, change the public credentials consistently in `network_setup.py`, the setup script and the displayed instructions.

## Desktop ambient light

<img src="../../media/photos/desktop-ambient-light.jpg" alt="My prototype playing a fireplace scene with warm case lighting" width="150" align="right">

This separate helper reads local Wayland screen colours with `grim` and Pillow. It uses neither camera nor cloud. The main installation owns the pixel lock and takes priority; the helper avoids taking screen captures while the installation owns it.

For example, a fireplace video turns the enclosure into a small ambient display, with LEDs following the screen colours. This is another way to reuse the same case and lighting.

Close the installation with Escape. To try the helper from a graphical Wayland session in `software/`:

```bash
sudo apt install python3-pil grim
./start-screen-pixels.sh
```

Play your chosen content on the desktop; Ctrl+C stops the helper. For automatic startup, use `./install-autostart.sh --ambient`. Remove `~/.config/autostart/screen-pixels.desktop` to disable its future autostart. Do not run independent SPI writers alongside the installation. The shared lock name `please-dont-unplug-me-neopixels.lock` is retained for compatibility.

<br clear="all">

## Documentation generators

The [build guide](../../build/README.md#files-and-build-settings) lists the optional drawing dependencies. The PDF, PNG, SVG and print pack are ready to use; running a generator is not part of device setup. Runtime Python modules, GPIO assignments and prompt versions remain at their original paths.
