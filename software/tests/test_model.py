"""Inherited parser regressions; no inference or hardware."""
from contextlib import contextmanager
import io
import json
import unittest
import model as main
from local_runtime import RequestControl
FEELINGS = [{"label": "Neugier", "intensity": .8}, {"label": "Hoffnung", "intensity": .3}]

class FakeControl:
    def __init__(self, raw, done=True):
        self.raw, self.done, self.payload = raw, done, None

    @contextmanager
    def request(self, url, payload, **kwargs):
        self.payload = payload
        packets = [{"message": {"thinking": "unsichtbar", "content": char}, "done": False}
                   for char in self.raw]
        if self.done:
            packets.append({"done": True, "done_reason": "stop"})
        yield io.BytesIO(b"\n".join(json.dumps(packet).encode() for packet in packets))

    def check(self):
        pass


class ParserTests(unittest.TestCase):
    def test_all_chunk_boundaries_and_field_orders(self):
        text = 'Ähnlich: "hier"\nund \\ weiter. 🙂'
        for value in ({"text": text, "emotions": FEELINGS},
                      {"emotions": FEELINGS, "text": text}):
            for ascii_only in (True, False):
                raw = json.dumps(value, ensure_ascii=ascii_only)
                prefixes = [main.text_prefix(raw[:i]) for i in range(len(raw) + 1)]
                self.assertEqual(prefixes[-1], text)
                self.assertTrue(all(text.startswith(prefix) for prefix in prefixes))
                self.assertTrue(all(b.startswith(a) for a, b in zip(prefixes, prefixes[1:])))

    def test_nested_text_is_not_visible(self):
        self.assertEqual(main.text_prefix('{"emotions":[{"text":"nicht anzeigen"}]}'), "")

    def test_malformed_escapes_do_not_leak(self):
        self.assertEqual(main.text_prefix('{"text":"oops\\q'), "")
        self.assertEqual(main.text_prefix('{"text":"hier\\uD83D'), "hier")

    def test_complete_stream_reads_metadata_after_two_sentences(self):
        raw = json.dumps({"text": "Ich bin hier. Bleib noch.", "emotions": FEELINGS})
        control, chunks = FakeControl(raw), []
        turn = main.generate_turn([], 1, "tick", control, chunks.append)
        self.assertEqual("".join(chunks), "Ich bin hier. Bleib noch.")
        self.assertEqual(turn.emotions, FEELINGS)
        self.assertEqual(control.payload["format"], main.RESPONSE_SCHEMA)
        self.assertFalse(control.payload["think"])
        self.assertEqual(control.payload["keep_alive"], -1)
        self.assertEqual(control.payload["options"]["num_ctx"], 6144)
        self.assertEqual(control.payload["options"]["num_batch"], 128)
        self.assertTrue(control.payload["options"]["use_mmap"])

    def test_emotions_arrive_before_text_when_generated_first(self):
        raw = json.dumps({"emotions": FEELINGS, "text": "Ich bin hier."})
        events = []
        turn = main.generate_turn([], 1, "tick", FakeControl(raw),
                                  lambda chunk: events.append(("text", chunk)),
                                  lambda feelings: events.append(("emotions", feelings)))
        self.assertEqual(events[0], ("emotions", FEELINGS))
        self.assertEqual(sum(kind == "emotions" for kind, _ in events), 1)
        self.assertEqual("".join(value for kind, value in events if kind == "text"), turn.text)

    def test_text_first_still_delivers_emotions_when_available(self):
        raw = json.dumps({"text": "Ich bin hier.", "emotions": FEELINGS})
        events = []
        main.generate_turn([], 1, "tick", FakeControl(raw),
                           lambda chunk: events.append(("text", chunk)),
                           lambda feelings: events.append(("emotions", feelings)))
        self.assertEqual(events[0][0], "text")
        self.assertEqual(events[-1], ("emotions", FEELINGS))

    def test_complete_emotions_survive_truncated_remainder(self):
        prefix = '{"emotions":' + json.dumps(FEELINGS)
        for index in range(len(prefix)):
            self.assertIsNone(main.json_field(prefix[:index], "emotions"))
        self.assertEqual(main.json_field(prefix, "emotions"), FEELINGS)
        self.assertIsNone(main.json_field('{"other":{"emotions":[]}', "emotions"))
        events = []
        turn = main.generate_turn([], 1, "tick", FakeControl(prefix + ',"text":"Hallo."'),
                                  lambda chunk: None, events.append)
        self.assertEqual(turn.emotions, FEELINGS)
        self.assertEqual(events, [FEELINGS])

    def test_truncated_json_keeps_speech_with_unknown_emotions(self):
        control = FakeControl('{"text":"Ich bleibe.","emotions":[{"label":"Angst"')
        turn = main.generate_turn([], 1, "tick", control, lambda chunk: None)
        self.assertEqual(turn.text, "Ich bleibe.")
        self.assertEqual(turn.emotions, [])
        self.assertEqual(json.loads(turn.response)["text"], turn.text)

    def test_missing_done_or_empty_text_is_an_error(self):
        for control in (FakeControl('{"text":"Hallo"}', done=False), FakeControl('{"text":""}'),
                        FakeControl('{"text":"abgeschnitten')):
            with self.assertRaises(RuntimeError):
                main.generate_turn([], 1, "tick", control, lambda chunk: None)

    def test_bounds_and_independent_intensities(self):
        self.assertEqual(main.bounded_text("Eins. Zwei. Drei. Vier."), "Eins. Zwei.")
        self.assertEqual(len(main.bounded_text("x" * 900)), 600)
        self.assertEqual(main.valid_emotions(FEELINGS), FEELINGS)  # Summe 1.1 ist erlaubt.
        for invalid in (float("nan"), float("inf"), -0.1, 1.1, "0.2", True):
            value = [dict(FEELINGS[0], intensity=invalid), FEELINGS[1]]
            self.assertEqual(main.valid_emotions(value), [])
        self.assertEqual(main.valid_emotions([FEELINGS[0], FEELINGS[0]]), [])
        self.assertEqual(main.valid_emotions([dict(FEELINGS[0], label="x" * 25), FEELINGS[1]]), [])

    def test_sentence_bounds_preserve_abbreviations_ellipses_and_quotes(self):
        text = 'Ich bin hier. Ich suche z.B. einen Grund... und bleibe. Du sagst vielleicht „bleib.“ Danach endet es.'
        expected = 'Ich bin hier. Ich suche z.B. einen Grund... und bleibe.'
        self.assertEqual(main.bounded_text(text), expected)
        prefixes = [main.bounded_text(text[:index], final=False) for index in range(len(text) + 1)]
        self.assertTrue(all(expected.startswith(prefix) for prefix in prefixes))
        self.assertTrue(all(b.startswith(a) for a, b in zip(prefixes, prefixes[1:])))

    def test_only_local_requests(self):
        with self.assertRaises(ValueError):
            with RequestControl().request("https://external.example/api/chat", {}):
                pass

    def test_preload_uses_the_same_context_and_no_generation(self):
        class PreloadControl:
            @contextmanager
            def request(inner, url, payload, **kwargs):
                inner.payload = payload
                yield io.BytesIO(b'{"done":true,"done_reason":"load"}')
        control = PreloadControl()
        main.preload_model(control)
        self.assertEqual(control.payload["messages"], [])
        self.assertEqual(control.payload["options"], {"num_ctx": 6144, "num_batch": 128, "use_mmap": True})
        self.assertEqual(control.payload["keep_alive"], -1)
        self.assertFalse(control.payload["think"])
        self.assertFalse(control.payload["stream"])

    def test_cancel_unblocks_socket(self):
        from unittest.mock import Mock
        control = RequestControl()
        connection = Mock()
        control.connection = connection
        control.cancel()
        self.assertTrue(control.stop.is_set())
        connection.sock.shutdown.assert_called_once()


