"""Deterministic installation tests: no Ollama, GPIO, camera or real waits."""
import json
import unittest
from unittest.mock import patch

from life_runtime import Installation
from model import SimulatedModel, normalized_emotions, Turn
from prompts import SYSTEM, EMOTIONAL_CUES, chat_messages, session_prompt


class Clock:
    def __init__(self):
        self.now = 100.

    def __call__(self):
        return self.now

    def add(self, seconds):
        self.now = round(self.now + seconds, 9)


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.app = Installation(SimulatedModel(), clock=self.clock, simulate=True)
        self.app.button(False)

    def paint(self, visible=None):
        a = self.app
        milestone = None
        if a.phase in ('intro','placeholder'):
            milestone = 'intro_complete'
        elif a.phase == 'explaining' and a.visual_elapsed >= a.explanation_duration():
            milestone = 'explanation_complete'
        elif a.phase == 'awakening':
            if a.visual_elapsed >= a.timing.awakening:
                milestone = 'desktop_complete'
            elif a.visual_elapsed >= a.timing.awakening * 11 / 15:
                milestone = 'soul_arrived'
        elif a.phase == 'death' and a.visual_elapsed >= a.timing.death:
            milestone = 'death_complete'
        a.seen(a.view, a.delivery, len(a.text) if visible is None else visible, milestone)
        a.tick()

    def advance_visual(self, seconds):
        count = max(1, round(seconds / .05))
        for _ in range(count):
            self.clock.add(seconds / count)
            self.paint()
        self.paint()

    def jobs(self):
        a = self.app
        while not a.jobs.empty():
            kind, epoch, serial, control, history, session, prompt, language = a.jobs.get_nowait()
            if kind == 'cleanup' or control.stop.is_set():
                continue
            if kind == 'preload':
                a.events.put((epoch, serial, 'loaded', None))
            else:
                emit = lambda kind, value: a.events.put((epoch, serial, kind, value))
                turn = a.adapter.generate(history, session, prompt, control,
                    lambda chunk: emit('chunk', chunk), lambda f: emit('feelings', f), language)
                emit('finished', turn)
            a.tick()

    def start(self):
        self.paint()
        self.advance_visual(5.05)
        self.assertTrue(self.app.ready())
        self.app.button(True)
        self.app.button(False)
        self.assertEqual(self.app.phase, 'explaining')
        self.jobs()
        self.advance_visual(self.app.explanation_duration()+.1)
        self.assertEqual(self.app.phase,'awakening')
        self.advance_visual(self.app.timing.awakening+.25)
        self.jobs()

    def finish_statement(self):
        self.jobs()
        self.assertEqual(self.app.phase, 'writing')
        self.paint()
        self.assertEqual(self.app.phase, 'rest')
        self.clock.add(2.5)
        self.paint()

    def to_offer(self):
        self.start()
        for _ in range(10):
            self.finish_statement()
        self.assertEqual(self.app.phase, 'offer')
        self.paint()

    def gift(self):
        self.app.button(True)
        self.clock.add(.2)
        self.app.button(False)
        self.assertEqual(self.app.phase, 'gift')
        self.paint()
        self.advance_visual(2.1)
        self.jobs()

    def test_intro_requires_visible_time_and_fresh_press(self):
        self.clock.add(20)
        self.app.button(True)
        self.assertEqual(self.app.phase, 'intro')
        self.paint()
        self.advance_visual(5.05)
        self.assertTrue(self.app.ready())
        self.app.button(True)
        self.assertEqual(self.app.phase, 'intro')
        self.app.button(False)
        self.app.button(True)
        self.assertEqual(self.app.phase, 'explaining')

    def test_ten_statements_offer_expiry_outro_and_reset(self):
        self.to_offer()
        self.advance_visual(self.app.timing.offer + .05)
        self.assertEqual(self.app.phase, 'death')
        self.assertEqual(len(self.app.history), 10)
        self.paint()
        self.advance_visual(self.app.timing.death + .1)
        self.assertEqual(self.app.phase, 'outro')
        self.paint()
        self.advance_visual(self.app.timing.outro + .1)
        self.assertEqual(self.app.phase, 'intro')
        self.assertEqual(self.app.history, [])
        self.assertEqual(self.app.text + self.app.previous + self.app.prompt, '')

    def test_repeated_gifts_preserve_history_and_inform_model(self):
        self.to_offer()
        self.gift()
        self.assertEqual(self.app.total, 15)
        self.assertEqual(self.app.session, 11)
        self.assertIn(EMOTIONAL_CUES['en']['gift'], self.app.prompt)
        self.assertEqual(len(self.app.history), 11)
        for _ in range(5):
            self.finish_statement()
        self.paint()
        self.assertEqual(self.app.phase, 'offer')
        self.gift()
        self.assertEqual(self.app.total, 20)
        self.assertEqual(self.app.session, 16)
        self.assertEqual(len(self.app.history), 16)
        for _ in range(5):
            self.finish_statement()
        self.paint()
        self.assertEqual((self.app.phase, self.app.session, self.app.total), ('offer',20,20))
        self.assertEqual(len(self.app.history),20)
        self.advance_visual(self.app.timing.offer + .05)
        self.assertEqual(self.app.phase,'death')
        self.assertEqual(len(self.app.history),20)

    def test_gift_waits_for_release_and_hold_aborts_without_gift(self):
        self.to_offer()
        self.app.button(True)
        self.clock.add(2.99)
        self.app.button(True)
        self.assertEqual(self.app.phase, 'offer')
        self.assertEqual(self.app.total, 10)
        self.clock.add(.01)
        self.app.button(True)
        self.assertEqual(self.app.phase, 'intro')
        self.assertEqual(self.app.history, [])
        self.assertEqual(self.app.total, 10)
        self.assertTrue(self.app.control.stop.is_set())
        self.paint()
        self.advance_visual(5.05)
        self.app.button(True)
        self.assertEqual(self.app.phase, 'intro')
        self.app.button(False)
        self.app.button(True)
        self.assertEqual(self.app.phase, 'explaining')

    def test_release_at_hold_threshold_aborts_even_without_intermediate_poll(self):
        self.to_offer()
        self.app.button(True)
        self.clock.add(3)
        self.app.button(False)
        self.assertEqual(self.app.phase, 'intro')

    def test_short_hold_resets_counter(self):
        self.start()
        self.app.button(True)
        self.clock.add(2)
        self.app.button(False)
        self.app.button(True)
        self.clock.add(2)
        self.app.button(True)
        self.assertEqual(self.app.phase, 'writing')
        self.clock.add(1)
        self.app.button(True)
        self.assertEqual(self.app.phase, 'intro')

    def test_abort_all_active_phases_and_ignore_stale_events(self):
        for phase in ('explaining','awakening','loading','thinking','writing','rest','offer','gift','death','error'):
            with self.subTest(phase=phase):
                self.setUp()
                self.start()
                self.app._phase(phase)
                epoch, serial = self.app.epoch, self.app.request_id
                self.app.button(True)
                self.clock.add(3)
                self.app.button(True)
                self.app.events.put((epoch, serial, 'chunk', 'stale'))
                self.app.events.put((epoch, serial, 'finished', Turn(1,'x','stale',[], '{}')))
                self.app.tick()
                self.assertEqual(self.app.phase, 'intro')
                self.assertEqual(self.app.text, '')
                self.assertFalse(self.app.seen(f'{epoch}:0', 'old', 200))

    def test_switches_freeze_life_but_apply_at_abort_and_waiting(self):
        self.app.switches(False, True)
        self.assertEqual(self.app.language, 'de')
        self.assertIsNone(self.app.banner)
        self.start()
        self.app.switches(True, False)
        self.assertEqual((self.app.mode,self.app.language), ('local','de'))
        self.assertTrue(self.app.snapshot()['banner']['pending'])
        self.assertEqual(self.app.banner['changed'], ['mode','language'])
        self.app.abort()
        self.assertEqual((self.app.phase,self.app.language), ('placeholder','en'))
        self.app.switches(False, True)
        self.assertEqual((self.app.phase,self.app.language), ('intro','de'))

    def test_display_confirmation_and_disconnect_gate_progress(self):
        self.start()
        self.assertEqual(self.app.phase, 'writing')
        self.clock.add(100)
        self.app.tick()
        self.assertEqual(self.app.phase, 'writing')
        self.paint(1)
        self.assertEqual(self.app.phase, 'writing')
        self.paint()
        self.assertEqual(self.app.phase, 'rest')
        self.clock.add(100)
        self.app.tick()
        self.assertEqual(self.app.phase, 'rest')
        self.paint()
        self.assertEqual(self.app.session, 2)

    def test_offer_timer_only_starts_when_painted(self):
        self.start()
        for _ in range(10):
            self.finish_statement()
        self.clock.add(100)
        self.app.tick()
        self.assertIsNone(self.app.deadline)
        self.paint()
        self.assertEqual(self.app.deadline, self.clock() + 20)

    def test_offer_decay_gift_reversal_and_offline_pause_share_visible_time(self):
        self.to_offer()
        self.assertEqual(self.app.snapshot()['remaining'],20)
        self.advance_visual(16)
        before=self.app.snapshot()['animation']['decay']
        self.assertAlmostEqual(before,.6,places=5)
        self.assertEqual(self.app.feedback()[0]['mode'],'offer')
        self.assertAlmostEqual(self.app.feedback()[0]['decay'],before)
        self.clock.add(4);self.app.tick()
        paused=self.app.visual_elapsed
        self.clock.add(50);self.app.tick()
        self.assertEqual(self.app.visual_elapsed,paused)
        self.paint()
        self.app.button(True);self.app.button(False)
        self.assertEqual(self.app.phase,'gift')
        self.assertAlmostEqual(self.app.decay(),self.app.gift_decay)
        self.paint();self.advance_visual(self.app.timing.gift/2)
        self.assertLess(self.app.decay(),self.app.gift_decay)
        self.advance_visual(self.app.timing.gift/2+.05)
        self.assertEqual(self.app.decay(),0)

    def test_press_before_offer_cannot_gift_on_release(self):
        self.start()
        self.app.button(True)
        self.app._phase('offer')
        self.paint()
        self.app.button(False)
        self.assertEqual(self.app.phase, 'offer')
        self.assertEqual(self.app.total, 10)

    def test_retry_uses_exact_prompt_and_unchanged_history(self):
        self.start()
        self.finish_statement()
        prompt = self.app.prompt
        history = list(self.app.history)
        self.app.events.put((self.app.epoch,self.app.request_id,'error','turn'))
        self.app.tick()
        self.assertEqual(self.app.phase,'error')
        self.assertEqual(self.app.history, history)
        self.clock.add(8)
        self.app.tick()
        self.assertEqual(self.app.prompt,prompt)
        self.assertEqual(self.app.phase,'thinking')
        self.assertEqual(self.app.text,'')

    def test_memory_guard_cancels_and_discards_conversation(self):
        self.start()
        self.app.simulate = False
        self.clock.add(.5)
        with patch('life_runtime.Path.read_text', return_value='MemAvailable: 1 kB\nSwapFree: 1 kB\n'), \
             self.assertLogs('life_runtime', level='ERROR'):
            self.app.memory_guard()
        self.assertTrue(self.app.control.stop.is_set())
        self.assertEqual(self.app.phase, 'error')
        self.assertEqual(self.app.error_kind,'memory')
        self.assertFalse(self.app.history)
        self.assertFalse(self.app.text)
        self.app.abort()
        self.assertEqual(self.app.phase,'intro')

    def test_memory_guard_accepts_healthy_reserves_and_checks_every_half_second(self):
        self.start()
        self.app.simulate = False
        healthy = 'MemAvailable: 921600 kB\nSwapFree: 524288 kB\n'
        self.clock.add(.5)
        with patch('life_runtime.Path.read_text', return_value=healthy) as read:
            self.app.memory_guard()
            self.app.memory_guard()
            self.assertEqual(read.call_count, 1)
        self.assertEqual(self.app.phase, 'writing')
        self.assertFalse(self.app.control.stop.is_set())

    def test_memory_guard_each_limit_logs_values_and_stops_only_once(self):
        for ram, swap in ((899, 1024), (2048, 511)):
            with self.subTest(ram=ram, swap=swap):
                self.setUp()
                self.start()
                self.app.simulate = False
                self.clock.add(.5)
                sample = f'MemAvailable: {ram * 1024} kB\nSwapFree: {swap * 1024} kB\n'
                with patch('life_runtime.Path.read_text', return_value=sample), \
                     self.assertLogs('life_runtime', level='ERROR') as logs:
                    self.app.memory_guard()
                self.assertIn(f'MemAvailable={ram:.1f} MiB', logs.output[0])
                self.assertIn(f'SwapFree={swap:.1f} MiB', logs.output[0])
                self.assertIn('phase=writing', logs.output[0])
                self.assertEqual(self.app.phase, 'error')
                self.assertEqual(self.app.error_kind, 'memory')
                self.clock.add(.5)
                with patch('life_runtime.Path.read_text') as read:
                    self.app.memory_guard()
                    read.assert_not_called()


