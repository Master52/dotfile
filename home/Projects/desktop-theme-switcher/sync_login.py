#!/usr/bin/python3
"""Explicit, authenticated sync of the chosen theme to LightDM."""
import importlib.util
import json
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import sys
import time

if os.geteuid() != 0 or 'SUDO_UID' not in os.environ:
    raise SystemExit('Run desktop-theme --sync-login as your normal user.')
user_home = Path(pwd.getpwuid(int(os.environ['SUDO_UID'])).pw_dir)
spec = importlib.util.spec_from_file_location('switcher', Path(__file__).with_name('theme_switcher.py'))
switcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(switcher)
switcher.HOME = user_home
switcher.ROOT = Path(sys.argv[1])
theme = switcher.load_theme(sys.argv[2])
greeter = switcher.slick_greeter_session()
if greeter is None:
    subprocess.run(['xbps-install', '-y', 'lightdm-slick-greeter'], check=True)
    greeter = switcher.slick_greeter_session()
if greeter is None:
    raise SystemExit('No Slick Greeter session file was found in /usr/share/xgreeters.')
backup = Path('/etc/lightdm') / time.strftime('theme-backup-%Y%m%d-%H%M%S')
backup.mkdir(parents=True)
for path in (Path('/etc/lightdm/slick-greeter.conf'), Path('/etc/lightdm/lightdm.conf.d/90-desktop-rice.conf')):
    if path.exists():
        shutil.copy2(path, backup / path.name)
for key, kind in (('gtk', 'themes'), ('icons', 'icons'), ('cursor', 'icons')):
    src = switcher.find_asset(theme[key], kind)
    dest = Path('/usr/local/share') / kind / theme[key]
    shutil.copytree(src, dest, dirs_exist_ok=True)
    for path in [dest, *dest.rglob('*')]:
        if not path.is_symlink():
            path.chmod(0o755 if path.is_dir() else 0o644)
wall = Path('/usr/local/share/backgrounds/desktop-theme' + Path(theme['wallpaper']).suffix)
wall.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(theme['wallpaper'], wall)
wall.chmod(0o644)
conf = f'''[Greeter]
background={wall}
background-color={theme['colors']['bg']}
draw-user-backgrounds=false
draw-grid=false
theme-name={theme['gtk']}
icon-theme-name={theme['icons']}
font-name={theme['ui_font']} 11
show-hostname=false
show-clock=true
show-power=true
show-keyboard=true
clock-format=%H:%M
'''
switcher.atomic(Path('/etc/lightdm/slick-greeter.conf'), conf)
switcher.atomic(Path('/etc/lightdm/lightdm.conf.d/90-desktop-rice.conf'),
                f'[Seat:*]\ngreeter-session={greeter}\n')
print(f'Login screen updated to {theme["name"]}. It takes effect at your next login.')
print(f'Previous login configuration: {backup}')
