"""Just one more moment — local installation server and hardware controller."""
import argparse
from contextlib import ExitStack
import json
import logging
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import signal
import threading
from urllib.parse import urlsplit, parse_qs

from camera_preview import CameraPreview
from cloud_config import load_config
from cloud_model import OpenAIModel
from life_runtime import Installation
from model import LocalModel, SimulatedModel
from network_setup import NetworkSetup
from startup import StartupScene, claim_boot

WEB = Path(__file__).resolve().parent / 'web'
log = logging.getLogger(__name__)


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, app, startup=None):
        self.app = app
        self.startup = startup or StartupScene()
        self.shutdown_requested = threading.Event()
        self.sim_pressed = False
        self.camera = CameraPreview(simulate=app.simulate)
        super().__init__(address, Handler)

    def snapshot(self):
        return dict(self.app.snapshot(), startup=self.startup.snapshot())

    def update_camera(self):
        with self.app.lock:
            view = self.app.camera_scope()
        self.camera.update(view)

    def server_close(self):
        self.camera.close()
        super().server_close()


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, *_):
        pass  # No content, browser requests or conversation data in operating logs.

    def _valid_host(self):
        host = self.headers.get('Host', '')
        port = self.server.server_port
        return host in (f'127.0.0.1:{port}', f'localhost:{port}')

    def _headers(self, code, content_type, length=None):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        if length is not None:
            self.send_header('Content-Length', str(length))
        self.end_headers()

    def _json(self, value, code=200):
        data = json.dumps(value, ensure_ascii=False).encode()
        try:
            self._headers(code, 'application/json; charset=utf-8', len(data))
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass  # Reloads may close a heartbeat request before its reply.

    def do_GET(self):
        if not self._valid_host():
            self._json({'error': 'Invalid host'}, 403)
            return
        path = urlsplit(self.path).path
        if path == '/api/state':
            self._json(self.server.snapshot())
        elif path == '/api/health':
            self._json({'ready': True, 'simulate': self.server.app.simulate, 'pid': os.getpid()})
        elif path == '/api/camera':
            requested = parse_qs(urlsplit(self.path).query).get('view', [''])[0]
            with self.server.app.lock:
                if requested != self.server.app.view or not self.server.app.camera_requested():
                    self._json({'error': 'Inactive view'}, 409)
                else:
                    self._json(self.server.camera.frame(requested))
        elif path == '/api/events':
            self._headers(200, 'text/event-stream; charset=utf-8')
            try:
                while not self.server.shutdown_requested.is_set():
                    data = json.dumps(self.server.snapshot(), ensure_ascii=False)
                    self.wfile.write(f'data: {data}\n\n'.encode())
                    self.wfile.flush()
                    self.server.shutdown_requested.wait(1 / 12)
            except (BrokenPipeError, ConnectionResetError, TimeoutError):
                pass
        else:
            files = {'/': ('index.html', 'text/html; charset=utf-8'),
                     '/startup': ('startup.html', 'text/html; charset=utf-8'),
                     '/startup.js': ('startup.js', 'text/javascript; charset=utf-8'),
                     '/startup.css': ('startup.css', 'text/css; charset=utf-8'),
                     '/pointer.js': ('pointer.js', 'text/javascript; charset=utf-8'),
                     '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                     '/style.css': ('style.css', 'text/css; charset=utf-8'),
                     '/ascii.js': ('ascii.js', 'text/javascript; charset=utf-8'),
                     '/fonts/VT323-Regular.ttf': ('fonts/VT323-Regular.ttf', 'font/ttf')}
            if path not in files:
                self._json({'error': 'Not found'}, 404)
                return
            filename, mime = files[path]
            data = (WEB / filename).read_bytes()
            self._headers(200, mime, len(data))
            self.wfile.write(data)

    def do_POST(self):
        # JSON + same-origin checks prevent websites from operating local hardware.
        origin = self.headers.get('Origin')
        expected = f'http://{self.headers.get("Host", "")}'
        if (not self._valid_host() or origin not in (None, expected) or
                self.headers.get('Sec-Fetch-Site') == 'cross-site' or
                self.headers.get('Content-Type', '').split(';')[0] != 'application/json'):
            self._json({'error': 'Forbidden'}, 403)
            self.close_connection = True
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 2048:
                raise ValueError()
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError()
            path = urlsplit(self.path).path
            if path == '/api/seen':
                accepted = (not self.server.startup.snapshot()['active'] and
                    self.server.app.seen(data.get('view'), data.get('delivery'), data.get('visible', 0), data.get('milestone')))
                self._json({'accepted': accepted})
            elif path == '/api/startup':
                accepted = self.server.startup.heartbeat(data.get('token'), data.get('visible'))
                self._json(dict(self.server.startup.snapshot(), accepted=accepted))
            elif path == '/api/shutdown':
                self._json({'ok': True})
                self.server.shutdown_requested.set()
            elif path == '/api/network-preview':
                accepted = self.server.app.preview_network_setup()
                self._json({'accepted': accepted}, 200 if accepted else 409)
            elif path == '/api/simulate' and self.server.app.simulate:
                with self.server.app.lock:
                    if 'pressed' in data:
                        if type(data['pressed']) is not bool:
                            raise ValueError()
                        self.server.sim_pressed = data['pressed']
                    if 'online' in data or 'german' in data:
                        online = data.get('online', self.server.app.selected_mode == 'online')
                        german = data.get('german', self.server.app.selected_language == 'de')
                        if type(online) is not bool or type(german) is not bool:
                            raise ValueError()
                        self.server.app.switches(online, german)
                self._json({'ok': True})
            else:
                self._json({'error': 'Not found'}, 404)
        except (ValueError, TypeError):
            self._json({'error': 'Invalid request'}, 400)
            self.close_connection = True


