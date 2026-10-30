#!/bin/bash
# Run from a graphical session. Escape or closing Chromium ends this launch.
set -euo pipefail
for arg in "$@"; do
    [[ "$arg" == '--simulate' || "$arg" == '--boot-animation' || "$arg" == '--preview-startup' ]] || { echo 'Usage: start-installation.sh [--simulate] [--boot-animation] [--preview-startup]'; exit 2; }
done
APP_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
LOG_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/just-one-more-moment"
mkdir -p -- "$LOG_DIR"
exec 9>"$LOG_DIR/autostart.lock"
/usr/bin/flock -n 9 || exit 0
if [[ -f "$LOG_DIR/autostart.log" ]]; then
    mv -f -- "$LOG_DIR/autostart.log" "$LOG_DIR/autostart.previous.log"
fi
exec >>"$LOG_DIR/autostart.log" 2>&1
cd -- "$APP_DIR"
export DISPLAY="${DISPLAY:-:0}"
BROWSER=$(command -v chromium || command -v chromium-browser || true)
if [[ -z "$BROWSER" ]]; then
    echo 'Chromium fehlt. Siehe README.md.'
    exit 1
fi
backend_pid=''
browser_pid=''
cleanup() {
    trap - EXIT INT TERM
    if [[ -n "$browser_pid" ]]; then kill "$browser_pid" 2>/dev/null || true; fi
    if [[ -n "$backend_pid" ]]; then
        kill "$backend_pid" 2>/dev/null || true
        wait "$backend_pid" 2>/dev/null || true
    fi
    if [[ -n "$browser_pid" ]]; then wait "$browser_pid" 2>/dev/null || true; fi
}
trap cleanup EXIT INT TERM
/usr/bin/python3 -u main.py "$@" 9>&- &
backend_pid=$!
# Verify our backend, never attach to an unrelated listener on this port.
ready=false
for ((attempt=0; attempt<100; attempt++)); do
    kill -0 "$backend_pid" 2>/dev/null || exit 1
    if /usr/bin/python3 - "$backend_pid" <<'PY'
import json
import sys
import urllib.request
try:
    with urllib.request.urlopen('http://127.0.0.1:8765/api/health', timeout=.5) as response:
        health = json.load(response)
        assert health['ready'] and health['pid'] == int(sys.argv[1])
except Exception:
    raise SystemExit(1)
PY
    then ready=true; break; fi
    sleep .1
done
[[ "$ready" == true ]] || exit 1
# The dedicated local kiosk profile must start without unlocking a desktop keyring.
"$BROWSER" --kiosk --no-first-run --no-default-browser-check --disable-session-crashed-bubble \
    --password-store=basic \
    --disable-background-networking --disable-component-update --disable-sync --no-pings \
    --disable-extensions --renderer-process-limit=2 \
    --disable-features=OptimizationGuideOnDeviceModel,Translate \
    --user-data-dir="$LOG_DIR/chromium" --app=http://127.0.0.1:8765/ 9>&- &
browser_pid=$!
# Only this launcher owns fd 9. Polling also catches children that exited before
# wait could register them; either ending closes the other, without a restart.
while kill -0 "$backend_pid" 2>/dev/null && kill -0 "$browser_pid" 2>/dev/null; do
    sleep .2
done
