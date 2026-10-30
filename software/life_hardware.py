"""Hardware-Rückmeldung aus dem Controllerthread; keine Modellanfragen."""
from contextlib import ExitStack
import math
import time
from hardware_io import open_inputs, open_button_led, NeoPixels, switch_on
import hardware_pins as pins

# Spread failures across all five physical groups; never a DIN chase.
FAILURE_ORDER = (0, 3, 8, 6, 7, 1, 4, 9, 2, 5, 10)


class LifeHardware:
    def __init__(self, log):
        self.stack = ExitStack()
        self.pixels = None
        self.last_frame = 0
        try:
            self.button, self.mode_switch, self.language_switch = self.stack.enter_context(open_inputs())
            self.led = self.stack.enter_context(open_button_led())
            try:
                self.pixels = self.stack.enter_context(NeoPixels())
            except OSError as error:
                log.warning('NeoPixels nicht verfügbar (SPI aktivieren): %s', error)
            self.log = log
        except BaseException:
            self.stack.close()
            raise

    def switches(self):
        return switch_on(self.mode_switch), switch_on(self.language_switch)

    def pressed(self):
        return bool(self.button.is_pressed)

    def update(self, feedback, led=False):
        now = time.monotonic()
        self.led.value = led
        if not self.pixels or now - self.last_frame < 1 / 12:
            return
        self.last_frame = now
        frame = pixel_frame(feedback)
        try:
            self.pixels.write(frame)
        except OSError as error:
            self.log.error('NeoPixel-Ausgabe fehlgeschlagen: %s', error)
            try:
                self.pixels.off()
            except OSError:
                pass
            self.pixels = None

    def close(self):
        self.stack.close()


def pixel_frame(feedback):
    """Pure RGB renderer. Animation time comes from the shared backend timeline."""
    mode = feedback['mode']
    if mode == 'off':
        return [(0, 0, 0)] * pins.NEOPIXEL_COUNT
    t, breath = feedback['time'], feedback['breath']
    gain = feedback['energy']
    progress = feedback['progress']
    if mode == 'birth':
        gain *= progress * progress * (3 - 2 * progress)
        breath = progress
    elif mode == 'gift':
        gain *= 1 + .4 * math.sin(math.pi * progress)
    frame = []
    for index in range(pins.NEOPIXEL_COUNT):
        # Continuous breathing remains underneath the soft, low-level white shimmer.
        drift = 1.8 * math.sin(t * .83 + index * .37)
        pixel_gain = gain
        if mode in ('offer','death','gift'):
            decay = feedback.get('decay', .75+.25*progress if mode == 'death' else .75*progress if mode == 'offer' else 0.)
            threshold = (FAILURE_ORDER.index(index)+.85)/pins.NEOPIXEL_COUNT
            if decay >= threshold:
                frame.append((0, 0, 0))
                continue
            failure = max(0., (decay-(threshold-.06))/.06)
            if mode == 'gift':
                pixel_gain *= 1-failure
            elif failure > 0:
                # Local red/white sputters, increasingly ragged near extinction.
                flicker = .12+.88*(.5+.5*math.sin(t*(19 if mode=='death' else 8)+index*2.7))**2
                white = round(18*failure*flicker*gain)
                red = round(((1-failure)*35+18*failure)*flicker*gain)
                frame.append((min(60,red),min(18,white),min(18,white)))
                continue
        red = round(max(0, min(60, (20 + 28 * breath + drift) * pixel_gain)))
        white = round(3 * ((1 + math.sin(t * 9 + index * 1.73)) / 2) ** 5 * gain) if mode == 'writing' else 0
        frame.append((red, min(4, white), min(4, white)))
    return frame
