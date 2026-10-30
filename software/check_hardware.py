"""Interaktiver Hardwaretest ohne Display, Kamera oder Modelle."""
import argparse
import os
import time

import hardware_pins as pins
from hardware_io import open_inputs, open_button_led, NeoPixels


def input_test(seconds):
    with open_inputs() as devices:
        names = ('Arcade-Taster', 'Kippschalter 1', 'Kippschalter 2')
        results = []
        for device, name in zip(devices, names):
            print(f'\n{name}: jetzt betätigen und wieder zurückstellen / loslassen. '
                  f'Zeit: {seconds:g} Sekunden.', flush=True)
            previous = device.is_pressed
            seen = {previous}
            changed = 0
            print('Anfang: ' + ('Kontakt GESCHLOSSEN' if previous else 'Kontakt OFFEN'), flush=True)
            until = time.monotonic() + seconds
            candidate = previous
            since = time.monotonic()
            while time.monotonic() < until:
                value = device.is_pressed
                if value != candidate:
                    candidate, since = value, time.monotonic()
                if candidate != previous and time.monotonic() - since >= 0.05:
                    previous = candidate
                    seen.add(previous)
                    changed += 1
                    print(name + ': ' + ('GESCHLOSSEN / LOW' if previous else 'OFFEN / HIGH'), flush=True)
                time.sleep(0.01)
            ok = len(seen) == 2 and changed >= 2
            results.append(ok)
            print(f'{name}: ' + ('OK, beide Zustände und Rückkehr erkannt' if ok else
                  'NICHT BESTÄTIGT, bitte erneut prüfen'), flush=True)
        return all(results)


def led_test():
    with open_button_led() as led:
        print('Taster-LED: 2 Sekunden an, danach dreimal blinken.', flush=True)
        led.on()
        time.sleep(2)
        led.off()
        time.sleep(0.5)
        led.blink(on_time=0.4, off_time=0.4, n=3, background=False)
    return input('War die Taster-LED an und blinkte dreimal? [j/N] ').strip().lower() == 'j'


def pixel_test():
    path = f'/dev/spidev{pins.NEOPIXEL_SPI_BUS}.{pins.NEOPIXEL_SPI_DEVICE}'
    if not os.path.exists(path):
        print(f'NEOPIXEL NICHT GETESTET: {path} fehlt; SPI0 muss aktiviert sein.', flush=True)
        return False
    black = [(0, 0, 0)] * pins.NEOPIXEL_COUNT
    with NeoPixels() as pixels:
        for name, color in [('Rot', (16, 0, 0)), ('Grün', (0, 16, 0)), ('Blau', (0, 0, 16))]:
            print(f'Alle {pins.NEOPIXEL_COUNT} NeoPixels: {name}, schwache Helligkeit, 2 Sekunden.', flush=True)
            pixels.fill(*color)
            time.sleep(2)
        print(f'Jetzt läuft ein schwaches weißes Licht einzeln über alle {pins.NEOPIXEL_COUNT} LEDs.', flush=True)
        for index in range(pins.NEOPIXEL_COUNT):
            frame = list(black)
            frame[index] = (8, 8, 8)
            pixels.write(frame)
            time.sleep(0.3)
    return input(f'Alle {pins.NEOPIXEL_COUNT} LEDs mit korrekten Farben und Lauflicht gesehen? [j/N] ').strip().lower() == 'j'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', 'inputs', 'led', 'pixels'], default='all')
    parser.add_argument('--seconds', type=float, default=15)
    args = parser.parse_args()
    if not 3 <= args.seconds <= 120:
        parser.error('--seconds muss zwischen 3 und 120 liegen')
    tests = [('inputs', lambda: input_test(args.seconds)), ('led', led_test), ('pixels', pixel_test)]
    results = []
    try:
        for name, test in tests:
            if args.stage in ('all', name):
                try:
                    ok = test()
                except (OSError, RuntimeError) as exc:
                    print(f'{name}: FEHLER: {exc}', flush=True)
                    ok = False
                results.append(ok)
                print(f'{name}: ' + ('BESTÄTIGT' if ok else 'OFFEN / NICHT BESTÄTIGT'), flush=True)
    except (KeyboardInterrupt, EOFError):
        print('\nTest abgebrochen; geöffnete Ausgänge werden ausgeschaltet.', flush=True)
        return 130
    return 0 if all(results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
