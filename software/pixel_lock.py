"""Gemeinsame SPI-Reservierung: Anwendungen dauerhaft, Ambient pro Frame."""
import fcntl
import os
from pathlib import Path


def acquire(blocking=True):
    runtime = Path(os.environ.get('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}'))
    handle = open(runtime / 'please-dont-unplug-me-neopixels.lock', 'a')
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
    except BaseException:
        handle.close()
        raise
    return handle
