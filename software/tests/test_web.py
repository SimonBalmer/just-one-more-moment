"""HTTP contracts and serial worker cancellation; all model access is simulated."""
import http.client
import json
import threading
import time
import unittest

from life_runtime import Installation
from main import Server
from model import SimulatedModel


class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Installation(SimulatedModel(),simulate=True)
        cls.server = Server(('127.0.0.1',0),cls.app)
        cls.thread = threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown_requested.set()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(2)

    def request(self,path,method='GET',data=None,headers=None):
        connection = http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=2)
        defaults = {'Content-Type':'application/json'}
        defaults.update(headers or {})
        connection.request(method,path,json.dumps(data) if data is not None else None,defaults)
        response = connection.getresponse()
        status, body, response_headers = response.status,response.read(),dict(response.getheaders())
        connection.close()
        return status,body,response_headers

    def test_assets_and_no_external_assets(self):
        for path,mime in (('/','text/html'),('/app.js','text/javascript'),('/style.css','text/css'),('/ascii.js','text/javascript'),('/fonts/VT323-Regular.ttf','font/ttf')):
            status,body,headers = self.request(path)
            self.assertEqual(status,200)
            self.assertIn(mime,headers['Content-Type'])
            self.assertEqual(headers['Cache-Control'],'no-store')
            self.assertNotIn(b'https://',body)
        self.assertEqual(self.request('/../main.py')[0],404)

    def test_same_origin_and_host_protection(self):
        self.assertEqual(self.request('/api/state',headers={'Host':'evil.example'})[0],403)
        self.assertEqual(self.request('/api/shutdown','POST',{}, {'Origin':'https://evil.example'})[0],403)
        self.assertEqual(self.request('/api/shutdown','POST',{}, {'Content-Type':'text/plain'})[0],403)
        self.assertFalse(self.server.shutdown_requested.is_set())

    def test_state_confirmation_and_stale_id(self):
        state = json.loads(self.request('/api/state')[1])
        response = self.request('/api/seen','POST',{'view':state['view'],'delivery':'','visible':0})
        self.assertTrue(json.loads(response[1])['accepted'])
        response = self.request('/api/seen','POST',{'view':'stale','visible':999})
        self.assertFalse(json.loads(response[1])['accepted'])

    def test_simulation_controls_and_validation(self):
        self.assertEqual(self.request('/api/simulate','POST',{'online':True,'german':True})[0],200)
        self.assertEqual(self.app.phase,'placeholder')
        self.assertEqual(self.app.language,'de')
        self.assertEqual(self.request('/api/simulate','POST',{'pressed':'yes'})[0],400)
        self.request('/api/simulate','POST',{'online':False,'german':False})
        self.app.simulate = False
        try:
            self.assertEqual(self.request('/api/simulate','POST',{'pressed':True})[0],404)
        finally:
            self.app.simulate = True

    def test_camera_endpoint_rejects_inactive_view(self):
        self.assertEqual(self.request('/api/camera?view=stale')[0],409)
        self.assertEqual(self.request('/api/camera?view='+self.app.view)[0],409)

    def test_sse_snapshot(self):
        connection = http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=2)
        connection.request('GET','/api/events')
        response = connection.getresponse()
        self.assertEqual(response.status,200)
        line = response.readline()
        self.assertTrue(line.startswith(b'data: '))
        self.assertIn('view',json.loads(line[6:]))
        connection.close()


class WorkerTests(unittest.TestCase):
    def test_abort_interrupts_worker_and_serializes_unload_before_next_load(self):
        calls, entered = [],threading.Event()
        class Blocking(SimulatedModel):
            def preload(self,control):
                calls.append('load')
                entered.set()
                control.stop.wait(2)
                control.check()
            def unload(self,control):
                calls.append('unload')
        app = Installation(Blocking(),simulate=True)
        app.start_worker()
        try:
            with app.lock:
                app._start()
            self.assertTrue(entered.wait(1))
            app.abort()
            deadline = time.monotonic()+1
            while 'unload' not in calls and time.monotonic()<deadline:
                time.sleep(.01)
            self.assertEqual(calls,['load','unload'])
            self.assertEqual(app.phase,'intro')
            self.assertEqual(app.text,'')
            self.assertEqual(app.history,[])
        finally:
            app.close()
        self.assertFalse(app.worker.is_alive())


class CancellationTests(unittest.TestCase):
    def test_cancel_interrupts_http10_response_after_connection_socket_detaches(self):
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        from local_runtime import RequestControl
        entered, release, finished = threading.Event(),threading.Event(),threading.Event()
        class Stalled(BaseHTTPRequestHandler):
            def log_message(self,*_):
                pass
            def do_POST(self):
                self.rfile.read(int(self.headers['Content-Length']))
                self.send_response(200)
                self.end_headers()
                self.wfile.flush()
                entered.set()
                release.wait(3)
        server = ThreadingHTTPServer(('127.0.0.1',0),Stalled)
        server.daemon_threads = True
        thread = threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        control = RequestControl()
        def read():
            try:
                with control.request(f'http://127.0.0.1:{server.server_port}/api/chat',{}) as response:
                    response.read()
            except (OSError,RuntimeError,InterruptedError):
                pass
            finally:
                finished.set()
        reader=threading.Thread(target=read,daemon=True); reader.start()
        try:
            self.assertTrue(entered.wait(1))
            control.cancel()
            self.assertTrue(finished.wait(1),'Cancellation failed to interrupt response.read()')
        finally:
            release.set(); server.shutdown(); server.server_close(); thread.join(2); reader.join(2)
