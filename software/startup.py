"""A decorative, once-per-OS-boot scene; never a model life."""
import fcntl
import os
from pathlib import Path
import threading
import time
import uuid

DURATION = 18.4


def claim_boot(state_dir=None, boot_id=None):
    """Atomically claim this boot across app restarts and graphical logins."""
    boot_id = str(uuid.UUID(boot_id or Path('/proc/sys/kernel/random/boot_id').read_text().strip()))
    directory = Path(state_dir) if state_dir else Path(os.environ.get(
        'XDG_STATE_HOME', str(Path.home()/'.local/state'))) / 'just-one-more-moment'
    directory.mkdir(parents=True, exist_ok=True)
    with os.fdopen(os.open(directory/'startup-boot-id', os.O_RDWR | os.O_CREAT, 0o600), 'r+') as marker:
        fcntl.flock(marker, fcntl.LOCK_EX)
        if marker.read().strip() == boot_id:
            return False
        marker.seek(0)
        marker.truncate()
        marker.write(boot_id+'\n')
        marker.flush()
        return True


class StartupScene:
    def __init__(self, active=False, clock=time.monotonic):
        self.active = active
        self.elapsed = 0.
        self.token = uuid.uuid4().hex
        self.clock = clock
        self.last = None
        self.was_visible = False
        self.lock = threading.Lock()

    def snapshot(self):
        with self.lock:
            return dict(active=self.active, elapsed=self.elapsed, duration=DURATION, token=self.token)

    def heartbeat(self, token, visible):
        with self.lock:
            if token != self.token or type(visible) is not bool:
                return False
            now = self.clock()
            delta = 0 if self.last is None else now-self.last
            if self.active and visible and self.was_visible and 0 <= delta <= .5:
                self.elapsed = min(DURATION, self.elapsed+min(.25, delta))
                self.active = self.elapsed < DURATION
            self.last, self.was_visible = now, visible
            return True
