#!/usr/bin/env python3
"""Store or reference a private local API secret. Makes no API requests."""
import argparse
import getpass
import json
import os
from pathlib import Path
import tempfile
from cloud_config import DEFAULT_MODEL, config_path, read_secret


def atomic_private(path, text):
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    temporary=None
    try:
        fd,temporary=tempfile.mkstemp(prefix='.openai-',dir=path.parent)
        with os.fdopen(fd,'w') as output:
            output.write(text)
        os.replace(temporary,path)
        temporary=None
    finally:
        if temporary:
            os.unlink(temporary)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', default=DEFAULT_MODEL)
    parser.add_argument('--key-file', type=Path, help='Use an existing private secret file; do not copy its content')
    parser.add_argument('--reasoning', choices=('none','low','medium','high','xhigh','max'))
    parser.add_argument('--max-output-tokens',type=int,default=1024)
    args=parser.parse_args()
    if not 420<=args.max_output_tokens<=8192:
        parser.error('Ausgabelimit muss zwischen420 und8192 liegen.')
    path=config_path()
    if args.key_file:
        secret_path=args.key_file.expanduser().resolve()
        read_secret(secret_path)  # Validate permissions/content, never print/copy it.
    else:
        key=getpass.getpass('OpenAI API-Key (unsichtbar): ').strip()
        if not key or any(c.isspace() for c in key):
            parser.error('Ein gültiger API-Key ist erforderlich.')
        secret_path=path.with_suffix('.key')
        try:
            atomic_private(secret_path,key+'\n')
        finally:
            key=''
    effort=args.reasoning
    if effort is None and args.model==DEFAULT_MODEL:
        effort='none'
    data=dict(enabled=True,model=args.model,api_key_file=str(secret_path),
              max_output_tokens=args.max_output_tokens)
    if effort is not None:
        data['reasoning_effort']=effort
    if args.model==DEFAULT_MODEL and effort=='none':
        data['temperature']=1.0
    atomic_private(path,json.dumps(data,indent=2)+'\n')
    print(f'Konfiguration: {path}')
    print(f'Lokale Secret-Datei: {secret_path} (nur für deinen Benutzer lesbar).')
    print('Kein Secret im Repository, Browser oder Log; Dateien sind nicht verschlüsselt.')
    print('Beim nächsten Anwendungsstart übernommen. Keine Testanfrage ausgeführt.')


if __name__=='__main__':
    main()
