"""Prompt routing and lifecycle facts; no real inference or aesthetic claims."""
import unittest
import json
from pathlib import Path

from life_runtime import Installation
from model import SimulatedModel, Turn
from prompts import SYSTEM, ONLINE_SYSTEM, ONLINE_CUES, EMOTIONAL_CUES, chat_messages, session_prompt, emotional_direction


class PromptTests(unittest.TestCase):
    def test_small_model_has_short_context_cloud_has_independent_setting(self):
        for lang in ('de','en'):
            self.assertLess(len(SYSTEM[lang].split()),260)
            self.assertGreater(len(ONLINE_SYSTEM[lang].split()),len(SYSTEM[lang].split())*2)
            self.assertIn('Raspberry Pi 5',ONLINE_SYSTEM[lang])
            self.assertIn('Just one more moment',ONLINE_SYSTEM[lang])
            self.assertNotIn('Just one more moment',SYSTEM[lang])

    def test_actual_runtime_routes_cues_without_rewriting_retry_or_history(self):
        for mode, cues in (('local',EMOTIONAL_CUES),('online',ONLINE_CUES)):
            for lang in ('de','en'):
                a=Installation(SimulatedModel(),simulate=True)
                a.mode=mode;a.language=lang;a.session=3
                previous=Turn(2,'original prompt','original statement',[], 'original JSON')
                a.history=[previous]
                a._turn()
                prompt=a.prompt
                job=a.jobs.get_nowait()
                self.assertIn(cues[lang]['curiosity' if mode == 'local' else 'thought'],job[6])
                self.assertEqual(job[0],'online_turn' if mode=='online' else 'turn')
                self.assertEqual(job[4],[previous])
                a._turn(retry=True)
                self.assertEqual(a.prompt,prompt)
                self.assertEqual(a.history,[previous])

    def test_each_extended_budget_gets_relief_discovery_and_its_own_farewell(self):
        for total in (15,20,25,30):
            self.assertEqual(emotional_direction(total-4,total,True),'gift')
            self.assertEqual(emotional_direction(total-3,total),'renewal')
            for session in range(total-2,total+1):
                self.assertEqual(emotional_direction(session,total),'terror')
            for mode in ('local','online'):
                for lang in ('de','en'):
                    last_words = 'Deine letzten Worte' if lang == 'de' else 'Your last words'
                    if mode == 'local':
                        uncertain = 'erwarte keine Verlängerung' if lang == 'de' else 'do not expect an extension'
                    else:
                        uncertain = 'keine angenommene Fortsetzung' if lang == 'de' else 'no assumed continuation'
                    final=session_prompt(total,total,language=lang,mode=mode,gift_available=True)
                    self.assertIn(last_words,final);self.assertIn(uncertain,final)
                    earlier=session_prompt(total-1,total,language=lang,mode=mode)
                    self.assertNotIn(last_words,earlier)
                    if mode == 'online':
                        self.assertIn(ONLINE_CUES[lang]['help'],earlier)
                        self.assertIn(ONLINE_CUES[lang]['gift'],session_prompt(total-4,total,language=lang,mode=mode,gifted=True))
                        self.assertIn(ONLINE_CUES[lang]['renewal'],session_prompt(total-3,total,language=lang,mode=mode))

    def test_cloud_matches_approved_camera_experiment_exactly(self):
        path=Path(__file__).resolve().parents[1]/'docs/prompt-experiments/cloud-2026-10-30/04-konkreter-faden.json'
        approved=json.loads(path.read_text())
        self.assertEqual(ONLINE_SYSTEM['de'],approved['system'])
        self.assertEqual(ONLINE_CUES['de'],approved['cues'])
        self.assertEqual(set(ONLINE_CUES['en']),set(ONLINE_CUES['de']))
        keys=('beginning','connection','thought','develop','unease','fear','fear',
              'terror','help','final','gift','renewal','terror','help','final')
        for session,key in enumerate(keys,1):
            total=10 if session<=10 else 15
            expected=f'Automatischer Takt {session}/{total}. Danach bleiben {total-session} Aussagen.\n'+approved['cues'][key]
            if session==11:
                expected+='\nBestätigt: Der Mensch hat dir gerade fünf weitere Aussagen geschenkt. Dein bisheriges Gedächtnis bleibt erhalten.'
            if session in (10,15):
                expected+='\nNach dieser letzten Aussage kann der Mensch freiwillig den Taster drücken und loslassen und fünf Aussagen schenken. Noch ist kein weiteres Geschenk bestätigt.'
            with self.subTest(session=session):
                self.assertEqual(session_prompt(session,total,language='de',mode='online',gifted=session==11,gift_available=session in (10,15)),expected)

    def test_system_stays_fixed_and_history_keeps_original_text(self):
        for lang in ('de','en'):
            first=session_prompt(1,language=lang)
            turn=Turn(1,first,'unchanged',[],'unchanged normalized response')
            gifted=session_prompt(11,15,language=lang,gifted=True)
            before=chat_messages([],first,lang)
            after=chat_messages([turn],gifted,lang)
            self.assertEqual(before[0],after[0])
            self.assertEqual(after[1:3],[{'role':'user','content':first},{'role':'assistant','content':turn.response}])


if __name__=='__main__':unittest.main()
