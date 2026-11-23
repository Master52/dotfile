#!/usr/bin/python3
"""One-time, verified migration of the closed Persnal profile into gocryptfs."""
from contextlib import ExitStack
from datetime import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import runpy
import secrets
import shutil
import subprocess
import tarfile


HOME = Path.home()
ROOT = HOME / '.local/share/firefox-vault/Persnal'
CONFIG = HOME / '.config/firefox-launcher/vault.json'
PROFILE = HOME / '.mozilla/firefox/CAlDsdyA.Profile 1'
CACHE = HOME / '.cache/mozilla/firefox/CAlDsdyA.Profile 1'
BINARY = HOME / '.local/libexec/gocryptfs/gocryptfs'
ENTRY = 'firefox-profiles/Persnal'
CODE = runpy.run_path(str(HOME / '.local/bin/firefox-vault'), run_name='vault_setup_helpers')


def digest(stream):
    value = hashlib.sha256()
    while chunk := stream.read(1024 * 1024):
        value.update(chunk)
    return value.hexdigest()


def manifest(source):
    result = {}
    for path in sorted(source.rglob('*')):
        relative = path.relative_to(source).as_posix()
        if relative in ('.parentlock', 'lock'):
            continue
        if path.is_symlink():
            result[relative] = ('link', os.readlink(path))
        elif path.is_file():
            with path.open('rb') as stream:
                result[relative] = ('file', digest(stream))
        elif path.is_dir():
            result[relative] = ('dir', '')
    return result


