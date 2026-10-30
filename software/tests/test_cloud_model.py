"""OpenAI preparation tested with fake credentials, fake frames and fake SSE only."""
import base64
from contextlib import contextmanager
import io
import json
import os
import runpy
import sys
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock, patch

from camera_preview import CameraPreview, png_rgb, gray_preview
from cloud_config import CloudConfig, load_config
from cloud_model import OpenAIModel
from life_runtime import Installation
from local_runtime import RequestControl
from model import SimulatedModel, Turn
from prompts import ONLINE_SYSTEM
from tests import test_lifecycle as lifecycle_tests


def stream(text='Ich bin noch hier.', complete=True):
    raw=json.dumps({'emotions':[{'label':'Freude','intensity':.8},{'label':'Neugier','intensity':.2}], 'text':text},ensure_ascii=False)
    packets=[{'type':'response.output_text.delta','delta':raw[:50]},
             {'type':'response.output_text.delta','delta':raw[50:]}]
    if complete: packets.append({'type':'response.completed','response':{'status':'completed'}})
    return io.BytesIO(b''.join(('data: '+json.dumps(p)+'\n\n').encode() for p in packets))


class FakeControl(RequestControl):
    def __init__(self, complete=True):
        super().__init__();self.calls=[];self.complete=complete
    @contextmanager
    def openai_request(self,payload,api_key,timeout=120):
        self.check();self.calls.append((json.loads(json.dumps(payload)),api_key));yield stream(complete=self.complete)


