"""Hardware feedback with fake GPIO and SPI."""
from contextlib import contextmanager
import unittest
from unittest.mock import Mock, patch
import hardware_pins as pins
import life_hardware
from life_runtime import Installation
from model import SimulatedModel

def light(mode="alive", **values):
    return dict(mode=mode, time=10., breath=.5, energy=1., progress=0., **values)



@contextmanager
def device(value):
    yield value


class HardwareTests(unittest.TestCase):
    def test_switch_mapping_led_and_eleven_pixels(self):
        inputs = (Mock(is_pressed=False), Mock(is_pressed=True), Mock(is_pressed=False))
        led, pixels = Mock(), Mock()
        with patch.object(life_hardware,'open_inputs',return_value=device(inputs)), \
             patch.object(life_hardware,'open_button_led',return_value=device(led)), \
             patch.object(life_hardware,'NeoPixels',return_value=device(pixels)):
            hardware = life_hardware.LifeHardware(Mock())
        self.assertEqual(hardware.switches(),(False,True))
        hardware.update(light(),True)
        self.assertTrue(led.value)
        self.assertEqual(len(pixels.write.call_args.args[0]),11)
        self.assertTrue(all(r > 0 and g == b == 0 for r,g,b in pixels.write.call_args.args[0]))
        with patch.object(life_hardware.time,'monotonic',return_value=hardware.last_frame+1):
            hardware.update({'mode':'off'},False)
        self.assertEqual(pixels.write.call_args.args[0],[(0,0,0)]*pins.NEOPIXEL_COUNT)
        self.assertFalse(led.value)
        hardware.close()

    def test_missing_spi_preserves_inputs(self):
        @contextmanager
        def missing():
            raise FileNotFoundError()
            yield
        with patch.object(life_hardware,'open_inputs',return_value=device((Mock(),Mock(),Mock()))), \
             patch.object(life_hardware,'open_button_led',return_value=device(Mock())), \
             patch.object(life_hardware,'NeoPixels',return_value=missing()):
            hardware = life_hardware.LifeHardware(Mock())
        self.assertIsNone(hardware.pixels)
        hardware.update({'mode':'off'})
        hardware.close()

    def test_hold_led_accelerates_and_overrides_offer(self):
        current = [100.]
        app = Installation(SimulatedModel(),clock=lambda:current[0],simulate=True)
        app._phase('offer')
        app.press_started = current[0]
        transitions = []
        prior = app.feedback()[1]
        for i in range(1,300):
            current[0] = 100+i/100
            led = app.feedback()[1]
            if led != prior:
                transitions.append(i/100)
            prior = led
        early = sum(t < 1 for t in transitions)
        late = sum(t > 2 for t in transitions)
        self.assertGreater(late,early*2)
