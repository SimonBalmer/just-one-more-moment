"""Presentation milestones, shared light and interruption without devices."""
import unittest
from unittest.mock import patch

from life_runtime import Installation
from life_hardware import pixel_frame, FAILURE_ORDER
from model import SimulatedModel
from tests.test_lifecycle import Clock


class PresentationTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.app = Installation(SimulatedModel(), clock=self.clock, simulate=True)
        self.app.button(False)

    def paint(self, marker=None, visible=0):
        a = self.app
        return a.seen(a.view, a.delivery, visible, marker)

    def elapse(self, seconds, marker=None):
        steps = max(1, round(seconds / .05))
        for _ in range(steps):
            self.clock.add(seconds / steps)
            self.paint(marker)
            self.app.tick()

    def begin(self):
        self.paint('intro_complete')
        self.elapse(5.1)
        self.app.button(True)
        self.app.button(False)
        self.paint()
        self.elapse(self.app.explanation_duration()+.1)
        self.paint('explanation_complete')
        self.app.tick()
        self.paint()
        return self.app.view

    def build(self):
        self.elapse(4.5)
        self.paint('soul_arrived')
        self.elapse(1.7)
        self.paint('desktop_complete')
        self.app.tick()

    def test_intro_requires_finished_explanation_and_same_blink_for_screen_and_led(self):
        self.paint()
        self.elapse(8)
        self.assertFalse(self.app.ready())
        self.assertFalse(self.app.snapshot()['button_led'])
        self.paint('intro_complete')
        self.assertTrue(self.app.ready())
        self.assertEqual(self.app.snapshot()['button_led'], self.app.feedback()[1])

    def test_fast_model_waits_for_all_birth_milestones(self):
        self.begin()
        self.app.events.put((self.app.epoch, self.app.request_id, 'loaded', None))
        self.app.tick()
        self.assertEqual(self.app.phase, 'awakening')
        self.assertTrue(self.app.model_ready)
        self.assertEqual(self.app.session, 0)
        self.build()
        self.assertEqual(self.app.phase, 'thinking')
        self.assertEqual(self.app.session, 1)
        self.assertEqual(self.app.instance, 1)

    def test_slow_model_leaves_built_desktop_breathing_without_new_request(self):
        self.begin()
        serial = self.app.request_id
        self.build()
        self.assertEqual(self.app.phase, 'loading')
        self.paint()
        self.elapse(20)
        self.assertEqual(self.app.request_id, serial)
        self.assertEqual(self.app.feedback()[0]['mode'], 'alive')
        self.assertTrue(self.app.desktop_built)
        self.app.events.put((self.app.epoch, serial, 'loaded', None))
        self.app.tick()
        self.assertEqual(self.app.phase, 'thinking')

    def test_soul_must_be_shown_before_any_light_and_desktop_cannot_skip_it(self):
        self.begin()
        self.paint('soul_arrived')
        self.paint('desktop_complete')
        self.assertEqual(self.app.feedback()[0]['mode'], 'off')
        self.elapse(10)
        self.assertAlmostEqual(self.app.visual_elapsed, 4.4)
        self.assertFalse(self.app.desktop_built)
        self.assertEqual(self.app.feedback()[0]['mode'], 'off')
        self.paint('soul_arrived')
        self.assertEqual(self.app.feedback()[0]['mode'], 'birth')
        self.assertEqual(pixel_frame(self.app.feedback()[0]), [(0,0,0)]*11)
        self.elapse(.5)
        self.assertTrue(any(r for r,g,b in pixel_frame(self.app.feedback()[0])))

    def test_disconnect_does_not_catch_up_or_duplicate_model_load(self):
        self.begin()
        self.elapse(.5)
        request = self.app.request_id
        self.clock.add(100)
        self.app.tick()
        paused = self.app.visual_elapsed
        self.assertLess(paused, 3)
        self.clock.add(100)
        self.paint()
        self.assertEqual(self.app.visual_elapsed, paused)
        self.app.tick()
        self.assertEqual(self.app.request_id, request)
        self.elapse(.5)
        self.assertGreater(self.app.visual_elapsed, paused)

    def test_preload_error_retries_without_counting_a_second_instance(self):
        self.begin()
        self.app.events.put((self.app.epoch, self.app.request_id, 'error', 'preload'))
        self.app.tick()
        self.assertEqual(self.app.phase, 'error')
        self.assertEqual(self.app.feedback()[0]['mode'], 'off')
        serial = self.app.request_id
        self.clock.add(8)
        self.app.tick()
        self.assertEqual(self.app.phase, 'awakening')
        self.assertGreater(self.app.request_id, serial)
        self.assertEqual(self.app.instance, 1)
        self.assertFalse(self.app.desktop_built)

    def test_transcript_excludes_current_statement_and_reset_removes_it(self):
        from model import Turn
        self.begin()
        self.app.session = 2
        self.app.history = [Turn(1, 'old prompt', 'First memory.', [], '{}'),
                            Turn(2, 'current prompt', 'Current words.', [], '{}')]
        self.app.text = 'Current words.'
        snapshot = self.app.snapshot()
        self.assertEqual(snapshot['transcript'], [{'session':1, 'text':'First memory.'}])
        self.assertNotIn('prompt', str(snapshot['transcript']))
        self.app.abort()
        self.assertEqual(self.app.snapshot()['transcript'], [])
        self.assertEqual(self.app.snapshot()['text'], '')

    def test_death_requires_rendered_end_and_light_extinguishes_before_message(self):
        self.begin()
        self.app._phase('death')
        self.paint('death_complete')
        self.assertEqual(self.app.phase, 'death')
        self.elapse(self.app.timing.death + .1)
        self.assertEqual(self.app.phase, 'death')
        self.assertEqual(pixel_frame(self.app.feedback()[0]), [(0,0,0)]*11)
        self.paint('death_complete')
        self.app.tick()
        self.assertEqual(self.app.phase, 'outro')
        self.assertEqual(self.app.instance, 1)
        self.paint()
        self.elapse(self.app.timing.outro + .1)
        self.assertEqual(self.app.phase, 'intro')
        self.assertEqual(self.app.feedback()[0]['mode'], 'off')

    def test_ascii_return_preserves_only_decorative_time_and_survives_switches(self):
        self.begin()
        self.app._phase('death');self.paint()
        self.elapse(self.app.timing.death+.05)
        self.paint('death_complete');self.app.tick()
        self.assertEqual(self.app.phase,'outro')
        cycle=self.app.cycle_time
        self.paint();self.elapse(self.app.timing.outro+.05)
        self.assertEqual(self.app.phase,'intro')
        self.assertTrue(self.app.returning)
        self.assertGreater(self.app.cycle_time,cycle)
        self.assertFalse(self.app.history)
        self.paint();self.elapse(1)
        progress=self.app.snapshot()['animation']['return_progress']
        self.assertGreater(progress,.2);self.assertLess(progress,.4)
        self.app.switches(True,True)
        self.assertAlmostEqual(self.app.snapshot()['animation']['return_progress'],progress)
        self.paint();self.elapse(3.1)
        self.assertFalse(self.app.returning)
        self.assertEqual(self.app.snapshot()['animation']['return_progress'],1)
        self.assertEqual(self.app.instance,1)
        self.assertEqual(self.app.phase, 'placeholder')
        self.assertEqual(self.app.feedback()[0]['mode'], 'off')

    def test_gift_restores_energy_and_future_budget_fades_only_to_seventy_percent(self):
        self.begin()
        self.app.session = 10
        self.app._phase('offer')
        self.paint()
        self.app.tick()
        before = self.app.feedback()[0]['energy']
        self.app.button(True)
        self.clock.add(.1)
        self.app.button(False)
        self.assertEqual(self.app.phase, 'gift')
        self.assertGreater(self.app.feedback()[0]['energy'], before)
        self.assertEqual(self.app.feedback()[0]['energy'], 1)
        self.app.session = self.app.total
        self.assertAlmostEqual(self.app.feedback()[0]['energy'], .7)

    def test_abort_invalidates_animation_markers_and_instance_counts_only_starts(self):
        old = self.begin()
        self.app.abort()
        self.assertFalse(self.app.seen(old, milestone='soul_arrived'))
        self.assertEqual(self.app.feedback()[0]['mode'], 'off')
        self.assertEqual(self.app.instance, 1)
        self.begin()
        self.assertEqual(self.app.instance, 2)


