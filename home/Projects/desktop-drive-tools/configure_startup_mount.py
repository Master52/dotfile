#!/usr/bin/python3
"""Add only New Volume's UUID to fstab, keeping existing active mounts intact."""
import datetime
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

UUID = '66CEB2CECEB29631'
TARGET = '/mnt/new-volume'
ENTRY = f'UUID={UUID} {TARGET} ntfs3 defaults,nofail,uid=1000,gid=1000,umask=0022,windows_names 0 0'


def updated_fstab(text):
    lines = []
    for line in text.splitlines():
        parts = line.split('#', 1)[0].split()
        if parts and parts[0] == 'UUID=' + UUID:
            continue
        if len(parts) > 1 and parts[1] == TARGET:
            raise ValueError(f'{TARGET} already has a different fstab entry.')
        lines.append(line)
    return '\n'.join(lines).rstrip() + '\n' + ENTRY + '\n'


def main():
    if os.geteuid() != 0:
        raise SystemExit('Run: sudo python3 ~/Projects/desktop-drive-tools/configure_startup_mount.py')
    fstab = Path('/etc/fstab')
    old = fstab.read_text()
    new = updated_fstab(old)
    target = Path(TARGET)
    if target.is_symlink() or (target.exists() and not target.is_dir()):
        raise SystemExit(f'{TARGET} is not a normal directory.')
    target.mkdir(mode=0o755, parents=True, exist_ok=True)
    if any(target.iterdir()) and not os.path.ismount(target):
        raise SystemExit(f'{TARGET} contains files. Refusing to hide them with a mount.')
    fd, filename = tempfile.mkstemp(prefix='.fstab-new-volume-', dir='/etc')
    try:
        with os.fdopen(fd, 'w') as file:
            file.write(new)
        os.chmod(filename, fstab.stat().st_mode & 0o777)
        subprocess.run(['findmnt', '--verify', '--tab-file', filename], check=True)
        if new != old:
            backup = '/etc/fstab.before-new-volume-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            shutil.copy2(fstab, backup)
            os.replace(filename, fstab)
            print(f'fstab backup: {backup}')
    finally:
        Path(filename).unlink(missing_ok=True)
    current = subprocess.run(['findmnt', '-rn', '-S', 'UUID=' + UUID, '-o', 'TARGET'],
                             capture_output=True, text=True)
    if current.returncode == 0 and current.stdout.strip():
        print('The volume is already mounted. Its current mount is preserved.')
        print(f'At the next startup it will mount at {TARGET}.')
    elif Path('/dev/disk/by-uuid/' + UUID).exists():
        subprocess.run(['mount', TARGET], check=True)
        print(f'Mounted at {TARGET}.')
    else:
        print(f'Volume absent; it will mount at {TARGET} on a startup when present.')
    print('Startup mounting enabled for New Volume. A missing drive will not be required for boot.')


if __name__ == '__main__':
    main()
