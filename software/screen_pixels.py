"""Lokales Desktop-Ambientlicht unter labwc/Wayland. Keine Bilddateien."""
import io
import colorsys
import logging
import os
import signal
import subprocess
import threading
from PIL import Image
import hardware_pins as pins
from hardware_io import encode_pixels
from pixel_lock import acquire

# Physische Reihenfolge ab DIN. Jedes Dreierpaket zeigt dieselbe Palette;
# die beiden einzelnen LEDs zeigen die Hauptakzentfarbe.
GROUPS = (3, 3, 1, 1, 3)
BRIGHTNESS = 0.20
INTERVAL = 0.2
SMOOTHING = 0.45
# Separat justierbarer Weißabgleich; ohne Messung keine erfundenen Korrekturen.
WHITE_BALANCE = (1.0, 1.0, 1.0)


def palette(image):
    image = image.convert('RGB')
    image.thumbnail((96, 96))
    # Farbton-Familien statt drei Flächenmittelwerte: Weiß verdrängt sonst
    # kleine, aber prägende Akzente. Dunkle Pixel beeinflussen die Wahl kaum.
    buckets = {}
    neutral = []
    pixels = list(image.getdata())
    for rgb in pixels:
        hue, saturation, value = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
        if saturation < 0.20:
            if value >= 0.55:
                neutral.append(rgb)
            continue
        if value < 0.12:
            continue
        key = int((hue * 18 + 0.5) % 18)
        weight = (0.25 + 0.75 * saturation) * value
        score, sums = buckets.setdefault(key, [0.0, [0.0] * 3])
        buckets[key][0] = score + weight
        for channel in range(3):
            sums[channel] += rgb[channel] * weight
    ranked = sorted(buckets.values(), key=lambda item: item[0], reverse=True)
    if not ranked or ranked[0][0] < len(pixels) * 0.003:
        # Rein graue/weiße oder schwarze Inhalte bleiben entsprechend neutral.
        return [tuple(round(sum(rgb[c] for rgb in pixels) / len(pixels))
                      for c in range(3))] * 3
    def color(bucket):
        score, sums = bucket
        return tuple(round(value / score) for value in sums)
    main = color(ranked[0])
    candidates = []
    for bucket in ranked[1:]:
        candidate = color(bucket)
        if bucket[0] >= ranked[0][0] * 0.25 and sum(
                (a - b) ** 2 for a, b in zip(candidate, main)) > 80 ** 2:
            candidates.append((bucket[0], candidate))
    # Neutrale Flächen sind ein schwächer gewichteter Kandidat, kein Pflichtplatz.
    # Kleine farbige Akzente bleiben Hauptfarbe, große weiße Seiten bleiben erkennbar.
    if len(neutral) >= len(pixels) * 0.25:
        white = tuple(round(sum(rgb[c] for rgb in neutral) / len(neutral))
                      for c in range(3))
        candidates.append((len(neutral) * 0.15, white))
    result = [main]
    for _, candidate in sorted(candidates, reverse=True):
        if len(result) == 3:
            break
        if all(sum((a - b) ** 2 for a, b in zip(candidate, old)) > 80 ** 2
               for old in result):
            result.append(candidate)
    return (result + [main] * 3)[:3]


def led_channel(value, gain=1.0):
    """sRGB-Bildwert → lineare LED-PWM; Helligkeitslimit zuletzt anwenden."""
    encoded = value / 255
    linear = encoded / 12.92 if encoded <= 0.04045 else ((encoded + 0.055) / 1.055) ** 2.4
    return max(0, min(255, round(linear * 255 * BRIGHTNESS * gain)))


def smooth(previous, target):
    if previous is None:
        return target
    return [tuple(round(old + SMOOTHING * (new - old))
                  if abs(new - old) > 1 else new
                  for old, new in zip(before, after))
            for before, after in zip(previous, target)]


def frame(colors):
    values = []
    for size in GROUPS:
        values.extend(colors if size == 3 else colors[:1])
    if len(values) != pins.NEOPIXEL_COUNT:
        raise ValueError('LED-Gruppen passen nicht zur konfigurierten Anzahl')
    return [tuple(led_channel(c, gain) for c, gain in zip(rgb, WHITE_BALANCE))
            for rgb in values]


def capture():
    result = subprocess.run(['grim', '-s', '0.125', '-t', 'ppm', '-'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=4, check=True)
    with Image.open(io.BytesIO(result.stdout)) as image:
        return palette(image)


def main():
    import spidev
    logging.basicConfig(level=logging.INFO)
    stop = threading.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stop.set())
    # Zweiter Autostart darf keinen zweiten Schreiber erzeugen.
    import fcntl
    from pathlib import Path
    singleton = open(Path(os.environ['XDG_RUNTIME_DIR']) / 'screen-pixels.lock', 'a')
    try:
        fcntl.flock(singleton, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return
    failed = False
    previous = None
    while not stop.is_set():
        try:
            # Bei reservierten LEDs auch keine Screenshots erstellen.
            try:
                reservation = acquire(False)
            except BlockingIOError:
                previous = None
                stop.wait(INTERVAL)
                continue
            reservation.close()
            pixels = smooth(previous, frame(capture()))
            # Nach Aufnahme erneut prüfen; Anwendung kann inzwischen gestartet sein.
            try:
                reservation = acquire(False)
            except BlockingIOError:
                previous = None
                continue
            with reservation:
                spi = spidev.SpiDev()
                try:
                    spi.open(pins.NEOPIXEL_SPI_BUS, pins.NEOPIXEL_SPI_DEVICE)
                    spi.max_speed_hz = pins.NEOPIXEL_SPI_HZ
                    spi.mode = 0
                    spi.xfer2(encode_pixels(pixels))
                finally:
                    spi.close()
            previous = pixels
            failed = False
        except (OSError, subprocess.SubprocessError, ValueError):
            if not failed:
                logging.exception('Ambientlicht wartet auf Desktop/SPI')
            failed = True
        stop.wait(3 if failed else INTERVAL)


if __name__ == '__main__':
    main()