class PixelTests(unittest.TestCase):
    def frame(self, mode='alive', **values):
        defaults = dict(mode=mode, time=5., breath=.5, energy=1., progress=.5)
        defaults.update(values)
        return pixel_frame(defaults)

    def test_continuous_breathing_and_soft_white_shimmer(self):
        alive, writing = self.frame(), self.frame('writing')
        self.assertEqual([r for r,g,b in alive], [r for r,g,b in writing])
        self.assertTrue(all(g==b==0 for r,g,b in alive))
        self.assertTrue(all(0<=g<=4 and g==b for r,g,b in writing))
        self.assertNotEqual(self.frame(breath=0),self.frame(breath=1))
        self.assertEqual(self.frame(),self.frame())

    def test_birth_death_gift_and_visibility_floor(self):
        self.assertEqual(self.frame('birth',progress=0),[(0,0,0)]*11)
        self.assertEqual(self.frame('death',progress=1),[(0,0,0)]*11)
        self.assertTrue(all(r>=13 for r,g,b in self.frame(energy=.7,breath=0)))
        self.assertGreater(sum(r for r,g,b in self.frame('gift')),sum(r for r,g,b in self.frame()))


class PixelShutdownTests(unittest.TestCase):
    def test_gift_rebuilds_same_scattered_pixels_and_death_starts_with_remaining_three(self):
        def frame(mode,decay):
            return pixel_frame(dict(mode=mode,time=2.,breath=.5,energy=1.,progress=0.,decay=decay))
        dying=frame('offer',.75)
        self.assertEqual(sum(rgb==(0,0,0) for rgb in dying),8)
        self.assertEqual([i for i,rgb in enumerate(dying) if rgb!=(0,0,0)],[2,5,10])
        self.assertEqual([rgb==(0,0,0) for rgb in dying],[rgb==(0,0,0) for rgb in frame('gift',.75)])
        self.assertTrue(all(r>0 for r,g,b in frame('gift',0)))
        self.assertEqual(frame('death',1),[(0,0,0)]*11)

    def test_offer_disperses_failures_then_death_finishes_last_three(self):
        counts = []
        for p in (.0, .2, .4, .6, .8, 1.):
            frame = pixel_frame(dict(mode='offer', time=2., breath=.5, energy=1., progress=p))
            counts.append(sum(r == 0 for r,g,b in frame))
        self.assertEqual(counts[0],0)
        self.assertEqual(counts[-1],8)
        self.assertEqual(counts,sorted(counts))
        middle = pixel_frame(dict(mode='death',time=2.,breath=.5,energy=1.,progress=.5))
        self.assertTrue(any(r==0 for r,g,b in middle))
        self.assertTrue(any(r>20 for r,g,b in middle))

    def test_completed_pixels_remain_off_while_survivors_flicker(self):
        for t in (1., 1.1, 1.2, 1.3):
            frame = pixel_frame(dict(mode='death',time=t,breath=.5,energy=1.,progress=.5))
            self.assertTrue(all(frame[i]==(0,0,0) for i in FAILURE_ORDER[:9]))
            self.assertTrue(any(frame[i]!=(0,0,0) for i in FAILURE_ORDER[9:]))


