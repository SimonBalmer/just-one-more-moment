"""Boot-once claiming, presence gating and isolated opening HTTP contracts."""
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.request

from life_runtime import Installation
from main import Server
from model import SimulatedModel
from startup import claim_boot, StartupScene, DURATION


class StartupTests(unittest.TestCase):
    def test_once_per_boot_including_parallel_launches(self):
        first='11111111-1111-1111-1111-111111111111'
        with tempfile.TemporaryDirectory() as directory:
            with ThreadPoolExecutor(max_workers=6) as pool:
                result=list(pool.map(lambda _:claim_boot(directory,first),range(12)))
            self.assertEqual(sum(result),1)
            self.assertFalse(claim_boot(directory,first))
            self.assertTrue(claim_boot(directory,'22222222-2222-2222-2222-222222222222'))
            self.assertEqual(len(list(Path(directory).iterdir())),1)

    def test_only_contiguous_visible_time_and_stale_tokens(self):
        now=[0.]; scene=StartupScene(True,clock=lambda:now[0])
        self.assertFalse(scene.heartbeat('stale',True))
        scene.heartbeat(scene.token,True)
        now[0]+=.2;scene.heartbeat(scene.token,True)
        self.assertAlmostEqual(scene.elapsed,.2)
        now[0]+=10;scene.heartbeat(scene.token,True)
        self.assertAlmostEqual(scene.elapsed,.2)
        now[0]+=.1;scene.heartbeat(scene.token,False)
        now[0]+=.1;scene.heartbeat(scene.token,True)
        self.assertAlmostEqual(scene.elapsed,.2)
        now[0]+=.1;scene.heartbeat(scene.token,True)
        self.assertAlmostEqual(scene.elapsed,.3)
        scene.elapsed=DURATION-.05
        now[0]+=.1;scene.heartbeat(scene.token,True)
        self.assertFalse(scene.snapshot()['active'])
        self.assertEqual(scene.elapsed,DURATION)

    def test_opening_does_not_acknowledge_intro_or_start_life(self):
        app=Installation(SimulatedModel(),simulate=True)
        scene=StartupScene(True)
        server=Server(('127.0.0.1',0),app,scene)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_port}'
        def post(path,data):
            req=urllib.request.Request(base+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req) as r:return json.load(r)
        try:
            for path in ('/startup','/startup.js','/startup.css','/pointer.js'):
                with urllib.request.urlopen(base+path) as r:self.assertEqual(r.status,200)
            result=post('/api/seen',dict(view=app.view,milestone='intro_complete'))
            self.assertFalse(result['accepted']);self.assertIsNone(app.seen_at)
            app.button(True);app.tick();app.button(False)
            self.assertEqual(app.instance,0);self.assertEqual(app.session,0)
            self.assertTrue(app.jobs.empty());self.assertIsNone(app.camera_scope())
            self.assertFalse(post('/api/startup',dict(token='stale',visible=True))['accepted'])
            self.assertTrue(post('/api/startup',dict(token=scene.token,visible=True))['accepted'])
            scene.active=False
            self.assertTrue(post('/api/seen',dict(view=app.view))['accepted'])
        finally:
            server.shutdown();server.server_close();thread.join(2)

    def test_boot_changes_preserve_kernel_root_spi_and_are_idempotent(self):
        spec=importlib.util.spec_from_file_location('boot_installer',Path(__file__).parents[1]/'install-startup-boot.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        config='[all]\ndtoverlay=spi0-1cs,no_miso\n'
        cmd='console=tty1 root=PARTUUID=abc rootwait quiet splash\n'
        changed,line=module.proposed(config,cmd)
        self.assertTrue(changed.startswith(config))
        self.assertEqual(line.split(),cmd.split()+['logo.nologo'])
        self.assertEqual(module.proposed(changed,line),(changed,line))
        with self.assertRaises(ValueError):module.proposed(config,'quiet splash')


if __name__=='__main__':unittest.main()
