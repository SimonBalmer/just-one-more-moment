import subprocess
import threading
import unittest
from unittest.mock import Mock

from network_setup import NetworkSetup, PROFILE, SSID
from life_runtime import Installation
from model import SimulatedModel
from tests.test_lifecycle import Clock


class FakeNetwork:
    def __init__(self):
        self.state=dict(status='offline',error=None,serial=0,checked=100)
        self.calls=[]
        self.cancelled=False
    def snapshot(self):return dict(self.state)
    def request(self,connect=False,background=False):
        self.calls.append(connect)
        self.state.update(status='connecting' if connect else 'checking',serial=self.state['serial']+1)
        return self.state['serial']
    def cancel(self):self.cancelled=True
    def finish(self,online=False,error=None):self.state.update(status='online' if online else 'offline',error=error)


class NetworkTests(unittest.TestCase):
    def test_background_probe_preserves_online_and_start_awaits_same_probe(self):
        entered=threading.Event();release=threading.Event()
        def probe():
            entered.set();release.wait(2);return False
        n=NetworkSetup(probe=probe,run=Mock())
        n.state['status']='online'
        try:
            serial=n.request(background=True)
            self.assertTrue(entered.wait(1))
            self.assertEqual(n.snapshot()['status'],'online')
            self.assertIsNone(n.request(background=True))
            self.assertEqual(n.snapshot()['status'],'online')
            self.assertEqual(n.request(),serial)
            self.assertEqual(n.snapshot()['status'],'checking')
        finally:
            release.set();n.thread.join(2)
        self.assertEqual(n.snapshot()['status'],'offline')
        n.run.assert_not_called()

    def test_working_existing_network_is_never_reconfigured(self):
        run=Mock();n=NetworkSetup(probe=lambda:True,run=run)
        n.request(connect=True);n.thread.join(2)
        self.assertEqual(n.snapshot()['status'],'online');run.assert_not_called()

    def test_no_network_commands_for_reachability_check(self):
        run=Mock();n=NetworkSetup(probe=lambda:False,run=run)
        n.request();n.thread.join(2)
        self.assertEqual(n.snapshot()['status'],'offline');run.assert_not_called()

    def test_hotspot_failure_restores_previous_profile_without_deleting_any(self):
        calls=[]
        def run(args,**kwargs):
            calls.append(args)
            if '--active' in args:return subprocess.CompletedProcess(args,0,'old-uuid:802-11-wireless\n','')
            if '-g' in args:return subprocess.CompletedProcess(args,0,PROFILE+'\n','')
            return subprocess.CompletedProcess(args,4,'','Activation failed')
        n=NetworkSetup(probe=lambda:False,run=run)
        n.request(True);n.thread.join(2)
        self.assertEqual(n.snapshot()['error'],'connection')
        self.assertIn(['connection','up','uuid','old-uuid'],[c[3:] for c in calls])
        self.assertFalse(any('delete' in c or 'down' in c or 'modify' in c for c in calls))

    def test_new_profile_is_separate_lower_priority_and_permission_error_is_visible(self):
        calls=[]
        def run(args,**kwargs):
            calls.append(args)
            return subprocess.CompletedProcess(args,4 if 'add' in args else 0,'','Insufficient privileges')
        n=NetworkSetup(probe=lambda:False,run=run);n.request(True);n.thread.join(2)
        self.assertEqual(n.snapshot()['error'],'permission')
        create=next(c for c in calls if 'add' in c)
        self.assertIn(SSID,create);self.assertIn('-10',create);self.assertIn('connection.permissions',create)

    def test_online_waits_for_check_and_connection_never_counts_as_a_life(self):
        clock=Clock();network=FakeNetwork()
        app=Installation(SimulatedModel(),clock=clock,simulate=True,network=network)
        app.switches(True,True);app.button(False)
        def paint():app.seen(app.view,milestone='intro_complete');app.tick()
        def wait_ready():
            for _ in range(30):
                clock.add(.2);paint()
        paint();wait_ready();app.button(True);app.button(False)
        self.assertEqual(network.calls,[False]);self.assertEqual(app.instance,0)
        network.finish();app.tick();self.assertEqual(app.phase,'network')
        paint();wait_ready();app.button(True);app.button(False)
        self.assertEqual(network.calls,[False,True]);self.assertFalse(app.ready())
        network.finish(error='internet');app.tick();paint()
        self.assertEqual(app.phase,'network');self.assertEqual(app.instance,0)
        app.button(True);app.button(False);network.finish(True);network.state['checked']=clock();app.tick()
        self.assertEqual(app.phase,'placeholder');self.assertEqual(app.instance,0)
        paint();wait_ready();app.button(True);app.button(False)
        network.finish(True);app.tick()
        self.assertEqual(app.phase,'explaining');self.assertEqual(app.instance,1)

    def test_switch_to_local_cancels_pending_connection_and_ignores_late_success(self):
        n=FakeNetwork();app=Installation(SimulatedModel(),simulate=True,network=n)
        app.switches(True,False);app._phase('network');app.network_action=(1,'connect')
        app.switches(False,True);n.finish(True);app.tick()
        self.assertTrue(n.cancelled);self.assertEqual(app.phase,'intro');self.assertEqual(app.mode,'local')
        self.assertEqual(app.instance,0)

    def test_network_page_language_changes_immediately(self):
        app=Installation(SimulatedModel(),simulate=True,network=FakeNetwork())
        app.switches(True,False);app._phase('network');app.switches(True,True)
        self.assertEqual((app.phase,app.language),('network','de'));self.assertIsNone(app.banner)

    def test_manual_preview_never_attempts_wifi_even_when_internet_is_offline(self):
        n=FakeNetwork();clock=Clock();a=Installation(SimulatedModel(),simulate=True,network=n,clock=clock)
        def settle():
            for _ in range(12):
                a.seen(a.view);clock.add(.2);a.tick()
        self.assertFalse(a.preview_network_setup())
        a.switches(True,False);a.button(False)
        self.assertTrue(a.preview_network_setup())
        a.switches(True,True)
        self.assertTrue(a.network_preview)
        settle();a.seen(a.view);a.button(True);a.button(False)
        self.assertEqual(n.calls,[False])
        n.finish();a.tick();self.assertEqual(a.phase,'network')
        a.seen(a.view);a.button(True);a.button(False)
        self.assertEqual(n.calls,[False,False])
        n.finish(True);a.tick()
        self.assertEqual(a.phase,'placeholder');self.assertFalse(a.network_preview)
        self.assertEqual(a.instance,0)
        a._phase('thinking');self.assertFalse(a.preview_network_setup())

    def test_network_transition_uses_visible_time_and_reverses_without_jump(self):
        clock=Clock();a=Installation(SimulatedModel(),clock=clock,simulate=True,network=FakeNetwork())
        a.switches(True,False);a.preview_network_setup();a.seen(a.view)
        clock.add(.6);a.tick()
        self.assertAlmostEqual(a.network_blend,1/3)
        a.switches(False,False)
        self.assertAlmostEqual(a.network_blend,1/3)
        a.seen(a.view);clock.add(.3);a.tick()
        self.assertAlmostEqual(a.network_blend,1/6)
        clock.add(4);a.tick();paused=a.network_blend
        clock.add(20);a.tick();self.assertEqual(a.network_blend,paused)
        self.assertEqual(a.instance,0)


if __name__=='__main__':unittest.main()