class PixelEmberTests(unittest.TestCase):
    def test_every_pixel_turns_white_before_permanent_black(self):
        for rank,index in enumerate(FAILURE_ORDER):
            threshold=(rank+.85)/11
            def frame(decay,t=2.):
                return pixel_frame(dict(mode='death',time=t,breath=.5,energy=1.,progress=0.,decay=decay))[index]
            self.assertEqual(frame(max(0,threshold-.07))[1:],(0,0))
            flashes=[frame(threshold-.005,t/20) for t in range(20)]
            self.assertTrue(any(g>4 and g==b for r,g,b in flashes))
            self.assertEqual(frame(threshold),(0,0,0))

    def test_breath_has_clearer_range_without_exceeding_red_limit(self):
        low = pixel_frame(dict(mode='alive',time=2.,breath=0.,energy=1.,progress=0.))
        high = pixel_frame(dict(mode='alive',time=2.,breath=1.,energy=1.,progress=0.))
        self.assertTrue(all(b[0]-a[0]>=27 for a,b in zip(low,high)))
        self.assertTrue(all(0<r<=60 and g==b==0 for r,g,b in low+high))


class IntroWarmupTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.app = Installation(SimulatedModel(), clock=self.clock, simulate=True)
        self.app.worker = True  # Queue-only fixture, no real worker or model.

    def warm(self):
        self.app.seen(self.app.view)
        self.app.tick()
        return self.app.jobs.get_nowait()

    def test_visible_intro_loads_once_without_life_or_prompt(self):
        job = self.warm()
        self.assertEqual(job[0], 'warmup')
        self.assertEqual(job[4:7], ([], 0, ''))
        self.app.tick()
        self.assertTrue(self.app.jobs.empty())
        self.assertEqual((self.app.instance, self.app.session, self.app.history), (0, 0, []))
        self.assertEqual(self.app.feedback()[0]['mode'], 'off')

    def test_start_adopts_inflight_load_and_accepts_completion_after_epoch_change(self):
        job = self.warm()
        self.app._start()
        self.assertIs(self.app.control, job[3])
        self.assertTrue(self.app.jobs.empty())
        self.app.events.put((job[1], job[2], 'loaded', None))
        self.app.tick()
        self.assertTrue(self.app.model_ready)
        self.assertEqual(self.app.phase, 'explaining')
        self.assertEqual(self.app.session, 0)

    def test_completed_warmup_survives_language_change_and_start_without_reload(self):
        job = self.warm()
        self.app.events.put((job[1],job[2],'loaded',None))
        self.app.tick()
        self.app.switches(False,True)
        self.app._start()
        self.assertTrue(self.app.model_ready)
        self.assertTrue(self.app.jobs.empty())
        self.assertEqual(self.app.language,'de')

    def test_online_switch_cancels_warmup_and_ignores_late_completion(self):
        job = self.warm()
        self.app.switches(True,False)
        self.assertTrue(job[3].stop.is_set())
        self.app.events.put((job[1],job[2],'loaded',None))
        self.app.tick()
        self.assertFalse(self.app.model_ready)
        self.assertEqual(self.app.phase,'placeholder')
        self.assertEqual(self.app.jobs.get_nowait()[0], 'cleanup')
        self.app.seen(self.app.view); self.app.tick()
        self.assertTrue(self.app.jobs.empty())

    def test_failed_warmup_retries_later_without_interrupting_intro(self):
        job = self.warm()
        self.app.events.put((job[1],job[2],'error','warmup'))
        self.app.tick()
        self.assertEqual(self.app.phase,'intro')
        self.assertTrue(self.app.jobs.empty())
        self.clock.add(self.app.timing.retry+.1)
        self.app.seen(self.app.view);self.app.tick()
        self.assertEqual(self.app.jobs.get_nowait()[0],'warmup')

    def test_abort_discards_warmup_even_if_late_result_arrives(self):
        job = self.warm()
        self.app._start();self.app.abort()
        self.app.events.put((job[1],job[2],'loaded',None))
        self.app.tick()
        self.assertFalse(self.app.model_ready)
        self.assertFalse(self.app.history)

    def test_intro_warmup_keeps_memory_guard_and_does_not_retry_under_pressure(self):
        job = self.warm()
        self.app.simulate = False
        self.clock.add(.6)
        with patch('life_runtime.Path.read_text', return_value='MemAvailable: 800000 kB\nSwapFree: 1000000 kB\n'):
            with self.assertLogs('life_runtime',level='ERROR'):
                self.app.memory_guard()
        self.assertTrue(job[3].stop.is_set())
        self.assertEqual(self.app.phase,'intro')
        self.assertFalse(self.app.model_ready)
        self.assertEqual(self.app.warm_retry,float('inf'))
        self.assertEqual(self.app.jobs.get_nowait()[0],'cleanup')
        self.app.seen(self.app.view);self.app.tick()
        self.assertTrue(self.app.jobs.empty())


