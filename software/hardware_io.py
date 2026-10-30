"""Zentraler Hardwarezugriff; beim Import keine Geräte öffnen.

Alle geöffneten Geräte mit `with` benutzen. Schalter über switch_on() lesen: offen/HIGH = AN.
Taster .is_pressed bedeutet gedrückt; bei Schaltern zeigt es nur Kontaktschluss. Pinzuordnung in hardware_pins.py.
"""
from contextlib import contextmanager
import hardware_pins as pins


def switch_on(switch):
    """Logische Hebelstellung: beide als AUS bestätigten Kontakte sind geschlossen."""
    return bool(switch.is_pressed) == pins.SWITCH_ON_CLOSED


@contextmanager
def open_inputs():
    from contextlib import ExitStack
    from gpiozero import Button
    from gpiozero.pins.lgpio import LGPIOFactory
    with ExitStack() as stack:
        factory = stack.enter_context(LGPIOFactory(chip=pins.GPIO_CHIP))
        yield tuple(stack.enter_context(Button(pin, pull_up=True,
                    bounce_time=pins.DEBOUNCE_SECONDS, pin_factory=factory))
                    for pin in (pins.BUTTON, pins.SWITCH_1, pins.SWITCH_2))


@contextmanager
def open_button_led():
    from gpiozero import LED
    from gpiozero.pins.lgpio import LGPIOFactory
    with LGPIOFactory(chip=pins.GPIO_CHIP) as factory:
        with LED(pins.BUTTON_LED, initial_value=False, pin_factory=factory) as led:
            try:
                yield led
            finally:
                led.off()


def encode_pixels(pixels):
    # WS2812 RGB, Drahtreihenfolge GRB: 100=0, 110=1 bei SPI 2,4 MHz.
    encoded = bytearray(240)  # 800 µs LOW als Reset
    for red, green, blue in pixels:
        for channel in (green, red, blue):
            word = 0
            for bit in range(7, -1, -1):
                word = (word << 3) | (0b110 if channel & (1 << bit) else 0b100)
            encoded.extend(word.to_bytes(3, 'big'))
    encoded.extend(bytes(240))
    return encoded


class NeoPixels:
    """RGB-Pixel, GRB über SPI0; write() erwartet RGB-Werte 0–255."""

    def __enter__(self):
        import spidev
        from pixel_lock import acquire
        self.reservation = acquire()
        try:
            self.spi = spidev.SpiDev()
        except BaseException:
            self.reservation.close()
            raise
        try:
            self.spi.open(pins.NEOPIXEL_SPI_BUS, pins.NEOPIXEL_SPI_DEVICE)
            self.spi.max_speed_hz = pins.NEOPIXEL_SPI_HZ
            self.spi.mode = 0
            # CS0 unbeschaltet; SPI_NO_CS funktioniert auf diesem Pi 5 nicht.
            self.off()
        except BaseException:
            self.spi.close()
            self.reservation.close()
            raise
        return self

    def write(self, pixels):
        pixels = list(pixels)
        if len(pixels) != pins.NEOPIXEL_COUNT:
            raise ValueError(f'Genau {pins.NEOPIXEL_COUNT} RGB-Pixel erforderlich')
        if any(len(rgb) != 3 or any(type(c) is not int or not 0 <= c <= 255
                                   for c in rgb) for rgb in pixels):
            raise ValueError('RGB-Kanäle müssen ganze Zahlen von 0 bis 255 sein')
        self.spi.xfer2(encode_pixels(pixels))

    def fill(self, red, green, blue):
        self.write([(red, green, blue)] * pins.NEOPIXEL_COUNT)

    def off(self):
        self.fill(0, 0, 0)

    def __exit__(self, *exc):
        try:
            self.off()
        finally:
            try:
                self.spi.close()
            finally:
                self.reservation.close()