def run(args):
    network = None if args.simulate else NetworkSetup()
    app = Installation(SimulatedModel() if args.simulate else LocalModel(), simulate=args.simulate, network=network)
    with ExitStack() as stack:
        if network:
            stack.callback(network.close)
        hardware = None
        if not args.simulate:
            from life_hardware import LifeHardware
            hardware = LifeHardware(log)
            stack.callback(hardware.close)
            app.switches(*hardware.switches())
        opening = args.preview_startup
        if args.boot_animation and not args.simulate:
            try:
                opening = claim_boot()
            except OSError:
                log.warning('Startup boot marker unavailable; continuing to the home screen.')
        startup = StartupScene(opening)
        server = Server(('127.0.0.1', args.port), app, startup)
        stack.callback(server.server_close)
        if not args.simulate:
            try:
                app.online_adapter = OpenAIModel(load_config(), server.camera.snapshot)
            except (ValueError, OSError):
                log.warning('OpenAI configuration unavailable; online intro only.')
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, lambda *_: server.shutdown_requested.set())
        app.start_worker()
        stack.callback(app.close)
        thread = threading.Thread(target=server.serve_forever, name='http-server', daemon=True)
        thread.start()
        stack.callback(server.shutdown)
        log.info('Just one more moment: http://127.0.0.1:%s (%s)', args.port,
                 'simulation' if args.simulate else 'local hardware')
        try:
            while not server.shutdown_requested.wait(.02):
                if hardware:
                    app.switches(*hardware.switches())
                app.button(hardware.pressed() if hardware else server.sim_pressed)
                app.memory_guard()
                app.tick()
                server.update_camera()
                if hardware:
                    hardware.update(*app.feedback())
        finally:
            server.shutdown_requested.set()
            if hardware:
                hardware.update({'mode': 'off'}, False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--simulate', action='store_true', help='No hardware or Ollama; show development controls')
    parser.add_argument('--boot-animation', action='store_true', help='Show the opening once per Pi boot (autostart)')
    parser.add_argument('--preview-startup', action='store_true', help='Preview the opening in simulation, without claiming this boot')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    if args.preview_startup and not args.simulate:
        parser.error('--preview-startup requires --simulate')
    if not 1 <= args.port <= 65535:
        parser.error('Port must be between 1 and 65535')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    run(args)


if __name__ == '__main__':
    main()