class ExplanationTests(unittest.TestCase):
    setUp = PresentationTests.setUp
    paint = PresentationTests.paint
    elapse = PresentationTests.elapse
    def test_explanation_needs_visible_time_confirmation_and_stays_dark(self):
        self.app._start()
        self.paint('explanation_complete')
        self.assertEqual(self.app.phase,'explaining')
        self.elapse(self.app.explanation_duration()+1)
        self.assertEqual(self.app.phase,'explaining')
        self.assertEqual(self.app.feedback()[0]['mode'],'off')
        self.assertEqual(self.app.session,0)
        old=self.app.view
        self.paint('explanation_complete');self.app.tick()
        self.assertEqual(self.app.phase,'awakening')
        self.assertFalse(self.app.seen(old,milestone='explanation_complete'))

    def test_abort_during_explanation_clears_started_instance(self):
        self.app._start();self.app.button(False);self.app.button(True)
        self.clock.add(3);self.app.button(True)
        self.assertEqual(self.app.phase,'intro')
        self.assertFalse(self.app.history)


class ModeTransitionTests(unittest.TestCase):
    setUp = PresentationTests.setUp
    paint = PresentationTests.paint
    elapse = PresentationTests.elapse
    def test_waiting_motion_survives_switch_and_transition_can_reverse(self):
        self.paint(); self.elapse(1)
        before = self.app.snapshot()['animation']['creature']
        self.app.switches(True,False)
        self.assertEqual(self.app.snapshot()['animation']['creature'], before)
        self.paint(); self.elapse(.45)
        blend = self.app.snapshot()['animation']['mode_blend']
        self.assertGreater(blend,0)
        self.assertLess(blend,1)
        self.app.switches(False,False)
        self.paint(); self.elapse(.15)
        self.assertLess(self.app.mode_blend,blend)
        self.assertGreater(self.app.snapshot()['animation']['creature'],before)
        self.elapse(1)
        self.assertEqual(self.app.mode_blend,0)


