#!/usr/bin/python3
"""Data-driven bspwm theme switcher. Theme packs contain JSON, not executable hooks."""
import argparse
import configparser
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

HOME = Path.home()
ROOT = Path(os.environ.get('DESKTOP_THEMES_DIR', HOME / '.config/desktop-themes'))
CACHE = Path(os.environ.get('XDG_CACHE_HOME', HOME / '.cache')) / 'desktop-themes'
STATE = ROOT / 'current.json'
PREVIOUS = ROOT / 'previous.json'
COLOR_KEYS = ('bg', 'fg', 'accent', 'surface', 'muted', 'red', 'green', 'yellow',
              'blue', 'cyan', 'subtext', 'overlay', 'crust', 'mantle')
ID_RE = re.compile(r'[a-z0-9][a-z0-9_-]{0,63}\Z')
NAME_RE = re.compile(r'[A-Za-z0-9_ .+\-]{1,100}\Z')
TOKEN_RE = re.compile(r'\{\{([a-z_]+)\}\}')


def slick_greeter_session(directory=Path('/usr/share/xgreeters')):
    for name in ('slick-greeter', 'lightdm-slick-greeter'):
        if (directory / (name + '.desktop')).is_file():
            return name
    return None


def run(args, *, check=True, **kwargs):
    result = subprocess.run([str(x) for x in args], text=True, capture_output=True,
                            timeout=kwargs.pop('timeout', 30), **kwargs)
    if check and result.returncode:
        raise RuntimeError(f'{args[0]}: {(result.stderr or result.stdout).strip()}')
    return result