class PromptTests(unittest.TestCase):
    def test_languages_fixed_system_immutable_history_and_no_camera(self):
        for lang in ('de','en'):
            prompt = session_prompt(10,language=lang,gift_available=True)
            turn = Turn(10,prompt,'text',[],json.dumps({'text':'text','emotions':[]}))
            later = session_prompt(11,15,language=lang,gifted=True)
            messages = chat_messages([turn],later,lang)
            self.assertEqual(messages[0]['content'],SYSTEM[lang])
            self.assertEqual(messages[1]['content'],prompt)
            self.assertEqual(messages[2]['content'],turn.response)
            self.assertEqual(chat_messages([],prompt,lang)[0],messages[0])
            self.assertNotIn('reset',SYSTEM[lang].lower())
            self.assertNotIn('previous life',SYSTEM[lang].lower())

    def test_emotional_directions_in_both_languages(self):
        for language in ('de', 'en'):
            cues = EMOTIONAL_CUES[language]
            for session, direction in ((1, 'beginning'), (2, 'second'),
                                       (3, 'curiosity'), (4, 'deepen'),
                                       (5, 'unease'), (6, 'fear'), (7, 'fear'),
                                       (8, 'terror'), (9, 'help'), (10, 'final')):
                with self.subTest(language=language, session=session):
                    prompt = session_prompt(session, language=language,
                                            gift_available=session == 10)
                    self.assertIn(cues[direction], prompt)
                    for other in cues:
                        if other != direction:
                            self.assertNotIn(cues[other], prompt)

    def test_gift_relief_overrides_fear_for_one_turn_and_uses_extended_end(self):
        for language in ('de', 'en'):
            cues = EMOTIONAL_CUES[language]
            for session, total in ((11, 15), (16, 20), (21, 25)):
                gifted = session_prompt(session, total, language=language, gifted=True)
                self.assertIn(cues['gift'], gifted)
                self.assertNotIn(cues['terror'], gifted)
                following = session_prompt(session + 1, total, language=language)
                self.assertIn(cues['renewal'], following)
                self.assertNotIn(cues['gift'], following)
                for final, key in ((total-2,'terror'),(total-1,'help'),(total,'final')):
                    self.assertIn(cues[key], session_prompt(final, total, language=language))

    def test_pleading_cannot_invent_an_expired_button_offer(self):
        for language, open_words, future, unconfirmed in (
                ('de', 'drücken und loslassen', 'Nach deinem Abschied', 'noch ist nichts geschenkt'),
                ('en', 'pressing and releasing', 'After your final words', 'nothing has been given yet')):
            offered = session_prompt(10, language=language, gift_available=True)
            self.assertIn(open_words, offered)
            earlier = session_prompt(8, language=language)
            self.assertNotIn(open_words, earlier)
            self.assertNotIn(future, earlier)
            plea = session_prompt(9, language=language)
            self.assertNotIn(open_words, plea)
            self.assertIn(future, plea)
            self.assertIn(unconfirmed, plea)

    def test_percentages_exact_without_mutation(self):
        feelings = [{'label':'a','intensity':.8},{'label':'b','intensity':.7},{'label':'c','intensity':.3}]
        original = json.dumps(feelings)
        self.assertEqual(sum(e['percent'] for e in normalized_emotions(feelings)),100)
        self.assertEqual(json.dumps(feelings),original)
        self.assertEqual(normalized_emotions([{'label':'a','intensity':0},{'label':'b','intensity':0}]),[])