class CloudTests(unittest.TestCase):
    def test_opt_in_config_has_private_permissions_and_hidden_secret_repr(self):
        self.assertFalse(CloudConfig(api_key='fake-key',model='gpt-4.1').configured)
        self.assertNotIn('fake-key',repr(CloudConfig(True,'gpt-4.1','fake-key')))
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'openai.json'
            self.assertFalse(load_config(path).configured)
            path.write_text(json.dumps({'enabled':True,'model':'gpt-4.1','api_key':'fake-key'}))
            path.chmod(0o644)
            with self.assertRaises(ValueError):load_config(path)
            path.chmod(0o600)
            self.assertTrue(load_config(path).configured)

    def test_external_secret_file_and_old_inline_format_both_work(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);path=root/'openai.json';secret=root/'openai.key'
            secret.write_text('fake-secret-file-key\n');secret.chmod(0o600)
            path.write_text(json.dumps({'enabled':True,'model':'gpt-6.1-terra',
                'api_key_file':'openai.key','reasoning_effort':'none','temperature':1.,'max_output_tokens':1024}))
            path.chmod(0o600)
            config=load_config(path)
            self.assertTrue(config.configured)
            self.assertEqual(config.api_key,'fake-secret-file-key')
            self.assertNotIn('fake-secret-file-key',repr(config))
            secret.chmod(0o644)
            with self.assertRaises(ValueError):load_config(path)
            path.write_text(json.dumps({'enabled':False,'model':'gpt-6.1-terra','api_key_file':'missing'}))
            self.assertFalse(load_config(path).configured)

    def test_local_setup_stores_secret_separately_without_network(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'openai.json'
            script=runpy.run_path('configure-openai.py')
            with patch.dict(os.environ,{'MOMENT_OPENAI_CONFIG':str(path)}), \
                 patch.object(sys,'argv',['configure-openai.py']), \
                 patch('getpass.getpass',return_value='fake-setup-key'), \
                 patch('builtins.print'):
                script['main']()
            data=json.loads(path.read_text())
            self.assertEqual(data['model'],'gpt-6.1-terra')
            self.assertEqual(data['reasoning_effort'],'none')
            self.assertNotIn('fake-setup-key',path.read_text())
            self.assertNotIn('api_key',data)
            self.assertEqual(path.stat().st_mode&0o077,0)
            self.assertEqual(Path(data['api_key_file']).stat().st_mode&0o077,0)
            self.assertEqual(load_config(path).api_key,'fake-setup-key')

    def test_current_model_profile_preserves_parameter_compatibility(self):
        config=CloudConfig(True,'gpt-6.1-terra','fake-key','none',1024,1.)
        adapter=OpenAIModel(config,lambda _:b'png');control=FakeControl()
        adapter.generate([],1,'p',control,Mock(),Mock(),'de')
        payload=control.calls[0][0]
        self.assertEqual(payload['reasoning'],{'effort':'none'})
        self.assertEqual(payload['temperature'],1.)
        self.assertEqual(payload['max_output_tokens'],1024)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'config.json';path.write_text(json.dumps({
                'model':'gpt-6.1-terra','reasoning_effort':'low','temperature':1.}))
            path.chmod(0o600)
            with self.assertRaises(ValueError):load_config(path)

    def test_current_image_each_call_and_history_is_text_only_immutable(self):
        images=iter([png_rgb(bytes([20,40,60])*4,2,2),png_rgb(bytes([70,80,90])*4,2,2)])
        adapter=OpenAIModel(CloudConfig(True,'gpt-4.1','fake-key'),lambda _:next(images))
        history=[Turn(1,'Original prompt','Original text',[],'{"text":"Original text","emotions":[]}')]
        before=repr(history)
        controls=[]
        for _ in range(2):
            c=FakeControl();controls.append(c)
            result=adapter.generate(history,2,'Exact next prompt',c,Mock(),Mock(),'de')
            self.assertEqual(result.text,'Ich bin noch hier.')
            payload,key=c.calls[0]
            self.assertFalse(payload['store'])
            self.assertEqual(payload['instructions'],ONLINE_SYSTEM['de'])
            self.assertTrue(payload['text']['format']['strict'])
            self.assertEqual(payload['input'][0]['content'],'Original prompt')
            self.assertEqual(payload['input'][1]['content'],history[0].response)
            self.assertEqual(payload['input'][-1]['content'][0]['text'],'Exact next prompt')
            self.assertEqual(len([x for x in payload['input'] if isinstance(x['content'],list)]),1)
            self.assertNotIn('previous_response_id',payload)
            self.assertNotIn('fake-key',json.dumps(payload))
        self.assertNotEqual(controls[0].calls[0][0]['input'][-1]['content'][1],controls[1].calls[0][0]['input'][-1]['content'][1])
        self.assertEqual(repr(history),before)

    def test_stream_completion_is_required_and_no_text_when_camera_missing(self):
        adapter=OpenAIModel(CloudConfig(True,'gpt-4.1','fake-key'),lambda _:b'png')
        with self.assertRaises(RuntimeError):adapter.generate([],1,'p',FakeControl(False),Mock(),Mock(),'en')
        c=FakeControl()
        adapter.frame_provider=Mock(side_effect=RuntimeError('No current frame'))
        with self.assertRaises(RuntimeError):adapter.generate([],1,'p',c,Mock(),Mock(),'en')
        self.assertFalse(c.calls)

    def test_https_has_fixed_destination_and_sanitizes_error_body(self):
        connection=Mock();connection.sock=Mock()
        response=Mock(status=401);response.read.return_value=b'private upstream detail'
        connection.getresponse.return_value=response
        with patch('local_runtime.http.client.HTTPSConnection',return_value=connection) as factory:
            with self.assertRaises(RuntimeError) as caught:
                with RequestControl().openai_request({},'fake-key'):pass
        factory.assert_called_once_with('api.openai.com',443,timeout=5)
        self.assertNotIn('private',str(caught.exception))
        self.assertNotIn('fake-key',str(caught.exception))
        with self.assertRaises(ValueError):
            with RequestControl().request('https://api.openai.com/v1/responses',{}):pass

    def test_https_request_can_be_interrupted_without_exposing_key(self):
        connection=Mock();connection.sock=Mock()
        response=Mock(status=200);connection.getresponse.return_value=response
        control=RequestControl()
        with patch('local_runtime.http.client.HTTPSConnection',return_value=connection):
            with control.openai_request({},'fake-key'):
                control.cancel()
                connection.sock.shutdown.assert_called_once()
        self.assertIsNone(control.active_socket)
        connection.close.assert_called_once()

    def test_disabled_cloud_never_requests_a_camera_image(self):
        image=Mock(side_effect=AssertionError('Should not capture'))
        adapter=OpenAIModel(CloudConfig(),image)
        with self.assertRaises(RuntimeError):adapter.generate([],1,'p',FakeControl(),Mock(),Mock(),'de')
        image.assert_not_called()
        self.assertNotIn('Du hast keine Kamera',ONLINE_SYSTEM['de'])
        self.assertNotIn('You have no camera',ONLINE_SYSTEM['en'])

    def test_old_frame_is_not_reused_for_an_api_call(self):
        camera=CameraPreview();camera.view='view';camera.status='live'
        camera.rgb=bytes([1,2,3])*320*240;camera.updated=time.monotonic()-10
        control=RequestControl();entered=threading.Event();done=threading.Event();result=[]
        original_check=control.check
        def check():entered.set();original_check()
        control.check=check
        def capture():
            try:result.append(camera.snapshot(control))
            finally:done.set()
        thread=threading.Thread(target=capture);thread.start()
        self.assertTrue(entered.wait(1))
        self.assertFalse(done.is_set())
        fresh=bytes([4,5,6])*320*240
        with camera.frame_ready:
            camera.rgb=fresh;camera.updated=time.monotonic();camera.frame_ready.notify_all()
        thread.join(1)
        self.assertTrue(done.is_set())
        self.assertEqual(result[0],png_rgb(fresh))
        camera.close()

    def test_snapshot_is_png_and_closing_clears_both_buffers(self):
        camera=CameraPreview(simulate=True);camera.update('view')
        frame=camera.snapshot(RequestControl())
        self.assertTrue(frame.startswith(b'\x89PNG\r\n\x1a\n'))
        camera.close()
        self.assertIsNone(camera.rgb)
        self.assertIsNone(camera.pixels)
        with self.assertRaises(RuntimeError):camera.snapshot(RequestControl())
        self.assertEqual(len(gray_preview(bytes([255,0,0])*320*240)),80*60)

    def test_waiting_for_fresh_colour_frame_is_cancelled(self):
        camera=CameraPreview();camera.view='view';camera.status='waiting'
        control=RequestControl();finished=threading.Event()
        def wait():
            try:camera.snapshot(control)
            except InterruptedError:finished.set()
        thread=threading.Thread(target=wait);thread.start()
        control.cancel();thread.join(1)
        self.assertTrue(finished.is_set())
        camera.close()


class OnlineLifeTests(unittest.TestCase):
    paint=lifecycle_tests.LifecycleTests.paint
    advance_visual=lifecycle_tests.LifecycleTests.advance_visual
    start=lifecycle_tests.LifecycleTests.start
    finish_statement=lifecycle_tests.LifecycleTests.finish_statement
    to_offer=lifecycle_tests.LifecycleTests.to_offer
    gift=lifecycle_tests.LifecycleTests.gift

    def setUp(self):
        self.clock=lifecycle_tests.Clock()
        class Online(SimulatedModel):
            configured=True
        class NeverLocal(SimulatedModel):
            def preload(self,_):raise AssertionError('Unexpected local load')
            def generate(self,*_):raise AssertionError('Unexpected local inference')
        self.app=Installation(NeverLocal(),online_adapter=Online(),clock=self.clock,simulate=True)
        self.app.switches(True,False);self.app.button(False)

    def jobs(self):
        a=self.app
        while not a.jobs.empty():
            kind,epoch,serial,control,history,session,prompt,language=a.jobs.get_nowait()
            if control.stop.is_set():continue
            self.assertTrue(kind.startswith('online_'))
            if kind=='online_preload':a.events.put((epoch,serial,'loaded',None))
            else:
                turn=a.online_adapter.generate(history,session,prompt,control,
                    lambda text:a.events.put((epoch,serial,'chunk',text)),
                    lambda feelings:a.events.put((epoch,serial,'feelings',feelings)),language)
                a.events.put((epoch,serial,'finished',turn))
            a.tick()

    def test_full_online_life_ten_plus_five_then_death_and_reset(self):
        self.to_offer()
        self.assertEqual(self.app.session,10)
        self.gift()
        self.assertEqual((self.app.session,self.app.total),(11,15))
        for _ in range(5):self.finish_statement()
        self.paint();self.advance_visual(self.app.timing.offer+.05)
        self.assertEqual(self.app.phase,'death')
        self.advance_visual(self.app.timing.death+.1)
        self.advance_visual(self.app.timing.outro+.1)
        self.assertEqual(self.app.phase,'placeholder')
        self.assertFalse(self.app.history)
        self.assertFalse(self.app.camera_requested())

    def test_camera_survives_phase_change_but_stops_on_browser_disconnect(self):
        a=self.app
        a._phase('awakening')
        a.seen(a.view)
        scope=a.camera_scope()
        self.assertIsNotNone(scope)
        for phase in ('loading','thinking','writing','rest','offer','gift','error'):
            a._phase(phase)
            self.assertEqual(a.camera_scope(),scope)
        self.clock.add(a.timing.presence+.01)
        self.assertIsNone(a.camera_scope())
        a.seen(a.view)
        self.assertEqual(a.camera_scope(),scope)
        a._phase('death')
        self.assertIsNone(a.camera_scope())

    def test_online_retry_uses_same_prompt_and_abort_clears_everything(self):
        self.start()
        prompt=self.app.prompt
        self.app.events.put((self.app.epoch,self.app.request_id,'error','turn'))
        self.paint();self.clock.add(self.app.timing.retry+.1);self.paint()
        self.assertEqual(self.app.prompt,prompt)
        old=self.app.view
        self.app.abort()
        self.assertFalse(self.app.seen(old,visible=600))
        self.assertFalse(self.app.history)
        self.assertTrue(self.app.control.stop.is_set())