def atomic(path, content, mode=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    old_mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    fd, name = tempfile.mkstemp(prefix='.theme-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(content.encode() if isinstance(content, str) else content)
        os.chmod(name, old_mode if mode is None else mode)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def read_state(path=None):
    path = STATE if path is None else path
    return json.loads(path.read_text()) if path.exists() else {'id': 'catppuccin'}


def find_asset(name, kind):
    roots = [HOME / '.local/share' / kind, HOME / ('.themes' if kind == 'themes' else '.icons'),
             Path('/usr/local/share') / kind, Path('/usr/share') / kind]
    for root in roots:
        if (root / name / 'index.theme').is_file():
            return root / name
    raise ValueError(f'Missing {kind} asset: {name}')


def load_theme(theme_id):
    if not ID_RE.fullmatch(theme_id):
        raise ValueError('Theme IDs use lowercase letters, digits, hyphens and underscores.')
    directory = ROOT / 'themes' / theme_id
    theme = json.loads((directory / 'theme.json').read_text())
    override = ROOT / 'overrides' / (theme_id + '.json')
    if override.exists():
        overrides = json.loads(override.read_text())
        if not isinstance(overrides, dict) or set(overrides) - {'wallpaper'}:
            raise ValueError(f'{theme_id}: wallpaper override must contain only wallpaper')
        if 'wallpaper' in overrides and (not isinstance(overrides['wallpaper'], str) or not overrides['wallpaper']):
            raise ValueError(f'{theme_id}: wallpaper override must be a nonempty path')
        theme.update(overrides)
    name = theme.get('name', '')
    if not isinstance(name, str) or not name.strip() or len(name) > 80 or any(ord(c) < 32 for c in name):
        raise ValueError(f'{theme_id}: invalid display name')
    if not isinstance(theme.get('colors'), dict):
        raise ValueError(f'{theme_id}: colors must be an object')
    for key in COLOR_KEYS:
        color = theme['colors'].get(key)
        if not isinstance(color, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', color):
            raise ValueError(f'{theme_id}: colors.{key} must be #RRGGBB')
    for key in ('gtk', 'icons', 'cursor', 'ui_font', 'mono_font'):
        if not isinstance(theme.get(key), str) or not NAME_RE.fullmatch(theme[key]):
            raise ValueError(f'{theme_id}: invalid or missing {key}')
    for key in ('gtk', 'icons', 'cursor'):
        find_asset(theme[key], 'themes' if key == 'gtk' else 'icons')
    size = theme.get('cursor_size', 24)
    if type(size) is not int or not 16 <= size <= 96:
        raise ValueError('cursor_size must be an integer from 16 to 96')
    opacity = theme.get('opacity', 0.94)
    if type(opacity) not in (float, int) or not 0.5 <= opacity <= 1:
        raise ValueError('opacity must be between 0.5 and 1')
    if theme.get('mode', 'dark') not in ('light', 'dark'):
        raise ValueError('mode must be light or dark')
    for key, default, maximum in (('window_gap', 12, 40), ('border_width', 2, 8), ('ui_font_size', 10, 24)):
        value = theme.get(key, default)
        if type(value) is not int or not 0 <= value <= maximum:
            raise ValueError(f'{key} must be an integer from 0 to {maximum}')
    wallpaper = Path(theme.get('wallpaper', 'wallpaper.png')).expanduser()
    if not wallpaper.is_absolute():
        wallpaper = directory / wallpaper
    if not wallpaper.is_file():
        raise ValueError(f'{theme_id}: missing wallpaper {wallpaper}')
    theme.update(id=theme_id, wallpaper=str(wallpaper.resolve()), cursor_size=size, opacity=opacity)
    return theme


def themes():
    result = []
    for path in sorted((ROOT / 'themes').glob('*/theme.json')):
        try:
            result.append(load_theme(path.parent.name))
        except (ValueError, OSError) as error:
            print(f'Skipping {path.parent.name}: {error}', file=sys.stderr)
    names = [t['name'] for t in result]
    if len(set(names)) != len(names):
        raise ValueError('Each theme needs a unique display name.')
    return result


def render(theme):
    values = dict(theme['colors'])
    values.update({k: str(theme[k]) for k in ('gtk', 'icons', 'cursor', 'cursor_size',
                                             'ui_font', 'mono_font', 'opacity')})
    values.update({k + '_hex': v[1:] for k, v in theme['colors'].items()})
    values['prefer_dark'] = 'false' if theme.get('mode') == 'light' else 'true'
    values['mode'] = theme.get('mode', 'dark')
    files = {}
    templates = {p.relative_to(ROOT / 'templates'): p
                 for p in (ROOT / 'templates').rglob('*.tmpl')}
    overrides = ROOT / 'themes' / theme['id'] / 'templates'
    templates.update({p.relative_to(overrides): p for p in overrides.rglob('*.tmpl')})
    for rel, template in sorted(templates.items()):
        target = HOME / str(rel)[:-5]
        def replace(match):
            key = match[1]
            if key not in values:
                raise ValueError(f'Unknown template token {key} in {template}')
            return values[key]
        files[target] = TOKEN_RE.sub(replace, template.read_text())
    if not files:
        raise ValueError('No configuration templates found.')
    # Reject broken terminal/GTK configuration before changing any file.
    import tomllib
    for path, content in files.items():
        if path.suffix == '.toml':
            tomllib.loads(content)
        elif path.name == 'settings.ini':
            parser = configparser.ConfigParser(interpolation=None)
            parser.read_string(content)
    return files


def ensure_display():
    if not os.environ.get('DISPLAY') or run(['xset', 'q'], check=False).returncode:
        raise RuntimeError('Run this from your graphical desktop terminal (cannot access the X display).')


def lock_cache(theme):
    import hashlib
    screen = run(['xrandr', '--current']).stdout
    geometry = '\n'.join(line for line in screen.splitlines()
                         if ' connected' in line or line.startswith('Screen '))
    digest = hashlib.sha256(Path(theme['wallpaper']).read_bytes() + geometry.encode()).hexdigest()[:16]
    dest = CACHE / theme['id'] / digest
    if (dest / 'lock_dimblur.png').is_file():
        return dest
    CACHE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='prepare-', dir=CACHE) as temp:
        env = dict(os.environ, XDG_CACHE_HOME=temp)
        run(['betterlockscreen', '-u', theme['wallpaper'], '--fx', 'dimblur'], env=env, timeout=180)
        generated = Path(temp) / 'betterlockscreen/current'
        if not (generated / 'lock_dimblur.png').is_file():
            raise RuntimeError('Betterlockscreen did not generate the lock wallpaper.')
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(generated, dest, dirs_exist_ok=True)
    return dest


def refresh(theme):
    warnings = []
    def attempt(args):
        if not shutil.which(str(args[0])):
            return
        try:
            result = run(args, check=False)
            if result.returncode:
                warnings.append(f'{args[0]}: {result.stderr.strip()}')
        except (OSError, subprocess.TimeoutExpired) as error:
            warnings.append(str(error))
    properties = {'/Net/ThemeName': ('string', theme['gtk']),
                  '/Net/IconThemeName': ('string', theme['icons']),
                  '/Gtk/FontName': ('string', theme['ui_font'] + ' ' + str(theme.get('ui_font_size', 10))),
                  '/Gtk/MonospaceFontName': ('string', theme['mono_font'] + ' 10'),
                  '/Gtk/CursorThemeName': ('string', theme['cursor']),
                  '/Gtk/CursorThemeSize': ('int', str(theme['cursor_size']))}
    if shutil.which('xfconf-query'):
        for prop, (kind, value) in properties.items():
            result = run(['xfconf-query', '-c', 'xsettings', '-p', prop, '-s', value], check=False)
            if result.returncode:
                attempt(['xfconf-query', '-c', 'xsettings', '-p', prop, '-n', '-t', kind, '-s', value])
    if shutil.which('xfsettingsd') and run(['pgrep', '-u', str(os.getuid()), '-x', 'xfsettingsd'], check=False).returncode:
        subprocess.Popen(['xfsettingsd'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
    for key, value in {'gtk-theme': theme['gtk'], 'icon-theme': theme['icons'],
                       'cursor-theme': theme['cursor'],
                       'color-scheme': 'prefer-light' if theme.get('mode') == 'light' else 'prefer-dark'}.items():
        attempt(['gsettings', 'set', 'org.gnome.desktop.interface', key, value])
    colors = theme['colors']
    for key, value in {'normal_border_color': colors['surface'], 'focused_border_color': colors['accent'],
                       'active_border_color': colors['blue'], 'presel_feedback_color': colors['green']}.items():
        attempt(['bspc', 'config', key, value])
    for key, default in (('border_width', 2), ('window_gap', 12)):
        attempt(['bspc', 'config', key, str(theme.get(key, default))])
    attempt(['xrdb', '-merge', HOME / '.Xresources'])
    attempt(['xsetroot', '-cursor_name', 'left_ptr'])
    return warnings


def apply(theme, *, reload=True, extra_files=None, remember_previous=True):
    ensure_display()
    for binary in ('betterlockscreen', 'feh', 'xrandr'):
        if not shutil.which(binary):
            raise ValueError(f'Install {binary} before switching themes.')
    files = render(theme)
    files.update(extra_files or {})
    prepared = lock_cache(theme)  # Expensive preparation happens before changing settings.
    live_cache = Path(os.environ.get('XDG_CACHE_HOME', HOME / '.cache')) / 'betterlockscreen/current'
    for image in prepared.glob('*.png'):
        files[live_cache / image.name] = image.read_bytes()
    # Preserve unrelated Xresources and update just the cursor settings.
    xr = HOME / '.Xresources'
    resource = xr.read_text() if xr.exists() else ''
    resource = re.sub(r'^Xcursor\.(theme|size):.*\n?', '', resource, flags=re.M)
    resource = re.sub(r'^sxiv\.(background|foreground|font):.*\n?', '', resource, flags=re.M)
    files[xr] = resource.rstrip() + f'\nXcursor.theme: {theme["cursor"]}\nXcursor.size: {theme["cursor_size"]}\n'
    files[xr] += (f'sxiv.background: {theme["colors"]["bg"]}\n'
                  f'sxiv.foreground: {theme["colors"]["fg"]}\n'
                  f'sxiv.font: {theme["mono_font"]}:size=11\n')
    old = read_state()
    if remember_previous and old.get('id') != theme['id']:
        files[PREVIOUS] = json.dumps(old, indent=2) + '\n'
    files[STATE] = json.dumps(theme, indent=2) + '\n'
    snapshot = {path: (path.read_bytes() if path.exists() else None) for path in files}
    saved = CACHE / 'last-transaction'
    if saved.exists():
        shutil.rmtree(saved)
    saved.mkdir(parents=True)
    manifest = []
    for index, (path, content) in enumerate(snapshot.items()):
        if content is not None:
            (saved / str(index)).write_bytes(content)
        manifest.append({'path': str(path), 'file': str(index) if content is not None else None})
    atomic(saved / 'manifest.json', json.dumps(manifest, indent=2))
    try:
        for path, content in files.items():
            atomic(path, content)
        run(['feh', '--no-fehbg', '--bg-fill', theme['wallpaper']])
    except Exception:
        for path, content in snapshot.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                atomic(path, content)
        raise
    warnings = refresh(theme)
    if reload:
        for command in (['setsid', '-f', str(HOME / '.local/bin/polybar-launch')], ['dunstctl', 'reload']):
            try:
                result = run(command, check=False)
                if result.returncode:
                    warnings.append(f'{command[0]}: {result.stderr.strip()}')
            except (OSError, subprocess.TimeoutExpired) as error:
                warnings.append(str(error))
        compositor = HOME / '.local/bin/bspwm-compositor'
        if compositor.is_file():
            try:
                run(['pkill', '-u', str(os.getuid()), '-x', 'picom'], check=False)
                # Allow X to release the compositor selection. Waiting on pgrep
                # can hang on already exited children awaiting their parent.
                time.sleep(0.3)
                run(['sh', '-c', 'setsid -f "$HOME/.local/bin/bspwm-compositor" '
                     '>/dev/null 2>&1 </dev/null'], check=False)
            except (OSError, subprocess.TimeoutExpired) as error:
                warnings.append(str(error))
    print(f'Applied {theme["name"]}')
    for warning in warnings:
        print('Refresh warning: ' + warning, file=sys.stderr)
    if shutil.which('notify-send'):
        run(['notify-send', 'Desktop theme', theme['name'] + ' applied'], check=False)


def menu():
    available = themes()
    labels = {theme['name']: theme for theme in available}
    action = 'Sync current theme to login screen (sudo)'
    result = run([HOME / '.local/bin/desktop-menu', '-p', 'Theme'],
                 input='\n'.join([*labels, action]) + '\n', check=False)
    if result.returncode or not result.stdout.strip():
        return None
    selected = result.stdout.strip()
    if selected == action:
        subprocess.Popen(['kitty', '--hold', '--title', 'Apply login theme', '-e',
                          str(HOME / '.local/bin/desktop-theme'), '--sync-login'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        return None
    if selected not in labels:
        raise ValueError('Choose a theme from the list.')
    return labels[selected]


def set_wallpaper(source):
    """Pin a validated image and transactionally save its per-theme override."""
    import hashlib
    import gi
    gi.require_version('GdkPixbuf', '2.0')
    from gi.repository import GdkPixbuf
    source = Path(source).expanduser().resolve(strict=True)
    if not source.is_file():
        raise ValueError('Choose an image file.')
    # Decode before any theme state changes; GIFs become a static first frame.
    try:
        image = GdkPixbuf.Pixbuf.new_from_file(str(source))
    except Exception as error:
        raise ValueError(f'Cannot use this image as a wallpaper: {error}') from error
    theme = load_theme(read_state()['id'])
    digest = hashlib.sha256(source.read_bytes()).hexdigest()[:24]
    dest = ROOT / 'wallpapers' / theme['id'] / (digest + '.png')
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Generated copy keeps the selection available after moving the source.
        with tempfile.NamedTemporaryFile(suffix='.png', dir=dest.parent) as temp:
            image.savev(temp.name, 'png', [], [])
            atomic(dest, Path(temp.name).read_bytes())
    theme['wallpaper'] = str(dest)
    override = ROOT / 'overrides' / (theme['id'] + '.json')
    apply(theme, remember_previous=False,
          extra_files={override: json.dumps({'wallpaper': str(dest)}, indent=2) + '\n'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument('--list', action='store_true')
    actions.add_argument('--apply', metavar='ID')
    actions.add_argument('--check', metavar='ID')
    actions.add_argument('--build-assets', metavar='ID')
    actions.add_argument('--current', action='store_true')
    actions.add_argument('--previous', action='store_true')
    actions.add_argument('--refresh', action='store_true')
    actions.add_argument('--wallpaper', action='store_true')
    actions.add_argument('--lock-for-suspend', action='store_true')
    actions.add_argument('--sync-login', action='store_true')
    actions.add_argument('--set-wallpaper', metavar='IMAGE')
    args = parser.parse_args()
    if args.build_assets:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import build_presets
        build_presets.HOME = HOME
        build_presets.ROOT = ROOT
        build_presets.build_custom(args.build_assets)
        render(load_theme(args.build_assets))
        return
    if args.list:
        for theme in themes():
            print(f'{theme["id"]}\t{theme["name"]}')
        return
    if args.current:
        print(read_state()['id'])
        return
    if args.wallpaper:
        print(load_theme(read_state()['id'])['wallpaper'])
        return
    if args.lock_for_suspend:
        theme = load_theme(read_state()['id'])
        colors = theme['colors']
        image = Path(os.environ.get('XDG_CACHE_HOME', HOME / '.cache')) / 'betterlockscreen/current/lock_dimblur.png'
        if not image.is_file():
            raise ValueError('Apply a theme before using suspend locking.')
        run(['i3lock', '--image', image, '--color', colors['bg'][1:], '--clock',
             '--ring-color', colors['accent'][1:] + 'ff',
             '--inside-color', colors['bg'][1:] + '66',
             '--time-color', colors['fg'][1:] + 'ff'])
        return
    if args.check:
        render(load_theme(args.check))
        print(f'{args.check}: metadata, assets and templates are valid')
        return
    if args.sync_login:
        theme = load_theme(read_state()['id'])
        # Root helper only copies assets to fixed destinations; no hooks are executed.
        subprocess.run(['sudo', '/usr/bin/python3', str(Path(__file__).resolve().with_name('sync_login.py')),
                        str(ROOT), theme['id']], check=True)
        return
    if args.refresh:
        ensure_display()
        for warning in refresh(load_theme(read_state()['id'])):
            print(warning, file=sys.stderr)
        return
    ROOT.mkdir(parents=True, exist_ok=True)
    with (ROOT / '.switch.lock').open('w') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('Another theme switcher is already open.')
        if args.set_wallpaper:
            set_wallpaper(args.set_wallpaper)
            return
        if args.apply:
            theme = load_theme(args.apply)
        elif args.previous:
            if not PREVIOUS.exists():
                raise ValueError('No previous theme has been saved yet.')
            theme = load_theme(read_state(PREVIOUS)['id'])
        else:
            theme = menu()
        if theme:
            apply(theme)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f'Theme switch failed: {error}', file=sys.stderr)
        if os.environ.get('DISPLAY') and shutil.which('notify-send'):
            try:
                run(['notify-send', '-u', 'critical', 'Theme switch failed', str(error)], check=False)
            except Exception:
                pass
        sys.exit(1)
