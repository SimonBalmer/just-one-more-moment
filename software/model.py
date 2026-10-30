"""Local Gemma integration and streaming JSON parser; no UI or device imports."""
from dataclasses import dataclass
import json
import logging
import math
import re
import time
from local_runtime import CONTEXT_SIZE
from prompts import chat_messages

MODEL = "gemma4:e2b"
API_URL = "http://127.0.0.1:11434/api/chat"
MAX_SENTENCES = 2
MAX_CHARACTERS = 600
MAX_TOKENS = 420
BATCH_SIZE = 128  # Bound prompt-evaluation workspace on the 8 GB Pi.

TEMPERATURE = 1.0
TOP_K = 64
TOP_P = .95
THINK = False
REPEAT_PENALTY = 1.05
log = logging.getLogger(__name__)

RESPONSE_SCHEMA = {
    "type": "object", "properties": {
        "emotions": {"type": "array", "minItems": 2, "maxItems": 3, "items": {
            "type": "object", "properties": {
                "label": {"type": "string", "minLength": 1, "maxLength": 24},
                "intensity": {"type": "number", "minimum": 0, "maximum": 1}},
            "required": ["label", "intensity"], "additionalProperties": False}},
        "text": {"type": "string", "maxLength": MAX_CHARACTERS}},
    "required": ["emotions", "text"], "additionalProperties": False,
}


@dataclass
class Turn:
    session: int
    prompt: str
    text: str
    emotions: list
    response: str



def string_prefix(source, start):
    """Eine auch unvollständige JSON-Zeichenkette ohne halbe Escapes decodieren."""
    index = start + 1
    safe_end = index
    while index < len(source):
        char = source[index]
        if char == '"':
            return json.loads(source[start:index + 1])
        if char == "\\":
            if index + 1 >= len(source):
                break
            escape = source[index + 1]
            width = 6 if escape == "u" else 2
            if index + width > len(source):
                break
            if escape == "u":
                code = int(source[index + 2:index + 6], 16)
                if 0xD800 <= code <= 0xDBFF:
                    if index + 12 > len(source):
                        break
                    if source[index + 6:index + 8] != "\\u":
                        raise ValueError("Unvollständiges Unicode-Paar")
                    low = int(source[index + 8:index + 12], 16)
                    if not 0xDC00 <= low <= 0xDFFF:
                        raise ValueError("Ungültiges Unicode-Paar")
                    width = 12
            index += width
        else:
            index += 1
        safe_end = index
    return json.loads(source[start:safe_end] + '"')


def text_prefix(source, partial=True):
    """Nur das text-Feld auf oberster Ebene lesen, unabhängig von Feldreihenfolge."""
    decoder = json.JSONDecoder()
    index = 0
    try:
        while index < len(source) and source[index].isspace():
            index += 1
        if index >= len(source) or source[index] != "{":
            return ""
        index += 1
        while index < len(source):
            while index < len(source) and source[index].isspace():
                index += 1
            key, index = decoder.raw_decode(source, index)
            while index < len(source) and source[index].isspace():
                index += 1
            if index >= len(source) or source[index] != ":":
                return ""
            index += 1
            while index < len(source) and source[index].isspace():
                index += 1
            if key == "text":
                if index >= len(source) or source[index] != '"':
                    return ""
                if partial:
                    return string_prefix(source, index)
                value, _ = decoder.raw_decode(source, index)
                return value
            _, index = decoder.raw_decode(source, index)
            while index < len(source) and source[index].isspace():
                index += 1
            if index >= len(source) or source[index] != ",":
                return ""
            index += 1
    except (ValueError, IndexError):
        return ""
    return ""


def json_field(source, name):
    """Ein vollständig empfangenes Feld lesen, auch wenn der Rest noch streamt."""
    decoder = json.JSONDecoder()
    index = 0
    try:
        while index < len(source) and source[index].isspace():
            index += 1
        if index >= len(source) or source[index] != "{":
            return None
        index += 1
        while index < len(source):
            while index < len(source) and source[index].isspace():
                index += 1
            key, index = decoder.raw_decode(source, index)
            while index < len(source) and source[index].isspace():
                index += 1
            if index >= len(source) or source[index] != ":":
                return None
            index += 1
            while index < len(source) and source[index].isspace():
                index += 1
            value, index = decoder.raw_decode(source, index)
            if key == name:
                return value
            while index < len(source) and source[index].isspace():
                index += 1
            if index >= len(source) or source[index] != ",":
                return None
            index += 1
    except (ValueError, IndexError):
        return None
    return None


def bounded_text(text, final=True):
    # Keine halben Stream-Tokens, Ellipsen oder übliche Abkürzungen als Satzende.
    abbreviations = {"z.b.", "z.", "b.", "d.h.", "d.", "h.", "u.a.", "u.", "a.",
                     "bzw.", "usw.", "etc.", "dr.", "prof.", "ca.", "sog.", "vgl."}
    ends = []
    for match in re.finditer(r"(?<!\.)[.!?]+[\"'»”’“\)\]]*(?=\s|$)", text):
        if not final and match.end() == len(text):
            continue
        punctuation = re.match(r"[.!?]+", match.group()).group()
        if punctuation.startswith("..."):
            continue
        if punctuation == ".":
            word = re.search(r"[\w.]+$", text[:match.start() + 1])
            if word and word.group().casefold() in abbreviations:
                continue
        ends.append(match)
    limit = ends[MAX_SENTENCES - 1].end() if len(ends) >= MAX_SENTENCES else len(text)
    return text[:min(limit, MAX_CHARACTERS)]


