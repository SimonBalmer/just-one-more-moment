"""OpenAI Responses adapter. No network calls until explicitly configured and started."""
import base64
import json
from model import RESPONSE_SCHEMA, Turn, bounded_text, text_prefix, json_field, valid_emotions
from prompts import ONLINE_SYSTEM


class OpenAIModel:
    def __init__(self, config, frame_provider):
        self.config, self.frame_provider = config, frame_provider

    @property
    def configured(self):
        return self.config.configured

    def preload(self, control):
        control.check()
        if not self.configured:
            raise RuntimeError('OpenAI is not configured.')
        # No billable preflight request: the first model call contains a fresh image.

    def generate(self, history, session, prompt, control, on_chunk, on_emotions, language):
        self.preload(control)
        image = self.frame_provider(control)
        control.check()
        inputs=[]
        for turn in history:
            inputs.extend(({'role':'user','content':turn.prompt},
                           {'role':'assistant','content':turn.response}))
        inputs.append({'role':'user','content':[
            {'type':'input_text','text':prompt},
            {'type':'input_image','image_url':'data:image/png;base64,'+base64.b64encode(image).decode(), 'detail':'low'}]})
        payload=dict(model=self.config.model, instructions=ONLINE_SYSTEM[language], input=inputs,
                     store=False, stream=True, max_output_tokens=self.config.max_output_tokens,
                     text={'format':{'type':'json_schema','name':'installation_statement',
                                     'schema':RESPONSE_SCHEMA,'strict':True}})
        if self.config.reasoning_effort is not None:
            payload['reasoning']={'effort':self.config.reasoning_effort}
        if self.config.temperature is not None:
            payload['temperature']=self.config.temperature
        raw, emitted, done, feelings_sent = '', '', False, False
        try:
            with control.openai_request(payload,self.config.api_key) as response:
                for line in response:
                    control.check()
                    if not line.startswith(b'data:'):
                        continue
                    data=line[5:].strip()
                    if not data or data==b'[DONE]':
                        continue
                    packet=json.loads(data)
                    kind=packet.get('type')
                    if kind in ('response.failed','response.incomplete','error','response.refusal.delta'):
                        raise RuntimeError('OpenAI did not complete a valid statement.')
                    if kind=='response.output_text.delta':
                        raw+=packet.get('delta','')
                        if len(raw)>16000:
                            raise RuntimeError('OpenAI output exceeds the bounded JSON size.')
                        emotions=json_field(raw,'emotions')
                        if emotions is not None and not feelings_sent:
                            on_emotions(valid_emotions(emotions));feelings_sent=True
                        visible=bounded_text(text_prefix(raw),final=bool(text_prefix(raw,partial=False)))
                        if visible.startswith(emitted) and len(visible)>len(emitted):
                            on_chunk(visible[len(emitted):]);emitted=visible
                    elif kind=='response.completed':
                        done=packet.get('response',{}).get('status')=='completed'
                        break
            control.check()
            if not done:
                raise RuntimeError('OpenAI stream ended without completion.')
            result=json.loads(raw)
            if not isinstance(result,dict) or not emitted.strip() or not isinstance(result.get('text'),str):
                raise RuntimeError('OpenAI returned no valid statement.')
            emotions=valid_emotions(result.get('emotions'))
            if not feelings_sent:
                on_emotions(emotions)
            normalized=json.dumps({'emotions':emotions,'text':emitted},ensure_ascii=False)
            return Turn(session,prompt,emitted,emotions,normalized)
        finally:
            image=None;payload=None;inputs.clear()
