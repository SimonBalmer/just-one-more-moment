"""Camera frames stay in memory and simulation never opens a USB device."""
import base64
import unittest
from unittest.mock import patch
from camera_preview import CameraPreview, WIDTH, HEIGHT


class CameraTests(unittest.TestCase):
    def test_simulation_is_bounded_and_erases_frames_on_stop(self):
        camera=CameraPreview(simulate=True)
        with patch('camera_preview.subprocess.Popen',side_effect=AssertionError('Hardware access')):
            camera.update('view-1')
            frame=camera.frame('view-1')
            self.assertEqual(frame['status'],'simulation')
            self.assertEqual(len(base64.b64decode(frame['pixels'])),WIDTH*HEIGHT)
            self.assertEqual(camera.frame('stale')['status'],'off')
            camera.update(None)
            self.assertIsNone(camera.pixels)
            self.assertEqual(camera.frame('view-1')['status'],'off')

    def test_missing_usb_device_reports_unavailable_without_inference(self):
        camera=CameraPreview()
        with patch('camera_preview.Path.glob',return_value=[]), patch('camera_preview.Path.exists',return_value=False):
            camera.update('view-2')
        self.assertEqual(camera.frame('view-2')['status'],'unavailable')
        self.assertIsNone(camera.frame('view-2')['pixels'])
        camera.close()
