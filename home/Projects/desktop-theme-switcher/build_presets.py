#!/usr/bin/python3
"""Build local palette variants from the installed Catppuccin GTK/Papirus assets."""
from pathlib import Path
import json
import re
import shutil
import sys

import gi
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf

HOME = Path.home()
ROOT = HOME / '.config/desktop-themes'
KEYS = 'bg fg accent surface muted red green yellow blue cyan subtext overlay crust mantle'.split()
PALETTES = {
    'catppuccin': ('Catppuccin Mocha', '1e1e2e cdd6f4 cba6f7 313244 585b70 f38ba8 a6e3a1 f9e2af 89b4fa 94e2d5 a6adc8 45475a 11111b 181825'),
    'tokyo-night': ('Tokyo Night', '1a1b26 c0caf5 bb9af7 24283b 565f89 f7768e 9ece6a e0af68 7aa2f7 7dcfff a9b1d6 414868 15161e 16161e'),
    'nord': ('Nord', '2e3440 eceff4 88c0d0 3b4252 616e88 bf616a a3be8c ebcb8b 81a1c1 8fbcbb d8dee9 4c566a 242933 272d38'),
    'gruvbox': ('Gruvbox Material', '282828 d4be98 d8a657 32302f 7c6f64 ea6962 a9b665 d8a657 7daea3 89b482 bdae93 504945 1d2021 242424'),
    'rose-pine': ('Rosé Pine', '191724 e0def4 c4a7e7 26233a 6e6a86 eb6f92 9ccfd8 f6c177 31748f 9ccfd8 908caa 403d52 12101b 1f1d2e'),
}


def recolor(text, colors):
    original = dict(zip(KEYS, PALETTES['catppuccin'][1].split()))
    mapping = {old: colors[key][1:] for key, old in original.items()}
    mapping.update({'bac2de': colors['subtext'][1:], '9399b2': colors['muted'][1:],
                    '6c7086': colors['muted'][1:], 'fab387': colors['yellow'][1:],
                    'f5c2e7': colors['accent'][1:], 'f2cdcd': colors['red'][1:],
                    'f5e0dc': colors['fg'][1:], '74c7ec': colors['cyan'][1:],
                    '89dceb': colors['cyan'][1:], 'b4befe': colors['accent'][1:],
                    'eba0ac': colors['red'][1:]})
    text = re.sub(r'#([0-9a-fA-F]{6})(?![0-9a-fA-F])',
                  lambda m: '#' + mapping.get(m[1].lower(), m[1]), text)
    rgbmap = {tuple(int(old[i:i+2], 16) for i in (0, 2, 4)):
              tuple(int(new[i:i+2], 16) for i in (0, 2, 4)) for old, new in mapping.items()}
    def rgb(match):
        old = tuple(int(match[i]) for i in (2, 3, 4))
        new = rgbmap.get(old, old)
        return f'{match[1]}({new[0]}, {new[1]}, {new[2]}'
    return re.sub(r'\b(rgba?)\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', rgb, text)


def wallpaper(directory, c):
    # Native SVG artwork: layered hills, a moon and sparse stars.
    stars = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c["fg"]}" opacity=".35"/>'
                    for x, y, r in [(190,145,2),(470,260,2),(860,120,3),(1170,310,2),
                                    (1550,180,2),(2100,200,2),(2350,410,3),(650,420,2)])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="2560" height="1440" viewBox="0 0 2560 1440">
