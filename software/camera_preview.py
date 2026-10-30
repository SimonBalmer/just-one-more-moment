"""Ephemeral local USB preview. No files, cloud calls, or camera access in simulation."""
import base64
from pathlib import Path
import shutil
import subprocess
import struct
import zlib
import threading
import time

WIDTH, HEIGHT = 80, 60
CAPTURE_WIDTH, CAPTURE_HEIGHT = 320, 240


def png_rgb(pixels, width=CAPTURE_WIDTH, height=CAPTURE_HEIGHT):
    if len(pixels) != width * height * 3:
        raise ValueError('Invalid RGB frame size.')
    def chunk(kind, data):
        return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
    rows=b''.join(b'\0'+pixels[y*width*3:(y+1)*width*3] for y in range(height))
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!IIBBBBB',width,height,8,2,0,0,0))+
            chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b''))


def gray_preview(rgb):
    values=[]
    for y in range(HEIGHT):
        for x in range(WIDTH):
            offset=((y*4)*CAPTURE_WIDTH+x*4)*3
            r,g,b=rgb[offset:offset+3]
            values.append((77*r+150*g+29*b)>>8)
    return bytes(values)


class CameraPreview:
    def __init__(self, *, simulate=False):
        self.simulate = simulate
        self.lock = threading.Lock()
        self.frame_ready = threading.Condition(self.lock)
        self.view = None
        self.process = self.thread = None
        self.pixels = self.rgb = None
        self.status = 'off'
        self.sequence = 0
        self.updated = 0.
        self.last_attempt = 0.

    def update(self, view):
        if view == self.view and (view is None or self.simulate or self.status != 'unavailable'
                                  or time.monotonic() - self.last_attempt < 3):
            return
        self.close()
        if view is None:
            return
        with self.lock:
            self.view, self.status = view, 'waiting'
            self.last_attempt = time.monotonic()
        if self.simulate:
            return
        devices = sorted(Path('/dev/v4l/by-id').glob('*-video-index0'))
        device = str(devices[0]) if devices else '/dev/video0'
        if not shutil.which('ffmpeg') or not Path(device).exists():
            self.status = 'unavailable'
            return
        try:
            process = subprocess.Popen([
                'ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error',
                '-threads', '1', '-f', 'v4l2', '-input_format', 'mjpeg',
                '-framerate', '5', '-video_size', '640x480', '-i', device,
                '-vf', f'fps=5,scale={CAPTURE_WIDTH}:{CAPTURE_HEIGHT},format=rgb24',
                '-threads', '1', '-f', 'rawvideo', 'pipe:1'],
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            self.process = process
            self.thread = threading.Thread(target=self._read, args=(process, view), daemon=True,
                                           name='usb-camera-preview')
            self.thread.start()
        except OSError:
            self.status = 'unavailable'

    def _read(self, process, view):
        try:
            while True:
                rgb = process.stdout.read(CAPTURE_WIDTH * CAPTURE_HEIGHT * 3)
                if len(rgb) != CAPTURE_WIDTH * CAPTURE_HEIGHT * 3:
                    break
                pixels = gray_preview(rgb)
                with self.frame_ready:
                    if self.view != view:
                        return
                    self.pixels, self.rgb = pixels, rgb
                    self.sequence += 1
                    self.updated = time.monotonic()
                    self.status = 'live'
                    self.frame_ready.notify_all()
        except (OSError, ValueError):
            pass
        finally:
            with self.lock:
                if self.view == view:
                    self.pixels = self.rgb = None
                    self.status = 'unavailable'
                    self.frame_ready.notify_all()

    def frame(self, view):
        with self.lock:
            if view != self.view:
                return dict(status='off', view=view)
            if self.simulate:
                t = int(time.monotonic() * 5)
                pixels = bytes((x * 3 + y * 2 + t * 8) % 256
                               for y in range(HEIGHT) for x in range(WIDTH))
                status = 'simulation'
            else:
                pixels = self.pixels if time.monotonic() - self.updated < 2 else None
                status = self.status if pixels or self.status != 'live' else 'unavailable'
            return dict(view=view, status=status, width=WIDTH, height=HEIGHT,
                        sequence=self.sequence,
                        pixels=base64.b64encode(pixels).decode() if pixels else None)

    def snapshot(self, control):
        """Wait for a new colour frame, never silently send an old/absent image."""
        requested=time.monotonic()
        with self.frame_ready:
            while True:
                control.check()
                if self.view is None or self.status=='unavailable':
                    raise RuntimeError('Current USB camera image unavailable.')
                if self.simulate:
                    rgb=bytes((x*3+y)%256 for y in range(CAPTURE_HEIGHT) for x in range(CAPTURE_WIDTH*3))
                    break
                if self.rgb and self.updated>=requested:
                    rgb=self.rgb
                    break
                if time.monotonic()-requested>8:
                    raise RuntimeError('Timed out waiting for a fresh camera image.')
                self.frame_ready.wait(.1)
        control.check()
        return png_rgb(rgb)

    def close(self):
        with self.frame_ready:
            self.view, self.pixels, self.rgb, self.status = None, None, None, 'off'
            self.frame_ready.notify_all()
        process, thread = self.process, self.thread
        self.process = self.thread = None
        if process:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=1)
            process.stdout.close()
        if thread:
            thread.join(timeout=1)
