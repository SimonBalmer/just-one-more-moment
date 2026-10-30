"""Opt-in real Chromium opening, refresh and handoff regression; no hardware."""
import unittest,json,time,tempfile,subprocess,threading,base64,os,signal
from pathlib import Path
from tests.test_browser import DevTools
from life_runtime import Installation
from model import SimulatedModel
from main import Server
from startup import StartupScene,DURATION

@unittest.skipUnless(os.environ.get('MOMENT_BROWSER_TEST')=='1','Opt-in Chromium test')
class StartupBrowserTests(unittest.TestCase):
    def test_opening_refresh_handoff_and_no_replay(self):
        with tempfile.TemporaryDirectory(prefix='moment-opening-shots-') as shots_dir:
            app=Installation(SimulatedModel(),simulate=True);scene=StartupScene(True)
            server=Server(('127.0.0.1',0),app,scene)
            threading.Thread(target=server.serve_forever,daemon=True).start()
            folder=Path(shots_dir)
            with tempfile.TemporaryDirectory(prefix='moment-opening-browser-') as directory:
             log=open(Path(directory)/'browser.log','w')
             browser=subprocess.Popen(['chromium','--headless','--disable-gpu','--disable-dev-shm-usage','--password-store=basic','--no-first-run','--disable-background-networking','--disable-features=OptimizationGuideOnDeviceModel','--window-size=1280,720','--remote-debugging-port=0',f'--user-data-dir={directory}',f'http://127.0.0.1:{server.server_port}/'],stdout=log,stderr=log,start_new_session=True)
             cdp=None
             def wait(expression,timeout=12):
              until=time.monotonic()+timeout
              while time.monotonic()<until:
               try:
                if cdp.evaluate(expression):return
               except Exception:pass
               time.sleep(.1)
              raise AssertionError(expression)
             try:
              marker=Path(directory)/'DevToolsActivePort'
              for _ in range(100):
               if marker.exists():break
               if browser.poll() is not None:raise RuntimeError('Chromium exited')
               time.sleep(.1)
              import urllib.request
              port=marker.read_text().splitlines()[0]
              tabs=json.load(urllib.request.urlopen('http://127.0.0.1:'+port+'/json'))
              cdp=DevTools(next(t['webSocketDebuggerUrl'] for t in tabs if t['type']=='page'))
              wait("location.pathname==='/startup' && !!window.StartupFX && !!startup")
              time.sleep(.5);before=scene.elapsed
              assert before>0 and app.seen_at is None and app.jobs.empty() and app.session==0
              cdp.call('Page.reload');wait("location.pathname==='/startup' && !!window.StartupFX && !!startup")
              assert scene.elapsed>=before
              # Draw real production scenes deterministically for inspection.
              cdp.evaluate('closing=true')
              for name,t in [('field',1.4),('hslu',3.3),('phki',5.7),('simon',8.8),('logo',15.5)]:
               cdp.evaluate(f'StartupFX.draw({t})')
               expected={'hslu':'HSLU','phki':'PHKI HS26','simon':'Simon Balmer'}.get(name,name)
               self.assertEqual(cdp.evaluate('document.body.dataset.startupStage'),expected)
               data=cdp.call('Page.captureScreenshot',{'format':'png'})['data']
               (folder/(name+'.png')).write_bytes(base64.b64decode(data))
              with scene.lock:scene.elapsed=DURATION-.05
              cdp.evaluate('closing=false; heartbeat()')
              wait("location.pathname==='/' && !!state && !state.startup.active && document.fonts.status==='loaded'")
              wait("state.ready",12)
              assert app.session==0 and app.instance==0
              cdp.call('Page.reload');wait("location.pathname==='/' && !!state && !state.startup.active")
              assert app.session==0
              self.assertFalse(scene.active)
             finally:
              if cdp:cdp.close()
              os.killpg(browser.pid,signal.SIGTERM)
              try:browser.wait(5)
              except subprocess.TimeoutExpired:os.killpg(browser.pid,signal.SIGKILL);browser.wait()
              log.close();server.shutdown();server.server_close();app.close()