<defs><linearGradient id="sky" x2="0" y2="1"><stop stop-color="{c['crust']}"/>
<stop offset="1" stop-color="{c['surface']}"/></linearGradient>
<radialGradient id="glow"><stop stop-color="{c['accent']}" stop-opacity=".2"/>
<stop offset="1" stop-color="{c['accent']}" stop-opacity="0"/></radialGradient></defs>
<rect width="2560" height="1440" fill="url(#sky)"/>
<circle cx="1850" cy="410" r="500" fill="url(#glow)"/>
{stars}<circle cx="1850" cy="410" r="94" fill="{c['accent']}"/>
<path d="M0 950 Q350 630 760 900 T1530 790 T2560 850 V1440 H0Z" fill="{c['muted']}" opacity=".45"/>
<path d="M0 1100 Q460 800 970 1050 T1780 980 T2560 1040 V1440 H0Z" fill="{c['surface']}"/>
<path d="M0 1230 Q550 1010 1100 1210 T2000 1140 T2560 1200 V1440 H0Z" fill="{c['mantle']}"/>
<path d="M0 1370 Q600 1200 1320 1360 T2560 1280 V1440 H0Z" fill="{c['crust']}"/>
</svg>'''
    (directory / 'wallpaper.svg').write_text(svg)
    pix = GdkPixbuf.Pixbuf.new_from_file(str(directory / 'wallpaper.svg'))
    pix.savev(str(directory / 'wallpaper.png'), 'png', [], [])


def icons(theme_id, c):
    dest = HOME / '.local/share/icons' / ('Desktop-' + theme_id)
    dest.mkdir(parents=True, exist_ok=True)
    sections = []
    # Override folder/place icons; all application icons inherit Papirus-Dark.
    for size in (16, 22, 24, 32, 48, 64):
        source = Path('/usr/share/icons/Papirus') / f'{size}x{size}/places'
        target = dest / f'{size}x{size}/places'
        target.mkdir(parents=True, exist_ok=True)
        for file in source.glob('*.svg'):
            if not (file.name.startswith(('folder', 'user-')) or file.name == 'desktop.svg'):
                continue
            if file.name.startswith('folder-') and not file.is_symlink():
                continue  # Skip hundreds of alternative colour variants.
            text = file.read_text()
            # Papirus blue folder shades, replaced without changing emblems.
            shades = {'4877b1': c['accent'], '5294e2': c['accent'], '1d344f': c['surface'],
                      '1e5aa6': c['surface'], '3b7dda': c['blue'], '4f83c2': c['accent'],
                      '5c9ce6': c['accent'], '5c9ded': c['accent'], '2e6bc0': c['blue']}
            text = re.sub(r'#([0-9a-fA-F]{6})(?![0-9a-fA-F])',
                          lambda m: shades.get(m[1].lower(), m[0]), text)
            (target / file.name).write_text(text)
        sections.append(f'[{size}x{size}/places]\nSize={size}\nContext=Places\nType=Fixed\n')
    (dest / 'index.theme').write_text('[Icon Theme]\nName=Desktop-' + theme_id +
        '\nInherits=Papirus-Dark,hicolor\nDirectories=' +
        ','.join(f'{s}x{s}/places' for s in (16,22,24,32,48,64)) + '\n\n' + '\n'.join(sections))


def build():
    source = HOME / '.local/share/themes/catppuccin-mocha-mauve-standard+default'
    if not (source / 'gtk-3.0/gtk.css').exists():
        raise SystemExit('The existing Catppuccin GTK theme is required to build these presets.')
    for theme_id, (name, palette) in PALETTES.items():
        c = dict(zip(KEYS, ['#' + v for v in palette.split()]))
        directory = ROOT / 'themes' / theme_id
        directory.mkdir(parents=True, exist_ok=True)
        gtk = 'Desktop-' + theme_id
        dest = HOME / '.local/share/themes' / gtk
        shutil.copytree(source, dest, dirs_exist_ok=True)
        for path in dest.rglob('*'):
            if path.is_file() and path.suffix in ('.css', '.svg', '.theme', '.rc'):
                path.write_text(recolor(path.read_text(), c))
        (dest / 'index.theme').write_text(f'[Desktop Entry]\nType=X-GNOME-Metatheme\nName={gtk}\n\n[X-GNOME-Metatheme]\nGtkTheme={gtk}\nIconTheme=Desktop-{theme_id}\n')
        icons(theme_id, c)
        wallpaper(directory, c)
        data = {'name': name, 'colors': c, 'gtk': gtk, 'icons': 'Desktop-' + theme_id,
                'cursor': 'Bibata-Modern-Ice', 'cursor_size': 24, 'ui_font': 'Inter',
                'mono_font': 'DejaVu Sans Mono', 'opacity': 0.94, 'wallpaper': 'wallpaper.png'}
        if theme_id in ('gruvbox', 'rose-pine'):
            data['cursor'] = 'Bibata-Modern-Amber'
        elif theme_id in ('nord', 'tokyo-night'):
            data['cursor'] = 'Bibata-Modern-Classic'
        if theme_id == 'catppuccin':
            shutil.copy2(HOME / 'Pictures/Wallpapers/purple-horizon.jpg', directory / 'wallpaper.jpg')
            data['wallpaper'] = 'wallpaper.jpg'
        (directory / 'theme.json').write_text(json.dumps(data, indent=2) + '\n')
        print('Built', name)


def build_custom(theme_id):
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}', theme_id):
        raise ValueError('Invalid theme ID')
    directory = ROOT / 'themes' / theme_id
    data = json.loads((directory / 'theme.json').read_text())
    c = data['colors']
    for key in KEYS:
        if not isinstance(c.get(key), str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', c[key]):
            raise ValueError(f'colors.{key} must be #RRGGBB')
    source = HOME / '.local/share/themes/catppuccin-mocha-mauve-standard+default'
    dest = HOME / '.local/share/themes' / ('Desktop-' + theme_id)
    shutil.copytree(source, dest, dirs_exist_ok=True)
    for path in dest.rglob('*'):
        if path.is_file() and path.suffix in ('.css', '.svg', '.theme', '.rc'):
            path.write_text(recolor(path.read_text(), c))
    gtk = 'Desktop-' + theme_id
    (dest / 'index.theme').write_text(f'[Desktop Entry]\nType=X-GNOME-Metatheme\nName={gtk}\n\n[X-GNOME-Metatheme]\nGtkTheme={gtk}\n')
    icons(theme_id, c)
    data.update(gtk=gtk, icons=gtk)
    if data.get('mode') == 'light':
        index = HOME / '.local/share/icons' / gtk / 'index.theme'
        index.write_text(index.read_text().replace('Papirus-Dark,hicolor', 'Papirus-Light,Papirus,hicolor'))
    if data.get('wallpaper', 'wallpaper.png') == 'wallpaper.png':
        wallpaper(directory, c)
    (directory / 'theme.json').write_text(json.dumps(data, indent=2) + '\n')
    print(f'Built GTK theme, folder icons and wallpaper for {theme_id}')


if __name__ == '__main__':
    build()
