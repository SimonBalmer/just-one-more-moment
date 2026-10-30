"""Abbrechbare lokale HTTP-Anfragen für das lokale Modell."""
from contextlib import contextmanager
import http.client
import json
import socket
import threading
from urllib.parse import urlsplit

CONTEXT_SIZE = 6144  # Textkontext während eines Lebens.


class RequestControl:
    """Ein Worker besitzt höchstens eine lokale HTTP-Verbindung."""

    def __init__(self, stop=None):
        self.stop = stop if stop is not None else threading.Event()
        self.lock = threading.Lock()
        self.connection = None
        self.active_socket = None

    def check(self):
        if self.stop.is_set():
            raise InterruptedError("Abgebrochen")

    def cancel(self):
        self.stop.set()
        with self.lock:
            active_socket = self.active_socket or (self.connection.sock if self.connection else None)
        # shutdown unterbricht auch einen blockierenden HTTP-Stream.
        if active_socket:
            try:
                active_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

    @contextmanager
    def openai_request(self, payload, api_key, timeout=120):
        """Separate fixed HTTPS destination; the Ollama localhost guard stays intact."""
        self.check()
        connection = http.client.HTTPSConnection('api.openai.com', 443, timeout=5)
        with self.lock:
            self.connection = connection
        try:
            connection.connect()
            with self.lock:
                self.active_socket = connection.sock
            self.check()
            connection.sock.settimeout(timeout)
            connection.request('POST', '/v1/responses', json.dumps(payload).encode('utf-8'),
                               {'Content-Type':'application/json', 'Authorization':'Bearer '+api_key})
            response = connection.getresponse()
            if response.status >= 400:
                response.read(8192)  # Never disclose response bodies or credentials.
                raise RuntimeError(f'OpenAI request rejected (HTTP {response.status}).')
            yield response
        except OSError:
            if self.stop.is_set():
                raise InterruptedError('Abgebrochen') from None
            raise RuntimeError('OpenAI connection unavailable.') from None
        finally:
            with self.lock:
                self.connection = self.active_socket = None
            connection.close()

    @contextmanager
    def request(self, url, payload, timeout=600):
        self.check()
        address = urlsplit(url)
        if address.scheme != "http" or address.hostname not in ("localhost", "127.0.0.1", "::1"):
            raise ValueError("Ollama muss über eine lokale HTTP-Adresse erreichbar sein.")
        connection = http.client.HTTPConnection(address.hostname, address.port or 80, timeout=5)
        with self.lock:
            self.connection = connection
        try:
            self.check()
            connection.connect()
            with self.lock:
                self.active_socket = connection.sock
            self.check()
            connection.sock.settimeout(timeout)
            path = address.path or "/"
            if address.query:
                path += "?" + address.query
            connection.request("POST", path, json.dumps(payload).encode("utf-8"),
                               {"Content-Type": "application/json"})
            response = connection.getresponse()
            if response.status >= 400:
                detail = response.read(8192).decode("utf-8", errors="replace")
                raise RuntimeError(f"Ollama HTTP {response.status}: {detail}")
            yield response
        except (ConnectionError, socket.timeout) as error:
            if self.stop.is_set():
                raise InterruptedError("Abgebrochen") from error
            raise RuntimeError(f"Ollama ist nicht erreichbar oder antwortet nicht: {error}") from error
        finally:
            with self.lock:
                self.connection = None
                self.active_socket = None
            connection.close()