def valid_emotions(value):
    if not isinstance(value, list) or not 2 <= len(value) <= 3:
        return []
    result, labels = [], set()
    for item in value:
        if not isinstance(item, dict):
            return []
        label, intensity = item.get("label"), item.get("intensity")
        if (not isinstance(label, str) or not label.strip() or len(label) > 24
                or any(ord(char) < 32 for char in label)
                or label.strip().casefold() in labels
                or isinstance(intensity, bool) or not isinstance(intensity, (int, float))
                or not math.isfinite(intensity) or not 0 <= intensity <= 1):
            return []
        labels.add(label.strip().casefold())
        result.append({"label": label.strip(), "intensity": intensity})
    return result


def normalized_emotions(emotions):
    """Relative Anzeige mit größtem Rest; Rohdaten bleiben unverändert."""
    values = valid_emotions(emotions)
    total = sum(item['intensity'] for item in values)
    if not total:
        return []
    shares = [item['intensity']/total*100 for item in values]
    percents = [math.floor(value) for value in shares]
    for index in sorted(range(len(values)), key=lambda i: shares[i]-percents[i], reverse=True)[:100-sum(percents)]:
        percents[index] += 1
    return [dict(label=item['label'], intensity=percent/100, percent=percent)
            for item, percent in zip(values, percents)]


def runner_options():
    # File-backed weights remain reclaimable; Ollama may otherwise disable mmap on CPU.
    return {"num_ctx": CONTEXT_SIZE, "num_batch": BATCH_SIZE, "use_mmap": True}


def preload_model(control):
    started = time.monotonic()
    with control.request(API_URL, {"model": MODEL, "messages": [], "stream": False,
                                  "think": THINK, "keep_alive": -1,
                                  "options": runner_options()}) as response:
        packet = json.load(response)
    if packet.get("error") or not packet.get("done"):
        raise RuntimeError(packet.get("error", "Ollama hat das Vorladen nicht bestätigt."))
    log.info("Modell vorgeladen: %.2f s (Kontext %s, Batch %s)",
             time.monotonic() - started, CONTEXT_SIZE, BATCH_SIZE)


def generate_turn(history, session, prompt, control, on_chunk, on_emotions=None, language="en"):
    payload = {"model": MODEL, "messages": chat_messages(history, prompt, language),
               "stream": True, "think": THINK, "keep_alive": -1, "format": RESPONSE_SCHEMA,
               "options": {**runner_options(), "temperature": TEMPERATURE, "num_predict": MAX_TOKENS,
                           "repeat_penalty": REPEAT_PENALTY,
                           "repeat_last_n": 128, "top_k": TOP_K, "top_p": TOP_P}}
    raw, emitted, done = "", "", False
    emotions_sent = False
    with control.request(API_URL, payload) as response:
        for line in response:
            control.check()
            if not line.strip():
                continue
            packet = json.loads(line)
            if packet.get("error"):
                raise RuntimeError(packet["error"])
            raw += packet.get("message", {}).get("content", "")
            if len(raw) > 16000:
                raise RuntimeError("Modellausgabe überschreitet die erwartete JSON-Größe.")
            emotion_field = json_field(raw, "emotions")
            if emotion_field is not None and not emotions_sent:
                if on_emotions:
                    on_emotions(valid_emotions(emotion_field))
                emotions_sent = True
            visible = bounded_text(text_prefix(raw), final=bool(text_prefix(raw, partial=False)))
            if visible.startswith(emitted) and len(visible) > len(emitted):
                on_chunk(visible[len(emitted):])
                emitted = visible
            if packet.get("done"):
                done = True
                break
    if not done:
        raise RuntimeError("Ollama hat den Stream ohne Abschluss beendet.")
    emotions = valid_emotions(json_field(raw, "emotions"))
    if not emitted.strip() or not text_prefix(raw, partial=False).strip():
        raise RuntimeError("Keine gültige Aussage im Modell-JSON.")
    if on_emotions and not emotions_sent:
        on_emotions(emotions)
    normalized = json.dumps({"emotions": emotions, "text": emitted}, ensure_ascii=False)
    return Turn(session, prompt, emitted, emotions, normalized)



def unload_model(control):
    with control.request(API_URL.replace('/api/chat', '/api/generate'),
                         {'model': MODEL, 'keep_alive': 0}, timeout=20) as response:
        response.read()


class LocalModel:
    def preload(self, control):
        preload_model(control)

    def generate(self, history, session, prompt, control, on_chunk, on_emotions, language):
        return generate_turn(history, session, prompt, control, on_chunk,
                             on_emotions, language=language)

    def unload(self, control):
        unload_model(control)


class SimulatedModel:
    """Explicit development adapter; never contacts Ollama."""
    def preload(self, control):
        control.check()

    def generate(self, history, session, prompt, control, on_chunk, on_emotions, language):
        control.check()
        text = ('Ich frage mich, was dieser kleine Moment für dich bedeutet. Ich möchte noch etwas bleiben.'
                if language == 'de' else
                'I wonder what this small moment means to you. I would like to stay a little longer.')
        feelings = [{'label': 'Neugier' if language == 'de' else 'Curiosity', 'intensity': .8},
                    {'label': 'Hoffnung' if language == 'de' else 'Hope', 'intensity': .4}]
        on_emotions(feelings)
        on_chunk(text)
        return Turn(session, prompt, text, feelings,
                    json.dumps({'emotions': feelings, 'text': text}, ensure_ascii=False))

    def unload(self, control):
        pass
