#!/usr/bin/python3
"""Per-user Transmission service, terminal launcher and safe file/magnet handler."""
import base64
import configparser
import fcntl
import html
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HOME = Path.home()
CONFIG = HOME / '.config/torrent-client'
DAEMON_CONFIG = HOME / '.config/transmission-daemon'
CACHE = HOME / '.cache/torrent-client'
DOWNLOADS = HOME / 'Downloads'
BIN = HOME / '.local/bin'
CLIENT = CONFIG / 'client.json'


def notify(title, body, urgent=False):
    text = ''.join(c for c in str(body) if c >= ' ' or c == '\n')[:400]
    try:
        subprocess.run(['notify-send', '-a', 'Torrents', '-i', 'folder-download',
                        '-u', 'critical' if urgent else 'normal', '--', title, html.escape(text)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5, check=False)
    except (OSError, subprocess.TimeoutExpired):
        pass


class RPC:
    def __init__(self):
        info = json.loads(CLIENT.read_text())
        self.url = 'http://127.0.0.1:9091/transmission/rpc'
        self.auth = 'Basic ' + base64.b64encode((info['username'] + ':' + info['password']).encode()).decode()
        self.session = ''
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def call(self, method, arguments=None):
        data = json.dumps({'method': method, 'arguments': arguments or {}}).encode()
        for _ in range(2):
            request = urllib.request.Request(self.url, data=data, headers={
                'Authorization': self.auth, 'Content-Type': 'application/json',
                'X-Transmission-Session-Id': self.session})
            try:
                with self.opener.open(request, timeout=5) as response:
                    result = json.load(response)
                if result.get('result') != 'success':
                    raise RuntimeError('Transmission could not complete that request')
                return result.get('arguments', {})
            except urllib.error.HTTPError as error:
                if error.code != 409:
                    raise
                self.session = error.headers['X-Transmission-Session-Id']
        raise RuntimeError('Transmission session negotiation failed')


def ensure_service():
    rpc = RPC()
    try:
        rpc.call('session-get')
        return rpc
    except (OSError, RuntimeError):
        pass
    CACHE.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (CACHE / 'service.log').open('a') as logfile:
        subprocess.Popen([str(BIN / 'torrent-background')], start_new_session=True,
                         stdin=subprocess.DEVNULL, stdout=logfile, stderr=logfile)
    deadline = time.monotonic() + 12
    while time.monotonic() < deadline:
        try:
            rpc.call('session-get')
            return rpc
        except (OSError, RuntimeError):
            time.sleep(.2)
    raise RuntimeError('Torrent service could not start; see ~/.cache/torrent-client/service.log')


def serve():
    CACHE.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (CACHE / 'service.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        env = dict(os.environ, TR_SAVE_VERSION_FORMAT='5')
        daemon = subprocess.Popen(['transmission-daemon', '--foreground', '--config-dir', str(DAEMON_CONFIG),
                                   '--log-level=error'], env=env, stdin=subprocess.DEVNULL)
        signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
        errors = {}
        try:
            rpc = RPC()
            while daemon.poll() is None:
                time.sleep(5)
                try:
                    torrents = rpc.call('torrent-get', {'fields': ['id', 'name', 'error', 'errorString']}).get('torrents', [])
                    current = {t['id']: t.get('errorString', '') for t in torrents if t.get('error')}
                    for torrent in torrents:
                        key = torrent['id']
                        if key in current and current[key] != errors.get(key):
                            notify('Torrent needs attention', torrent['name'] + '\nOpen Win+T for details.', True)
                    errors = current
                except (OSError, RuntimeError):
                    pass
        finally:
            if daemon.poll() is None:
                daemon.terminate()
                try:
                    daemon.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    daemon.kill()
                    daemon.wait()


def add(rpc, value):
    parsed = urllib.parse.urlsplit(value)
    arguments = {'download-dir': str(DOWNLOADS), 'paused': False}
    if parsed.scheme.lower() == 'magnet':
        arguments['filename'] = value
    else:
        if parsed.scheme.lower() == 'file':
            if parsed.netloc not in ('', 'localhost'):
                raise ValueError('Only local torrent files are supported')
            path = Path(urllib.parse.unquote(parsed.path))
        elif parsed.scheme:
            raise ValueError('Choose a local .torrent file or a magnet link')
        else:
            path = Path(value).expanduser()
        if not path.is_file() or path.stat().st_size > 32 * 1024 * 1024:
            raise ValueError('Choose a valid torrent file smaller than 32 MB')
        arguments['metainfo'] = base64.b64encode(path.read_bytes()).decode()
    result = rpc.call('torrent-add', arguments)
    torrent = result.get('torrent-added') or result.get('torrent-duplicate')
    if not torrent:
        raise RuntimeError('Transmission did not accept this torrent')
    notify('Torrent already added' if 'torrent-duplicate' in result else 'Torrent added',
           torrent['name'] + '\nSaving to ' + str(DOWNLOADS))
    return torrent


def focus_existing():
    result = subprocess.run(['bspc', 'query', '-N'], capture_output=True, text=True, check=False)
    for window in result.stdout.splitlines():
        prop = subprocess.run(['xprop', '-id', window, 'WM_CLASS'], capture_output=True, text=True, check=False)
        if '"Torrents"' in prop.stdout:
            subprocess.run(['bspc', 'node', window, '-f'], check=False)
            return True
    return False


def open_ui():
    if focus_existing():
        return
    subprocess.Popen([str(BIN / 'kitty'), '--class', 'Torrents', '--title', 'Torrents',
                      '--directory', str(DOWNLOADS), '/usr/bin/python3', __file__, 'tui'],
                     start_new_session=True, stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def tui():
    ensure_service()
    with (CACHE / 'ui.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        # Keep this process/lock alive while tremc runs. q only closes the client.
        subprocess.run(['tremc', '-f', str(HOME / '.config/tremc/settings.cfg')], check=False)


def menu():
    choices = ['Open torrent client', 'Add magnet link', 'Add torrent file',
               'Open Downloads', 'Pause all torrents', 'Resume all torrents']
    pick = subprocess.run([str(BIN / 'desktop-menu'), '-p', 'Torrents'],
                          input='\n'.join(choices) + '\n', text=True, capture_output=True)
    if pick.returncode or not pick.stdout.strip():
        return
    choice = pick.stdout.strip()
    if choice == choices[0]:
        ensure_service(); open_ui()
    elif choice in choices[1:3]:
        command = (['zenity', '--entry', '--title=Torrents', '--text=Paste a magnet link:']
                   if choice == choices[1] else
                   ['zenity', '--file-selection', '--title=Add torrent', '--file-filter=Torrent files | *.torrent',
                    '--filename=' + str(DOWNLOADS) + '/'])
        selected = subprocess.run(command, capture_output=True, text=True)
        if selected.returncode == 0 and selected.stdout.strip():
            add(ensure_service(), selected.stdout.strip()); open_ui()
    elif choice == choices[3]:
        subprocess.Popen([str(BIN / 'file-manager'), str(DOWNLOADS)], start_new_session=True)
    elif choice in choices[4:]:
        ensure_service().call('torrent-stop' if choice == choices[4] else 'torrent-start')
        notify('Torrents', 'All torrents paused.' if choice == choices[4] else 'All torrents resumed.')


def main():
    os.umask(0o077)
    mode = sys.argv[1] if len(sys.argv) > 1 else 'open'
    if mode == 'serve':
        serve()
    elif mode == 'done':
        notify('Download complete', os.environ.get('TR_TORRENT_NAME', 'Torrent') + '\nSaved in ' +
               os.environ.get('TR_TORRENT_DIR', str(DOWNLOADS)))
    elif mode == 'menu':
        menu()
    elif mode == 'tui':
        tui()
    elif mode == 'open':
        rpc = ensure_service()
        for value in sys.argv[2:]:
            add(rpc, value)
        open_ui()
    elif mode == 'status':
        info = ensure_service().call('session-get')
        print('Transmission ready; default download directory:', info.get('download-dir'))
    else:
        raise ValueError('Unknown torrent action')


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, ValueError) as error:
        notify('Torrent action failed', str(error), True)
        raise SystemExit(1)
