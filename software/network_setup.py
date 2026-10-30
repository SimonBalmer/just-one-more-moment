"""Non-blocking API reachability and opt-in NetworkManager hotspot connection.

Never changes existing profiles, radio settings or system policy. No API key,
camera data or inference is involved in connectivity checks.
"""
import http.client
import os
import getpass
import subprocess
import threading
import time

SSID = 'just-one-more-moment'
PASSWORD = 'hslu-phki-hs26'
PROFILE = 'Just one more moment — smartphone'


def internet_available():
    connection = http.client.HTTPSConnection('api.openai.com', timeout=4)
    try:
        connection.request('GET', '/v1/models')
        response = connection.getresponse()
        return response.status in (200, 401)
    except (OSError, http.client.HTTPException):
        return False
    finally:
        connection.close()


class NetworkSetup:
    def __init__(self, probe=internet_available, run=subprocess.run, clock=time.monotonic):
        self.probe, self.run, self.clock = probe, run, clock
        self.lock = threading.Lock()
        self.thread = None
        self.busy = False
        self.cancelled = threading.Event()
        self.serial = 0
        self.state = dict(status='unknown', error=None, checked=-1e9, serial=0)

    def snapshot(self):
        with self.lock:
            return dict(self.state)

    def request(self, connect=False, background=False):
        with self.lock:
            if self.busy:
                # A START can await the already running reachability probe.
                if not background and not connect and self.state['status'] == 'online':
                    self.state.update(status='checking', error=None)
                    return self.serial
                return None
            self.busy = True
            self.cancelled = threading.Event()
            self.serial += 1
            serial, cancelled = self.serial, self.cancelled
            status = 'online' if background and not connect and self.state['status'] == 'online' else 'connecting' if connect else 'checking'
            self.state.update(status=status, error=None, serial=serial)
            self.thread = threading.Thread(target=self._work, args=(serial, cancelled, connect),
                                           name='network-setup', daemon=True)
            self.thread.start()
            return serial

    def cancel(self):
        self.cancelled.set()

    def close(self):
        self.cancel()
        if self.thread:
            self.thread.join(timeout=1)

    def _nm(self, *args):
        return self.run(['nmcli', '--wait', '35', *args], capture_output=True, text=True,
                        timeout=40, env={**os.environ, 'LC_ALL':'C'})

    def _connect(self, cancelled):
        # Remember the active Wi-Fi profile for recovery after a failed attempt.
        result = self._nm('-t', '-f', 'UUID,TYPE', 'connection', 'show', '--active')
        previous = next((line.split(':')[0] for line in result.stdout.splitlines()
                         if line.endswith(':802-11-wireless')), None)
        result = self._nm('-g', 'connection.id', 'connection', 'show')
        if PROFILE not in result.stdout.splitlines():
            result = self._nm('connection', 'add', 'type', 'wifi', 'ifname', '*',
                              'con-name', PROFILE, 'ssid', SSID,
                              'connection.permissions', 'user:'+getpass.getuser(),
                              'connection.autoconnect-priority', '-10',
                              'wifi-sec.key-mgmt', 'wpa-psk', 'wifi-sec.psk', PASSWORD)
            if result.returncode:
                return 'permission' if any(word in result.stderr.lower() for word in ('authorized','privilege','permission')) else 'configuration'
        if cancelled.is_set():
            return 'cancelled'
        try:
            result = self._nm('connection', 'up', 'id', PROFILE)
            if result.returncode:
                return 'permission' if any(word in result.stderr.lower() for word in ('authorized','privilege','permission')) else 'connection'
            if cancelled.is_set():
                return 'cancelled'
            # DHCP/DNS may take a moment after activation.
            for _ in range(3):
                if self.probe():
                    return None
                if cancelled.wait(1):
                    return 'cancelled'
            return 'internet'
        finally:
            if previous and (cancelled.is_set() or not self.probe()):
                self._nm('connection', 'up', 'uuid', previous)

    def _work(self, serial, cancelled, connect):
        error = None
        try:
            if self.probe():
                online = True  # Keep a working home/venue connection untouched.
            elif connect:
                error = self._connect(cancelled)
                online = error is None
            else:
                online = False
        except (OSError, subprocess.SubprocessError):
            online, error = False, 'connection'
        with self.lock:
            if self.serial == serial:
                self.busy = False
                self.state.update(status='online' if online else 'offline', error=error,
                                  checked=self.clock())
