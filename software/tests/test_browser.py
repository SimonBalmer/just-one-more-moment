"""Optional real Chromium smoke test, stdlib only. MOMENT_BROWSER_TEST=1 enables it."""
import base64
from dataclasses import replace
from contextlib import ExitStack
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import struct
import subprocess
import tempfile
import threading
import time
import unittest
import urllib.request
from urllib.parse import urlsplit

from life_runtime import Installation, Timing
from main import Server
from model import SimulatedModel, Turn


class DevTools:
    """Small CDP test client. Only local Chromium's debugging WebSocket is used."""
    def __init__(self, url):
        address = urlsplit(url)
        self.socket = socket.create_connection((address.hostname,address.port),timeout=5)
        key = base64.b64encode(os.urandom(16)).decode()
        self.socket.sendall((f'GET {address.path} HTTP/1.1\r\nHost: {address.netloc}\r\n'
            f'Upgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n'
            'Sec-WebSocket-Version: 13\r\n\r\n').encode())
        header = b''
        while not header.endswith(b'\r\n\r\n'):
            header += self.socket.recv(1)
        if b' 101 ' not in header:
            raise RuntimeError(header.decode())
        self.serial = 0

    def close(self):
        self.socket.close()

    def read(self,n):
        result = b''
        while len(result)<n:
            part = self.socket.recv(n-len(result))
            if not part:
                raise EOFError()
            result += part
        return result

    def call(self, method, params=None):
        self.serial += 1
        payload = json.dumps({'id':self.serial,'method':method,'params':params or {}}).encode()
        mask = os.urandom(4)
        length = len(payload)
        header = bytes([0x81,0x80|length]) if length<126 else bytes([0x81,0xFE])+struct.pack('!H',length)
        self.socket.sendall(header+mask+bytes(b^mask[i%4] for i,b in enumerate(payload)))
        while True:
            first,second = self.read(2)
            size = second&127
            if size==126: size=struct.unpack('!H',self.read(2))[0]
            if size==127: size=struct.unpack('!Q',self.read(8))[0]
            data = self.read(size)
            if first&15 != 1:
                continue
            message = json.loads(data)
            if message.get('id')==self.serial:
                if 'error' in message:
                    raise RuntimeError(message['error'])
                return message.get('result',{})

    def evaluate(self, expression):
        result = self.call('Runtime.evaluate',{'expression':expression,'returnByValue':True,'awaitPromise':True})
        if 'exceptionDetails' in result:
            raise AssertionError(result['exceptionDetails'])
        return result.get('result',{}).get('value')


