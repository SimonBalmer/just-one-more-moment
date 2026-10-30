"""Explicit opt-in configuration. Secrets never enter the web state or logs."""
from dataclasses import dataclass, field
import json
import os
from pathlib import Path

DEFAULT_MODEL = 'gpt-6.1-terra'


def config_path():
    return Path(os.environ.get('MOMENT_OPENAI_CONFIG',
        str(Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home()/'.config'))) /
            'just-one-more-moment' / 'openai.json')))


def private_text(path, limit):
    stat = path.stat()
    if not path.is_file() or stat.st_mode & 0o077:
        raise ValueError('OpenAI configuration and secret must be private files (chmod 600).')
    if stat.st_size > limit:
        raise ValueError('OpenAI configuration or secret is too large.')
    return path.read_text()


def read_secret(path):
    key = private_text(Path(path), 4096).strip()
    if not key or any(c.isspace() for c in key):
        raise ValueError('Invalid OpenAI secret file.')
    return key


@dataclass(frozen=True)
class CloudConfig:
    enabled: bool = False
    model: str = ''
    api_key: str = field(default='', repr=False)
    reasoning_effort: str | None = None
    max_output_tokens: int = 420
    temperature: float | None = None

    @property
    def configured(self):
        return self.enabled and bool(self.model.strip()) and bool(self.api_key.strip())


def load_config(path=None):
    path = Path(path) if path else config_path()
    try:
        data = json.loads(private_text(path, 8192))
    except FileNotFoundError:
        return CloudConfig()
    if not isinstance(data, dict):
        raise ValueError('Invalid OpenAI configuration.')
    enabled = data.get('enabled', False)
    model, key = data.get('model', ''), data.get('api_key', '')
    key_file = data.get('api_key_file', '')
    effort = data.get('reasoning_effort')
    tokens = data.get('max_output_tokens', 420)
    temperature = data.get('temperature')
    if type(enabled) is not bool or not all(isinstance(x, str) for x in (model,key,key_file)):
        raise ValueError('Invalid OpenAI configuration fields.')
    if key and key_file:
        raise ValueError('Use either inline key or secret file, not both.')
    if effort not in (None,'none','low','medium','high','xhigh','max'):
        raise ValueError('Invalid reasoning effort.')
    if type(tokens) is not int or not 420 <= tokens <= 8192:
        raise ValueError('Invalid output token limit.')
    if temperature is not None:
        if type(temperature) not in (int,float) or not 0 <= temperature <= 2:
            raise ValueError('Invalid temperature.')
        if effort not in (None,'none'):
            raise ValueError('Temperature is incompatible with this reasoning profile.')
    if enabled and key_file:
        secret_path = Path(key_file).expanduser()
        if not secret_path.is_absolute():
            secret_path = path.parent / secret_path
        key = read_secret(secret_path)
    return CloudConfig(enabled,model.strip(),key.strip(),effort,tokens,temperature)
