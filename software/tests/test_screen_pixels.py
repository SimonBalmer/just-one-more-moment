import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
from pixel_lock import acquire
from screen_pixels import palette, frame


class AmbientTests(unittest.TestCase):
    def test_palette_and_physical_groups(self):
        image = Image.new('RGB', (100, 10), 'red')
        image.paste('green', (60, 0, 90, 10))
        image.paste('blue', (90, 0, 100, 10))
        colors = palette(image)
        self.assertEqual(colors[0], (255, 0, 0))
        values = frame(colors)
        self.assertEqual(len(values), 11)
        self.assertEqual(values[:3], values[3:6])
        self.assertEqual(values[:3], values[8:11])
        self.assertEqual(values[6:8], [values[0]] * 2)

    def test_foreground_excludes_ambient_and_releases(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict('os.environ', XDG_RUNTIME_DIR=directory):
                with acquire():
                    with self.assertRaises(BlockingIOError):
                        acquire(False)
                with acquire(False):
                    pass

    def test_white_page_keeps_small_blue_accent(self):
        image = Image.new('RGB', (100, 100), 'white')
        image.paste((0, 80, 255), (0, 0, 100, 8))
        colors = palette(image)
        self.assertGreater(colors[0][2], colors[0][0] + 100)
        self.assertEqual(colors[1], (255, 255, 255))
        self.assertEqual(colors[2], colors[0])

    def test_fire_and_neutral_screens(self):
        image = Image.new('RGB', (100, 100), (12, 8, 4))
        image.paste((255, 110, 0), (0, 0, 60, 100))
        image.paste((230, 95, 0), (60, 0, 90, 100))
        colors = palette(image)
        self.assertGreater(colors[0][0], colors[0][1])
        self.assertGreater(colors[0][1], colors[0][2])
        self.assertEqual(palette(Image.new('RGB', (10, 10), 'black')), [(0, 0, 0)] * 3)
        self.assertEqual(palette(Image.new('RGB', (10, 10), 'white')), [(255, 255, 255)] * 3)

    def test_srgb_output_preserves_saturated_mixtures(self):
        from screen_pixels import led_channel
        self.assertEqual(led_channel(255), 51)
        self.assertEqual(led_channel(0), 0)
        # Orange: Grün muss gegenüber einfacher Skalierung deutlich schwächer sein.
        self.assertLess(led_channel(128), 20)
        values = frame([(255, 128, 0)] * 3)
        self.assertTrue(all(rgb == (51, 11, 0) for rgb in values))

    def test_smoothing_converges_and_preserves_group_equality(self):
        from screen_pixels import smooth
        before = frame([(0, 0, 0)] * 3)
        target = frame([(255, 80, 0), (0, 0, 255), (255, 255, 255)])
        first = smooth(before, target)
        self.assertLess(first[0][0], target[0][0])
        for _ in range(20):
            before = smooth(before, target)
        self.assertEqual(before, target)
        self.assertEqual(first[:3], first[3:6])
        self.assertEqual(first[:3], first[8:11])
