#!/usr/bin/python3
"""Prepare/apply reversible logo-only boot customisation. Never reboots the Pi."""
import argparse
from datetime import datetime, timezone
import difflib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import stat

ROOT = Path(__file__).resolve().parent
THEME = Path('/usr/share/plymouth/themes/moment-black')
CONFIG = Path('/boot/firmware/config.txt')
CMDLINE = Path('/boot/firmware/cmdline.txt')
PLYMOUTH = Path('/etc/plymouth/plymouthd.conf')
BLOCK = '\n[all]\n# Just one more moment: black early boot, graphical opening in the installation\ndisable_splash=1\n'


def proposed(config, cmdline):
    if len(cmdline.strip().splitlines()) != 1 or not any(x.startswith('root=') for x in cmdline.split()):
        raise ValueError('Unexpected kernel command line; refusing to change it.')
    if BLOCK.strip() not in config:
        config = config.rstrip()+'\n'+BLOCK
    words = cmdline.split()
    if 'logo.nologo' not in words:
        words.append('logo.nologo')
    return config, ' '.join(words)+'\n'


def atomic_write(path, content):
    original_mode = stat.S_IMODE(path.stat().st_mode)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w',dir=path.parent,prefix=path.name+'.moment-',delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(original_mode)
        temporary.replace(path)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)


def backup_files():
    return [CONFIG, CMDLINE, PLYMOUTH, *Path('/boot').glob('initrd.img-*'),
            *Path('/boot/firmware').glob('initramfs*'),
            THEME/'moment-black.plymouth', THEME/'moment-black.script']


def restore(directory):
    directory = Path(directory).resolve()
    if directory.parent != Path('/var/backups') or not directory.name.startswith('just-one-more-moment-boot-'):
        raise ValueError('Expected a backup directory made by this installer.')
    entries = json.loads((directory/'manifest.json').read_text())
    allowed = {str(p) for p in backup_files()}
    for name, existed in entries.items():
        if name not in allowed:
            raise ValueError('Unexpected backup target.')
        target = Path(name)
        if existed:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(directory/name.lstrip('/'), target)
        else:
            target.unlink(missing_ok=True)
    print('Restored original boot files and initramfs:', directory)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--apply', action='store_true')
    group.add_argument('--restore', metavar='BACKUP')
    args = parser.parse_args()
    if args.restore:
        if os.geteuid() != 0:
            parser.error('Restoring boot files requires root.')
        restore(args.restore)
        return
    config, cmdline = proposed(CONFIG.read_text(), CMDLINE.read_text())
    for path, content in ((CONFIG,config),(CMDLINE,cmdline)):
        print(''.join(difflib.unified_diff(path.read_text().splitlines(True),content.splitlines(True),fromfile=str(path),tofile=str(path))),end='')
    print('Plymouth: pix/current theme -> moment-black. Existing login, services, SPI and kernel root settings are preserved.')
    if not args.apply:
        print('Dry run only. Apply: sudo python3 install-startup-boot.py --apply')
        return
    if os.geteuid() != 0:
        parser.error('Applying boot files requires root.')
    if Path('/usr/share/plymouth/themes/default.plymouth').is_symlink():
        raise RuntimeError('Unexpected legacy theme symlink; inspect before changing it.')
    for tool in ('plymouth-set-default-theme','update-initramfs'):
        if not shutil.which(tool):
            raise RuntimeError('Required existing tool unavailable: '+tool)
    directory = Path('/var/backups')/('just-one-more-moment-boot-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    directory.mkdir(mode=0o700)
    entries = {}
    for path in backup_files():
        entries[str(path)] = path.exists()
        if path.exists():
            dest = directory/str(path).lstrip('/')
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
    (directory/'manifest.json').write_text(json.dumps(entries,indent=2)+'\n')
    print('Backup:', directory, flush=True)
    try:
        THEME.mkdir(parents=True, exist_ok=True)
        for source in (ROOT/'boot/moment-black').iterdir():
            shutil.copy2(source, THEME/source.name)
        atomic_write(CONFIG, config)
        atomic_write(CMDLINE, cmdline)
        subprocess.run(['/usr/sbin/plymouth-set-default-theme','moment-black'],check=True)
        subprocess.run(['/usr/sbin/update-initramfs','-u','-k','all'],check=True)
    except BaseException:
        restore(directory)
        raise
    print('Installed for the next boot. No reboot was performed.')
    print('Undo: sudo python3 install-startup-boot.py --restore '+str(directory))


if __name__ == '__main__':
    main()