@unittest.skipUnless(os.environ.get('MOMENT_BROWSER_TEST')=='1','Opt-in Chromium test')
class BrowserTests(unittest.TestCase):
    def test_real_browser_switch_start_emotions_reconnect_gift_and_abort(self):
        browser = shutil.which('chromium')
        self.assertIsNotNone(browser)
        class ShortModel(SimulatedModel):
            def generate(self, history, session, prompt, control, on_chunk, on_emotions, language):
                feelings=[{'label':'Neugier' if language=='de' else 'Curiosity','intensity':.8},
                          {'label':'Hoffnung' if language=='de' else 'Hope','intensity':.4}]
                text='Hallo. 🙂' if language=='de' else 'Hello. 🙂'
                on_emotions(feelings); on_chunk(text)
                return Turn(session,prompt,text,feelings,json.dumps({'text':text,'emotions':feelings}))
        app = Installation(ShortModel(),simulate=True,timing=Timing(intro=.1,intro_cps=10000,intro_pause=.001,explanation_read=.8,awakening=1.2,death=.32,outro=.6,pause=.1,gift=.6))
        with ExitStack() as stack:
            app.start_worker(); stack.callback(app.close)
            server = Server(('127.0.0.1',0),app)
            stack.callback(server.server_close)
            http_thread = threading.Thread(target=server.serve_forever,daemon=True)
            http_thread.start(); stack.callback(server.shutdown)
            running = threading.Event(); running.set()
            def ticker():
                while running.is_set():
                    app.button(server.sim_pressed); app.tick(); server.update_camera(); time.sleep(.01)
            tick_thread = threading.Thread(target=ticker,daemon=True); tick_thread.start()
            stack.callback(lambda:(running.clear(),tick_thread.join(2)))
            directory=stack.enter_context(tempfile.TemporaryDirectory(prefix='moment-browser-'))
            errors=stack.enter_context(open(Path(directory)/'chromium.log','w+'))
            process=subprocess.Popen([browser,'--headless','--disable-gpu','--disable-dev-shm-usage','--password-store=basic',
                '--no-first-run','--no-default-browser-check','--disable-background-networking',
                '--disable-features=OptimizationGuideOnDeviceModel','--window-size=1280,720','--remote-debugging-port=0',
                f'--user-data-dir={directory}',f'http://127.0.0.1:{server.server_port}/'],
                stdout=errors,stderr=errors,start_new_session=True)
            def stop_browser():
                try: os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError: pass
                try: process.wait(5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL); process.wait()
                # Chromium helper processes may flush their profile after the parent exits.
                deadline = time.monotonic() + 2
                while time.monotonic() < deadline:
                    try: os.killpg(process.pid, 0)
                    except ProcessLookupError: break
                    time.sleep(.05)
                try: os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                time.sleep(.1)
            stack.callback(stop_browser)
            portfile=Path(directory)/'DevToolsActivePort'
            deadline=time.monotonic()+15
            while not portfile.exists() and time.monotonic()<deadline and process.poll() is None:
                time.sleep(.05)
            if not portfile.exists():
                errors.seek(0)
                self.fail(errors.read()[-3000:])
            port=int(portfile.read_text().splitlines()[0])
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/json/list') as response:
                pages=json.load(response)
            page=next(p for p in pages if p['type']=='page')
            cdp=DevTools(page['webSocketDebuggerUrl']); stack.callback(cdp.close)
            cdp.call('Page.navigate', {'url':f'http://127.0.0.1:{server.server_port}/'})
            cdp.call('Emulation.setDeviceMetricsOverride',{'width':1280,'height':720,'deviceScaleFactor':1,'mobile':False})
            def wait_js(expression,timeout=8):
                end=time.monotonic()+timeout
                while time.monotonic()<end:
                    try:
                        if cdp.evaluate(expression): return
                    except AssertionError:
                        pass
                    time.sleep(.05)
                self.fail('Browser condition timed out: '+expression+'; '+str(cdp.evaluate("({url:location.href,ready:document.readyState,title:document.title,body:document.body?.innerText.slice(0,300)})")))
            def review_dialogs(mode):
                gallery=Path('/tmp/moment-dialog-review');gallery.mkdir(exist_ok=True)
                with app.lock:
                    saved_timing,saved_language,saved_elapsed=app.timing,app.language,app.visual_elapsed
                    app.timing=replace(app.timing,intro_cps=18,intro_pause=4,explanation_read=5)
                for language in ('de','en'):
                    with app.lock:
                        app.language=language
                    steps=cdp.evaluate(f"copy.{language}.{'onlineSteps' if mode=='online' else 'introSteps'}")
                    elapsed=0
                    for index,step in enumerate(steps):
                        duration=app.intro_durations()[index]
                        with app.lock:
                            app.visual_elapsed=elapsed+min(1.,duration/3)
                            app.visual_updated=time.monotonic()
                        wait_js(f"introLanguage === '{language}:{mode}' && document.querySelector('.intro-pop.foremost')?.dataset.index === '{index}'")
                        if step[2]=='camera':
                            wait_js("document.getElementById('onlineCameraStatus')?.textContent.includes('SIMUL')")
                        time.sleep(.22)
                        layout=cdp.evaluate("(()=>{const n=document.querySelector('.intro-pop.foremost'),r=n.getBoundingClientRect();return {x:r.x,y:r.y,right:r.right,bottom:r.bottom,overflow:n.scrollWidth>n.clientWidth+1,children:Array.from(n.querySelectorAll('p,.titlebar,.intro-ten')).map(p=>{const b=p.getBoundingClientRect();return {x:b.x,y:b.y,right:b.right,bottom:b.bottom}})}})()")
                        self.assertGreaterEqual(layout['x'],0,(mode,language,index,layout))
                        self.assertGreaterEqual(layout['y'],0,(mode,language,index,layout))
                        self.assertLessEqual(layout['right'],1281,(mode,language,index,layout))
                        self.assertLessEqual(layout['bottom'],721,(mode,language,index,layout))
                        self.assertFalse(layout['overflow'],(mode,language,index,layout))
                        for child in layout['children']:
                            self.assertLessEqual(child['right'],layout['right']+1,(mode,language,index,layout))
                            self.assertLessEqual(child['bottom'],layout['bottom']+1,(mode,language,index,layout))
                        if mode=='online' and index==0:
                            self.assertTrue(cdp.evaluate("(()=>{const c=document.getElementById('ascii'),p=c.getContext('2d').getImageData(Math.floor(innerWidth*.6),0,Math.floor(innerWidth*.39),45).data;let n=0;for(let j=0;j<p.length;j+=4)if(p[j]>220&&p[j+1]>180&&p[j+3]>20)n++;return n>20})()"))
                        shot=cdp.call('Page.captureScreenshot',{'format':'png'})
                        (gallery/f'{mode}-{language}-{index+1}.png').write_bytes(base64.b64decode(shot['data']))
                        elapsed+=duration
                with app.lock:
                    app.timing,app.language,app.visual_elapsed=saved_timing,saved_language,saved_elapsed
                    app.visual_updated=time.monotonic()
                wait_js(f"introLanguage === '{saved_language}:{mode}'")

            wait_js("document.readyState === 'complete' && !!document.getElementById('startHint')")
            self.assertEqual(cdp.evaluate("getComputedStyle(document.body).cursor"),'none')
            cdp.call('Input.dispatchMouseEvent',{'type':'mouseMoved','x':24,'y':24})
            self.assertEqual(cdp.evaluate("getComputedStyle(document.body).cursor"),'none')
            cdp.call('Input.dispatchMouseEvent',{'type':'mouseMoved','x':48,'y':48})
            wait_js("!document.documentElement.classList.contains('cursor-idle')")
            self.assertNotEqual(cdp.evaluate("getComputedStyle(document.body).cursor"),'none')
            # Repeated stationary input (window/remote pointer updates) must not
            # extend visibility. Test real trusted Chromium input, not JS events.
            for _ in range(22):
                cdp.call('Input.dispatchMouseEvent',{'type':'mouseMoved','x':48,'y':48})
                time.sleep(.2)
            wait_js("document.documentElement.classList.contains('cursor-idle')",2)
            self.assertEqual(cdp.evaluate("getComputedStyle(document.getElementById('startChoice')).cursor"),'none')
            cdp.call('Input.dispatchMouseEvent',{'type':'mouseMoved','x':72,'y':72})
            wait_js("!document.documentElement.classList.contains('cursor-idle')")
            cdp.call('Page.reload')
            wait_js("!!state && fontsReady && document.documentElement.classList.contains('cursor-idle')")
            wait_js("state?.phase === 'intro' && state.ready && document.getElementById('startChoice').classList.contains('ready')")
            # Network setup uses fake connectivity: no radio or external request.
            from tests.test_network_setup import FakeNetwork
            with app.lock:
                app.network=FakeNetwork()
                app.switches(True,True)
                app._phase('network')
            wait_js("state.phase === 'network' && state.animation.network_blend > .35 && state.animation.network_blend < .8")
            self.assertTrue(cdp.evaluate("!document.getElementById('intro').hidden && !document.getElementById('networkSetup').hidden"))
            self.assertTrue(cdp.evaluate("getComputedStyle(document.getElementById('introFinal')).animationName === 'none' && getComputedStyle(document.querySelector('.network-dialog')).animationName === 'none'"))
            shot=cdp.call('Page.captureScreenshot',{'format':'png'})
            Path('/tmp/just-one-more-moment-network-enter.png').write_bytes(base64.b64decode(shot['data']))
            for language in ('de','en'):
                with app.lock:
                    app.switches(True,language=='de')
                wait_js(f"state.phase === 'network' && state.language === '{language}' && state.animation.network_blend > .999 && !document.getElementById('networkSetup').hidden")
                time.sleep(.3)
                self.assertTrue(cdp.evaluate("(()=>{const r=document.querySelector('.network-dialog').getBoundingClientRect();return r.top>=0 && r.bottom<=innerHeight && r.right<=innerWidth && r.left>=0})()"))
                self.assertTrue(cdp.evaluate("document.getElementById('networkChoice').getBoundingClientRect().bottom <= document.querySelector('.network-dialog').getBoundingClientRect().bottom"))
                shot=cdp.call('Page.captureScreenshot',{'format':'png'})
                Path(f'/tmp/just-one-more-moment-network-{language}.png').write_bytes(base64.b64decode(shot['data']))
            with app.lock:
                app.network=None
                app.switches(False,False)
            wait_js("state.phase === 'intro' && state.animation.network_blend > .3 && state.animation.network_blend < .8")
            self.assertTrue(cdp.evaluate("!document.getElementById('intro').hidden && !document.getElementById('networkSetup').hidden"))
            shot=cdp.call('Page.captureScreenshot',{'format':'png'})
            Path('/tmp/just-one-more-moment-network-return.png').write_bytes(base64.b64decode(shot['data']))
            wait_js("state.phase === 'intro' && state.ready")
            self.assertTrue(cdp.evaluate("['localPi','localOffline'].every(id=>!document.getElementById(id).hidden && !!document.querySelector('#'+id+' svg'))"))
            self.assertTrue(cdp.evaluate("(()=>{const p=document.getElementById('localPi').getBoundingClientRect(),o=document.getElementById('localOffline').getBoundingClientRect(),d=document.getElementById('introFinal').getBoundingClientRect();return p.left>d.right && p.top<o.top && o.bottom-p.top<370 && p.right<=innerWidth && o.left>d.right && document.getElementById('localOffline').parentElement===document.body && !!document.getElementById('localPi').closest('#dialogs') && document.querySelector('#localPiIcon svg').getAttribute('viewBox')==='0 0 32 42'})()"))
            time.sleep(.25)  # Allow the title-bar pop to finish before review.
            shot=cdp.call('Page.captureScreenshot',{'format':'png'})
            Path('/tmp/just-one-more-moment-local-badges.png').write_bytes(base64.b64decode(shot['data']))
            self.assertEqual(cdp.evaluate("document.querySelectorAll('.intro-pop').length"),6)
            self.assertEqual(cdp.evaluate("document.querySelectorAll('.intro-pop:not([hidden])').length"),0)
            self.assertTrue(cdp.evaluate("!!document.querySelector('#introLogo svg')"))
            self.assertIsNone(cdp.evaluate("document.getElementById('arcadeHint')"))
            self.assertIsNone(cdp.evaluate("document.getElementById('holdHint')"))
            self.assertIsNone(cdp.evaluate("document.getElementById('language')"))
            self.assertEqual(cdp.evaluate('document.documentElement.lang'),'en')
            cdp.evaluate("document.getElementById('devGerman').click()")
            wait_js("document.documentElement.lang === 'de'")
            self.assertEqual(cdp.evaluate("document.getElementById('startLanguageValue').textContent"),'DEUTSCH')
            self.assertTrue(cdp.evaluate("document.getElementById('notice').hidden && document.getElementById('noticeBackdrop').hidden"))
            cdp.evaluate("document.getElementById('devOnline').click()")
            wait_js("state?.phase === 'placeholder' && !document.getElementById('intro').hidden")
            self.assertTrue(cdp.evaluate("document.getElementById('startModeValue').textContent.includes('ONLINE')"))
            self.assertEqual(cdp.evaluate("document.getElementById('startChoice').getAttribute('aria-disabled')"),'false')
            self.assertTrue(cdp.evaluate("document.getElementById('notice').hidden"))
            self.assertTrue(cdp.evaluate("!document.getElementById('cameraPlacement').hidden && !!document.querySelector('#cameraPlacementArt svg')"))
            self.assertTrue(cdp.evaluate("!document.getElementById('onlineWifi').hidden && !!document.querySelector('#onlineWifi svg')"))
            self.assertIn('Monitor',cdp.evaluate("document.getElementById('cameraPlacementText').textContent"))
            wait_js("state.animation.mode_blend > .999")
            self.assertTrue(cdp.evaluate("document.getElementById('localPi').hidden && document.getElementById('localOffline').hidden"))
            time.sleep(.2)
            shot=cdp.call('Page.captureScreenshot',{'format':'png'})
            Path('/tmp/just-one-more-moment-online-start.png').write_bytes(base64.b64decode(shot['data']))
            self.assertTrue(cdp.evaluate("(()=>{const d=document.getElementById('introFinal').getBoundingClientRect(),m=document.getElementById('startSettings').getBoundingClientRect(),w=document.getElementById('onlineWifi').getBoundingClientRect(),c=document.getElementById('cameraPlacement').getBoundingClientRect();return Math.abs(d.top-w.top)<1 && Math.abs(m.bottom-c.bottom)<1 && Math.abs(d.left-(innerWidth-c.right))<1})()"))
            self.assertIsNone(cdp.evaluate("document.getElementById('cameraPlacementTitle')"))
            with app.lock:
                app.timing = replace(app.timing, intro_cps=120, intro_pause=.05, explanation_read=.4)
            cdp.evaluate("post('/api/simulate',{pressed:true})")
            time.sleep(.08)
            cdp.evaluate("post('/api/simulate',{pressed:false})")
            wait_js("state?.phase === 'explaining' && state.mode === 'online'")
            wait_js("document.getElementById('onlineCameraStatus')?.textContent.includes('SIMULIERTE')",8)
            time.sleep(.3)
            shot=cdp.call('Page.captureScreenshot',{'format':'png'})
            Path('/tmp/just-one-more-moment-online-camera.png').write_bytes(base64.b64decode(shot['data']))
            review_dialogs('online')
            wait_js("state?.phase === 'online_ready'",10)
            self.assertEqual(app.instance,1)
            self.assertEqual(app.session,0)
            self.assertFalse(app.history)
            self.assertFalse(app.camera_requested())
            with app.lock:
                app.abort()
                app.timing = replace(app.timing, intro_cps=10000, intro_pause=.001, explanation_read=.8)
            wait_js("state?.phase === 'placeholder'")
            # Explicit fake cloud configuration exercises the full online lifecycle
            # in the real browser without a key, hardware or external API call.
            class ConfiguredOnline(ShortModel):
                configured=True
            with app.lock:
                app.online_adapter=ConfiguredOnline()
            wait_js("state.cloud_configured && state.ready")
            cdp.evaluate("post('/api/simulate',{pressed:true})")
            time.sleep(.08)
            cdp.evaluate("post('/api/simulate',{pressed:false})")
            wait_js("state.mode === 'online' && document.getElementById('statement').textContent.includes('🙂')",10)
            self.assertIn('API',cdp.evaluate("document.getElementById('camera').textContent"))
            self.assertTrue(app.camera_requested())
            shot=cdp.call('Page.captureScreenshot',{'format':'png'})
            Path('/tmp/just-one-more-moment-online-desktop.png').write_bytes(base64.b64decode(shot['data']))
            with app.lock:
                app.abort()
                app.online_adapter=None
            wait_js("state?.phase === 'placeholder' && !state.cloud_configured")
            cdp.evaluate("document.getElementById('devOnline').click()")
            wait_js("state?.phase === 'intro' && state.animation.mode_blend > .01 && state.animation.mode_blend < .99")
            self.assertTrue(cdp.evaluate("!document.getElementById('cameraPlacement').hidden"))
            shot=cdp.call('Page.captureScreenshot',{'format':'png'})
            Path('/tmp/just-one-more-moment-mode-transition.png').write_bytes(base64.b64decode(shot['data']))
            wait_js("state?.phase === 'intro' && state.ready && document.getElementById('startChoice').classList.contains('ready')")
            self.assertTrue(cdp.evaluate("document.getElementById('cameraPlacement').hidden && document.getElementById('onlineWifi').hidden"))
            with app.lock:
                app.banner = None
            # Real keyboard events exercise the browser control's own handlers.
            cdp.evaluate("document.getElementById('devButton').dispatchEvent(new KeyboardEvent('keydown',{key:'Enter'}))")
            time.sleep(.08)
            cdp.evaluate("document.getElementById('devButton').dispatchEvent(new KeyboardEvent('keyup',{key:'Enter'}))")
            wait_js("state?.phase === 'explaining'")
            review_dialogs('local')
            wait_js("state?.phase === 'explaining' && state.animation.elapsed > .3")
            self.assertEqual(cdp.evaluate("document.querySelectorAll('.intro-pop:not([hidden])').length"),6)
            self.assertIn('Du hast gerade',cdp.evaluate("document.querySelector('.intro-model').textContent"))
            self.assertEqual(app.feedback()[0]['mode'],'off')
            shot=cdp.call('Page.captureScreenshot',{'format':'png'})
            Path('/tmp/just-one-more-moment-explaining.png').write_bytes(base64.b64decode(shot['data']))
            wait_js("state?.phase === 'awakening' && state.animation.elapsed / state.animation.duration > .3")
            self.assertTrue(cdp.evaluate("(() => { const c=document.getElementById('ascii'); const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data; for(let i=0;i<d.length;i+=4) if(d[i]>150 && d[i+3]>50) return true; return false; })()"))
            shot = cdp.call('Page.captureScreenshot', {'format':'png'})
            Path('/tmp/just-one-more-moment-flight.png').write_bytes(base64.b64decode(shot['data']))
            cdp.call('Page.reload')
            wait_js("document.getElementById('statement').textContent.includes('🙂')")
            self.assertIn('Neugier',cdp.evaluate("document.getElementById('emotions').textContent"))
            with app.lock:
                app._phase('rest'); app.deadline = time.monotonic() + 120
            wait_js("document.body.classList.contains('rest')")
            # A silent/stale SSE connection must recover without a page reload,
            # a new life or duplicate model work.
            with app.lock:
                before = (app.epoch, app.instance, app.session, len(app.history))
            cdp.evaluate("window.stalledSource = events; events.close()")
            wait_js("!document.getElementById('connection').hidden")
            wait_js("events !== window.stalledSource && document.getElementById('connection').hidden")
            with app.lock:
                self.assertEqual((app.epoch, app.instance, app.session, len(app.history)), before)
            with app.lock:
                app.banner = None
            wait_js("document.getElementById('notice').hidden")
            screenshot=cdp.call('Page.captureScreenshot',{'format':'png'})
            Path('/tmp/just-one-more-moment-desktop.png').write_bytes(base64.b64decode(screenshot['data']))
            self.assertEqual(cdp.evaluate("parseFloat(getComputedStyle(document.getElementById('currentEntry')).fontSize)"),56)
            self.assertGreaterEqual(cdp.evaluate("parseFloat(getComputedStyle(document.querySelector('.emotion-label')).fontSize)"),18)
            cdp.call('Emulation.setDeviceMetricsOverride',{'width':390,'height':844,'deviceScaleFactor':1,'mobile':False})
            time.sleep(.15)
            bounds=cdp.evaluate("Array.from(document.querySelectorAll('#terminalWindow,#feelingsWindow')).map(n=>{const r=n.getBoundingClientRect();return {x:r.x,y:r.y,right:r.right,bottom:r.bottom}})")
            for bound in bounds:
                self.assertGreaterEqual(bound['x'],0)
                self.assertLessEqual(bound['right'],391)
                self.assertLessEqual(bound['bottom'],845)
            screenshot=cdp.call('Page.captureScreenshot',{'format':'png'})
            Path('/tmp/just-one-more-moment-mobile.png').write_bytes(base64.b64decode(screenshot['data']))
            cdp.call('Emulation.setDeviceMetricsOverride',{'width':1280,'height':720,'deviceScaleFactor':1,'mobile':False})
            # Long text and maximum-length labels must remain inside the small landscape display.
            with app.lock:
                saved_text, saved_feelings = app.text, app.feelings
                app.text = ('Ein weiterer Moment. ' * 30)[:600]
                app.visible = len(app.text)
                app.feelings = [{'label':'Verletzliche Dankbarkeit','intensity':.5},
                                {'label':'Wachsende Ungewissheit','intensity':.3},
                                {'label':'Unerwartete Zuversicht','intensity':.2}]
                app.delivery += ':layout'
            cdp.call('Emulation.setDeviceMetricsOverride',{'width':800,'height':600,'deviceScaleFactor':1,'mobile':False})
            wait_js("document.querySelectorAll('.emotion').length === 3")
            bounds=cdp.evaluate("Array.from(document.querySelectorAll('#terminalWindow,#feelingsWindow')).map(n=>{const r=n.getBoundingClientRect();return {x:r.x,y:r.y,right:r.right,bottom:r.bottom}})")
            for bound in bounds:
                self.assertGreaterEqual(bound['y'],0)
                self.assertLessEqual(bound['right'],801)
                self.assertLessEqual(bound['bottom'],601)
            self.assertTrue(cdp.evaluate("document.getElementById('terminalScroll').scrollTop > 0"))
            self.assertLessEqual(cdp.evaluate("(()=>{const n=document.getElementById('terminalScroll');return n.scrollHeight-n.scrollTop-n.clientHeight})()"),1)
            with app.lock:
                app.text, app.feelings = saved_text, saved_feelings
                app.visible = len(app.text)
                app.delivery += ':restored'
            cdp.call('Emulation.setDeviceMetricsOverride',{'width':1280,'height':720,'deviceScaleFactor':1,'mobile':False})
            # Reload preserves the life, budget and visible Unicode text.
            epoch=app.epoch
            cdp.call('Page.reload')
            wait_js("document.getElementById('statement').textContent.includes('🙂')")
            self.assertEqual(app.epoch,epoch)
            # Reach an offer without waiting through eight real-time statements.
            with app.lock:
                app.session=10; app._phase('offer')
            wait_js("!document.getElementById('offer').hidden")
            self.assertEqual(cdp.evaluate("document.getElementById('offerText').textContent"),'Schenke dem Modell noch etwas Sprechzeit.')
            self.assertEqual(cdp.evaluate("document.getElementById('offerQuestion').textContent"),'Ein weiterer Moment?')
            self.assertEqual(cdp.evaluate("getComputedStyle(document.body,'::after').zIndex"),'4')
            self.assertGreaterEqual(cdp.evaluate("parseFloat(getComputedStyle(document.getElementById('offerQuestion')).fontSize)"),40)
            time.sleep(.25)  # Let the retro window-open animation finish before visual review.
            screenshot=cdp.call('Page.captureScreenshot',{'format':'png'})
            Path('/tmp/just-one-more-moment-offer.png').write_bytes(base64.b64decode(screenshot['data']))
            with app.lock:
                app.visual_elapsed=14
                app.visual_updated=time.monotonic()
            wait_js("state.animation.decay > .5 && state.phase === 'offer'")
            time.sleep(.2)
            self.assertEqual(cdp.evaluate("document.getElementById('offerQuestion').textContent"),'Ein weiterer Moment?')
            screenshot=cdp.call('Page.captureScreenshot',{'format':'png'})
            Path('/tmp/just-one-more-moment-offer-decay.png').write_bytes(base64.b64decode(screenshot['data']))
            self.assertTrue(cdp.evaluate("(()=>{const r=document.getElementById('offer').getBoundingClientRect(),p=document.getElementById('ascii').getContext('2d').getImageData(Math.ceil(r.x+10),Math.ceil(r.y+10),20,20).data;return Array.from(p).every(v=>v===0)})()"))
            self.assertTrue(cdp.evaluate("(()=>{const r=document.getElementById('offer').getBoundingClientRect();return r.top>=0 && r.bottom<=innerHeight && r.right<=innerWidth})()"))
            self.assertEqual(cdp.evaluate("document.getElementById('ascii').style.opacity"),'')
            drawing=cdp.evaluate("(()=>{const c=document.getElementById('ascii').getContext('2d'),fill=c.fillRect,write=c.fillText,boxes=[],letters=[];try{c.fillRect=function(...a){boxes.push(this.fillStyle);return fill.apply(this,a)};c.fillText=function(...a){letters.push(a[0]);return write.apply(this,a)};fx.draw(state)}finally{c.fillRect=fill;c.fillText=write}return {boxes,letters}})()")
            self.assertTrue(drawing['letters'])
            self.assertTrue(all(color=='#000000' for color in drawing['boxes']))
            deadline=time.monotonic()+3
            while app.deadline is None and time.monotonic()<deadline: time.sleep(.02)
            cdp.evaluate("document.getElementById('devButton').dispatchEvent(new KeyboardEvent('keydown',{key:'Enter'}))")
            time.sleep(.1)
            self.assertEqual(app.total,10)
            cdp.evaluate("document.getElementById('devButton').dispatchEvent(new KeyboardEvent('keyup',{key:'Enter'}))")
            wait_js("!document.getElementById('gift').hidden")
            self.assertEqual(app.total,15)
            self.assertGreater(app.gift_decay,.5)
            wait_js("document.getElementById('gift').hidden")
            wait_js("document.querySelectorAll('.entry').length > 0")
            self.assertTrue(cdp.evaluate("getComputedStyle(document.querySelector('.entry')).fontSize === getComputedStyle(document.getElementById('currentEntry')).fontSize"))
            self.assertEqual(cdp.evaluate("document.querySelectorAll('.entry-label').length"),0)
            # Exercise the rendered collapse and termination dialog using a short fixture.
            with app.lock:
                app.timing = replace(app.timing, death=1.2, outro=1.5)
                app._phase('death')
            wait_js("document.body.classList.contains('death')")
            wait_js("(()=>{const c=document.getElementById('ascii');const p=c.getContext('2d').getImageData(0,0,c.width,c.height).data;for(let i=0;i<p.length;i+=16){if(p[i]>50 && p[i+1]<100 && p[i+3]>0)return true;}return false;})()")
            self.assertEqual(cdp.evaluate("getComputedStyle(document.getElementById('desktop')).opacity"),'1')
            wait_js("!document.getElementById('outro').hidden")
            self.assertEqual(cdp.evaluate("document.getElementById('outroTitle').textContent"),'INSTANZ BEENDET.')
            self.assertIn('LOKALEN INSTANZDATEN',cdp.evaluate("document.getElementById('outroNote').textContent"))
            wait_js("(()=>{const c=document.getElementById('ascii'),p=c.getContext('2d').getImageData(0,0,c.width,c.height).data;for(let i=0;i<p.length;i+=4)if(p[i]>180&&p[i+1]>180&&p[i+3]>10)return true;return false})()")
            screenshot=cdp.call('Page.captureScreenshot',{'format':'png'})
            Path('/tmp/just-one-more-moment-ascii-outro.png').write_bytes(base64.b64decode(screenshot['data']))
            wait_js("!document.getElementById('intro').hidden")
            wait_js("state.animation.returning && state.animation.return_progress > .1")
            progress=cdp.evaluate('state.animation.return_progress')
            cdp.call('Page.reload')
            wait_js(f"!!state && fontsReady && state.animation.return_progress >= {progress}")
            self.assertEqual(app.instance,3)
            screenshot=cdp.call('Page.captureScreenshot',{'format':'png'})
            Path('/tmp/just-one-more-moment-ascii-return.png').write_bytes(base64.b64decode(screenshot['data']))
            self.assertFalse(app.history)
            self.assertEqual(cdp.evaluate("document.getElementById('transcript').textContent"),'')
            wait_js("state?.phase === 'intro' && state.ready && document.getElementById('startChoice').classList.contains('ready')")
            cdp.evaluate("document.getElementById('devButton').dispatchEvent(new KeyboardEvent('keydown',{key:'Enter'}))")
            time.sleep(.06)
            cdp.evaluate("document.getElementById('devButton').dispatchEvent(new KeyboardEvent('keyup',{key:'Enter'}))")
            wait_js("document.getElementById('statement').textContent.includes('🙂')")
            self.assertEqual(app.instance,4)
            # Pending language changes stay frozen until the abort.
            cdp.evaluate("document.getElementById('devGerman').click()")
            wait_js("!document.getElementById('notice').hidden")
            self.assertIn('NÄCHSTEN LEBEN',cdp.evaluate("document.getElementById('noticeText').textContent"))
            self.assertTrue(cdp.evaluate("document.getElementById('noticeLanguageRow').classList.contains('changed')"))
            self.assertFalse(cdp.evaluate("document.getElementById('noticeModeRow').classList.contains('changed')"))
            self.assertEqual(cdp.evaluate("getComputedStyle(document.getElementById('noticeBackdrop')).zIndex"),'3')
            time.sleep(.25)
            shot=cdp.call('Page.captureScreenshot',{'format':'png'})
            Path('/tmp/just-one-more-moment-switch.png').write_bytes(base64.b64decode(shot['data']))
            self.assertEqual(app.language,'de')
            cdp.evaluate("document.getElementById('devButton').dispatchEvent(new KeyboardEvent('keydown',{key:'Enter'}))")
            wait_js("!document.getElementById('hold').hidden")
            wait_js("!document.getElementById('intro').hidden",5)
            self.assertFalse(app.history)
            self.assertEqual(app.language,'en')
            # Still held: no new life starts, even once the intro is ready.
            wait_js("state?.phase === 'intro' && state.ready && document.getElementById('startChoice').classList.contains('ready')")
            self.assertEqual(app.phase,'intro')
            cdp.evaluate("document.getElementById('devButton').dispatchEvent(new KeyboardEvent('keyup',{key:'Enter'}))")
            # Screenshot retained only as local QA artifact.
            with app.lock:
                app.banner = None
            wait_js("document.getElementById('notice').hidden")
            time.sleep(.6)
            screenshot=cdp.call('Page.captureScreenshot',{'format':'png'})
            Path('/tmp/just-one-more-moment-browser.png').write_bytes(base64.b64decode(screenshot['data']))
            cdp.call('Emulation.setDeviceMetricsOverride',{'width':390,'height':844,'deviceScaleFactor':1,'mobile':False})
            time.sleep(.2)
            self.assertTrue(cdp.evaluate("(()=>{const r=document.getElementById('introFinal').getBoundingClientRect();return r.x>=0 && r.right<=390 && r.bottom<=844})()"))
            shot=cdp.call('Page.captureScreenshot',{'format':'png'})
            Path('/tmp/just-one-more-moment-start-mobile.png').write_bytes(base64.b64decode(shot['data']))
            cdp.evaluate("document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))")
            deadline=time.monotonic()+2
            while not server.shutdown_requested.is_set() and time.monotonic()<deadline: time.sleep(.02)
            self.assertTrue(server.shutdown_requested.is_set())