class OnlineIntroTests(unittest.TestCase):
    setUp = PresentationTests.setUp
    paint = PresentationTests.paint
    elapse = PresentationTests.elapse

    def begin_online(self):
        self.app.switches(True,False)
        self.paint('intro_complete');self.elapse(5.1)
        self.app.button(True);self.app.button(False)
        self.assertEqual(self.app.phase,'explaining')
        self.assertTrue(self.app.jobs.empty())

    def test_camera_needs_visible_window_and_intro_waits_before_cloud_ready(self):
        self.begin_online()
        self.paint('camera_visible')
        self.assertFalse(self.app.camera_requested())
        self.elapse(4*24/self.app.timing.intro_cps+self.app.timing.intro_pause+.1)
        self.paint('camera_visible')
        self.assertTrue(self.app.camera_requested())
        self.assertEqual(self.app.feedback()[0]['mode'],'off')
        self.elapse(7*24/self.app.timing.intro_cps+self.app.timing.intro_pause+.1)
        self.assertFalse(self.app.camera_requested())
        self.paint('explanation_complete')
        self.assertEqual(self.app.phase,'explaining')
        self.elapse(self.app.explanation_duration()+.1)
        self.paint('explanation_complete');self.app.tick()
        self.assertEqual(self.app.phase,'online_ready')
        self.assertFalse(self.app.camera_requested())
        self.assertFalse(self.app.history)
        self.assertEqual(self.app.session,0)
        self.assertTrue(self.app.jobs.empty())
        self.assertEqual(self.app.feedback()[0]['mode'],'off')

    def test_online_intro_abort_ignores_late_events_and_uses_no_local_model(self):
        self.begin_online()
        view=self.app.view
        self.app.button(True);self.clock.add(3);self.app.button(False)
        self.assertEqual(self.app.phase,'placeholder')
        self.assertFalse(self.app.seen(view,milestone='camera_visible'))
        self.assertTrue(self.app.jobs.empty())
