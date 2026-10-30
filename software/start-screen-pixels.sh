#!/bin/bash
set -euo pipefail
APP_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
LOG_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/just-one-more-moment"
mkdir -p -- "$LOG_DIR"
exec >>"$LOG_DIR/screen-pixels.log" 2>&1
cd -- "$APP_DIR"
exec /usr/bin/python3 -u screen_pixels.py
