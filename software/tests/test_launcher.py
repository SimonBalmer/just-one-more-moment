"""Kiosk orchestration with a fake browser and explicit simulated backend."""
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time
import unittest
import urllib.request


class LauncherTests(unittest.TestCase):
    def test_ready_singleton_and_shutdown_with_simulated_backend(self):
        try:
            with socket.socket() as probe:
                probe.bind(('127.0.0.1',8765))
        except OSError:
            self.skipTest('Default port in use; do not disturb an existing installation')
        with tempfile.TemporaryDirectory(prefix='moment-launcher-') as directory:
            root=Path(directory)
            browser=root/'chromium'
            browser.write_text('#!/usr/bin/python3\nimport os,signal,sys,time\nfrom pathlib import Path\nPath(os.environ["FAKE_BROWSER_ARGS"]).write_text("\\n".join(sys.argv))\nsignal.signal(signal.SIGTERM,lambda *_:sys.exit(0))\nwhile True: time.sleep(.1)\n')
            browser.chmod(0o755)
            env=dict(os.environ,PATH=f'{root}:{os.environ["PATH"]}',XDG_STATE_HOME=str(root/'state'),FAKE_BROWSER_ARGS=str(root/'args'))
            process=subprocess.Popen(['bash','start-installation.sh','--simulate'],env=env,
                                     stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                end=time.monotonic()+10
                while not (root/'args').exists() and process.poll() is None and time.monotonic()<end:
                    time.sleep(.05)
                self.assertTrue((root/'args').exists(),'Launcher did not reach browser startup')
                args=(root/'args').read_text()
                self.assertIn('--kiosk',args)
                self.assertIn('--disable-features=OptimizationGuideOnDeviceModel,Translate',args)
                self.assertIn('--disable-extensions',args)
                self.assertIn('--renderer-process-limit=2',args)
                self.assertIn('--app=http://127.0.0.1:8765/',args)
                with urllib.request.urlopen('http://127.0.0.1:8765/api/health',timeout=2) as response:
                    self.assertTrue(json.load(response)['simulate'])
                duplicate=subprocess.run(['bash','start-installation.sh','--simulate'],env=env,timeout=3,capture_output=True)
                self.assertEqual(duplicate.returncode,0)
                self.assertIsNone(process.poll())
                request=urllib.request.Request('http://127.0.0.1:8765/api/shutdown',data=b'{}',headers={'Content-Type':'application/json'})
                with urllib.request.urlopen(request,timeout=2) as response:
                    self.assertEqual(response.status,200)
                process.wait(10)
                self.assertEqual(process.returncode,0)
                # A browser that exits immediately must also stop its backend;
                # it must not leave the launcher waiting forever on the other child.
                browser.write_text('#!/usr/bin/python3\nraise SystemExit(0)\n')
                quick = subprocess.run(['bash','start-installation.sh','--simulate'],
                                       env=env, timeout=10, capture_output=True)
                self.assertEqual(quick.returncode, 0)
                with socket.socket() as probe:
                    self.assertNotEqual(probe.connect_ex(('127.0.0.1',8765)), 0)
            finally:
                if process.poll() is None:
                    process.terminate()
                    try: process.wait(10)
                    except subprocess.TimeoutExpired: process.kill(); process.wait()
                process.communicate()
