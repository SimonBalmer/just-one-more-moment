"""Aktuelle Verdrahtung: GPIO-Nummern sind BCM, Header-Pins physisch."""
BUTTON = 17                 # Pin 11; COM an GND Pin 9
BUTTON_LED = 27             # Pin 13; LED− an GND Pin 14
SWITCH_1 = 22               # Pin 15; Gegenkontakt GND Pin 20; offen/HIGH = AN
SWITCH_2 = 23               # Pin 16; Gegenkontakt GND Pin 25; offen/HIGH = AN
NEOPIXEL_DATA = 10          # Pin 19: SPI0 MOSI → DIN
NEOPIXEL_COUNT = 11
NEOPIXEL_SPI_BUS = 0
NEOPIXEL_SPI_DEVICE = 0
# Versorgung ist kein GPIO: 5 V über Diode und gemeinsame Masse.
# Pin 4 über D1 an +V; Pin 34 direkt an GND.

GPIO_CHIP = 0
DEBOUNCE_SECONDS = 0.05
NEOPIXEL_SPI_HZ = 2_400_000

SWITCH_ON_CLOSED = False     # Nutzerstellung AUS: Kontakt geschlossen / LOW