def archive_backup(sources, destination, expected):
    recipients = [line.strip() for line in (HOME / '.password-store/.gpg-id').read_text().splitlines()
                  if line.strip() and not line.lstrip().startswith('#')]
    if not recipients:
        raise RuntimeError('No password-store GPG recipients found.')
    command = ['gpg', '--batch', '--yes', '--encrypt', '--output', str(destination)]
    for recipient in recipients:
        command += ['--recipient', recipient]
    def keep(member):
        locks = {f'{name}/{lock}' for name in sources for lock in ('.parentlock', 'lock')}
        return None if member.name in locks else member
    with subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL) as process:
        with tarfile.open(fileobj=process.stdin, mode='w|') as archive:
            for name, source in sources.items():
                archive.add(source, arcname=name, filter=keep)
        process.stdin.close()
        if process.wait() != 0:
            raise RuntimeError('Could not write the encrypted recovery backup.')
    destination.chmod(0o600)
    verified = {name: {} for name in sources}
    with subprocess.Popen(['gpg', '--batch', '--decrypt', str(destination)],
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
        with tarfile.open(fileobj=process.stdout, mode='r|') as archive:
            for member in archive:
                parts = member.name.split('/', 1)
                if len(parts) != 2:
                    continue
                name, relative = parts
                if member.isfile():
                    verified[name][relative] = ('file', digest(archive.extractfile(member)))
                elif member.issym():
                    verified[name][relative] = ('link', member.linkname)
                elif member.islnk():
                    target_name, target_relative = member.linkname.split('/', 1)
                    verified[name][relative] = verified[target_name][target_relative]
                elif member.isdir():
                    verified[name][relative] = ('dir', '')
        # Consume any tar padding before waiting for the decryptor to finish.
        process.stdout.read()
        if process.wait() != 0:
            raise RuntimeError('Could not verify the encrypted recovery backup.')
    if verified != expected:
        raise RuntimeError('Encrypted recovery backup verification failed.')


def main():
    os.umask(0o077)
    if CONFIG.exists():
        raise RuntimeError('Persnal vault is already configured; refusing to migrate it again.')
    if ROOT.exists():
        raise RuntimeError('A vault setup directory already exists; inspect it before retrying.')
    if not PROFILE.is_dir() or PROFILE.is_symlink():
        raise RuntimeError('Expected the original Persnal profile directory.')
    with ExitStack() as stack:
        profile_lock = stack.enter_context((PROFILE / '.parentlock').open('a+'))
        try:
            fcntl.lockf(profile_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('Close all Persnal Firefox windows before migration.') from None
        # Generate directly in memory; never print or write the unlock key in plaintext.
        entry_file = HOME / '.password-store' / (ENTRY + '.gpg')
        if not entry_file.exists():
            key = (secrets.token_urlsafe(48) + '\n').encode()
            subprocess.run(['pass', 'insert', '--multiline', ENTRY], input=key,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        result = subprocess.run(['pass', 'show', ENTRY], capture_output=True, timeout=120, check=True)
        key = result.stdout
        if not key.strip():
            raise RuntimeError('Password-store entry is empty.')
        ROOT.mkdir(parents=True, mode=0o700)
        ROOT.chmod(0o700)
        cipher, mountpoint = ROOT / 'cipher', ROOT / 'unlocked'
        cipher.mkdir(mode=0o700)
        mountpoint.mkdir(mode=0o700)
        backups = ROOT / 'backups'
        backups.mkdir(mode=0o700)
        sources = {'profile': PROFILE}
        if CACHE.is_dir():
            sources['cache'] = CACHE
        expected = {name: manifest(source) for name, source in sources.items()}
        backup = backups / ('Persnal-before-encryption-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.tar.gpg')
        print('Creating and verifying encrypted recovery backup...', flush=True)
        archive_backup(sources, backup, expected)
        config = {'name': 'Persnal', 'profile_path': str(PROFILE), 'cache_path': str(CACHE),
                  'cipher_dir': str(cipher), 'mount_dir': str(mountpoint),
                  'pass_entry': ENTRY, 'binary': str(BINARY), 'backup': str(backup)}
        def crypto(*arguments):
            subprocess.run([str(BINARY), '-q', '-nosyslog', '-passfile', '/dev/stdin', *arguments],
                           input=key, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=30, check=True)
        crypto('-init', str(cipher))
        crypto(str(cipher), str(mountpoint))
        moved = {}
        committed = False
        try:
            print('Copying profile and cache into encrypted storage...', flush=True)
            for name, source in sources.items():
                def ignore(directory, names, source=source):
                    return [name for name in names if name in ('.parentlock', 'lock')] if Path(directory) == source else []
                shutil.copytree(source, mountpoint / name, symlinks=True, ignore=ignore)
                if manifest(mountpoint / name) != expected[name]:
                    raise RuntimeError(f'Encrypted {name} content does not match the original.')
            (mountpoint / 'cache').mkdir(exist_ok=True, mode=0o700)
            if not CODE['unmount'](config):
                raise RuntimeError('Could not unmount the verified encrypted copy.')
            mountpoint.chmod(0o700)
            crypto(str(cipher), str(mountpoint))
            for name in sources:
                if manifest(mountpoint / name) != expected[name]:
                    raise RuntimeError(f'{name} changed after encrypted unmount/remount verification.')
            print('Verified encrypted content after remount; switching profile paths...', flush=True)
            for name, source in sources.items():
                staging = ROOT / ('plaintext-staging-' + name)
                source.rename(staging)
                moved[source] = staging
                source.symlink_to(mountpoint / name, target_is_directory=True)
            if 'cache' not in sources:
                CACHE.parent.mkdir(parents=True, exist_ok=True)
                CACHE.symlink_to(mountpoint / 'cache', target_is_directory=True)
            if not CODE['unmount'](config):
                raise RuntimeError('Could not lock the migrated vault.')
            temporary = CONFIG.with_suffix('.tmp')
            temporary.write_text(json.dumps(config, indent=2) + '\n')
            temporary.chmod(0o600)
            temporary.replace(CONFIG)
            committed = True
            # The verified GPG recovery archive replaces these plaintext copies.
            for staging in moved.values():
                shutil.rmtree(staging)
            print('Persnal encrypted and locked. Original files match the verified encrypted copy.', flush=True)
            print('Encrypted recovery backup:', backup, flush=True)
        finally:
            if not committed:
                for source, staging in reversed(list(moved.items())):
                    if source.is_symlink():
                        source.unlink()
                    if staging.exists():
                        staging.rename(source)
                if 'cache' not in sources and CACHE.is_symlink():
                    CACHE.unlink()
                if CODE['is_mounted'](config):
                    CODE['unmount'](config)
                print('Migration did not commit; the original profile is preserved.', flush=True)


if __name__ == '__main__':
    main()
