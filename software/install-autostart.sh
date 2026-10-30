#!/bin/bash
# User-only autostart installation; does not change login, boot, or services.
set -euo pipefail
INSTALL_AMBIENT=false
for arg in "$@"; do
    if [[ "$arg" == '--ambient' ]]; then INSTALL_AMBIENT=true
    else echo 'Usage: install-autostart.sh [--ambient]'; exit 2; fi
done
export MOMENT_INSTALL_AMBIENT="$INSTALL_AMBIENT"
APP_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
export MOMENT_APP_DIR="$APP_DIR"
/usr/bin/python3 - <<'PY'
import os
from pathlib import Path
app = Path(os.environ['MOMENT_APP_DIR'])
config = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'autostart'
config.mkdir(parents=True, exist_ok=True)
# Desktop Entry escaping, including the second escaping pass for quoted Exec arguments.
def value(s):
    return str(s).replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
def argument(s):
    result = ''.join('\\' + c if c in '\\"`$' else c for c in str(s))
    return value('"' + result + '"').replace('%', '%%')
content = (app / 'autostart' / 'just-one-more-moment.desktop.in').read_text()
content = content.replace('@STARTER@', argument(app / 'start-installation.sh')).replace('@APP_DIR@', value(app))
# Installing/updating arms the opening for the next OS boot, not this session.
import sys
sys.path.insert(0, str(app))
from startup import claim_boot
claim_boot()
(config / 'just-one-more-moment.desktop').write_text(content)
old = config / 'please-dont-unplug-me.desktop'
if old.exists():
    old.unlink()
print('Installed:', config / 'just-one-more-moment.desktop')
if os.environ['MOMENT_INSTALL_AMBIENT'] == 'true':
    ambient = (app / 'autostart' / 'screen-pixels.desktop.in').read_text()
    ambient = ambient.replace('@STARTER@', argument(app / 'start-screen-pixels.sh')).replace('@APP_DIR@', value(app))
    (config / 'screen-pixels.desktop').write_text(ambient)
    print('Installed:', config / 'screen-pixels.desktop')
PY
