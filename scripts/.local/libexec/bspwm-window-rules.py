#!/usr/bin/python3
"""Place dialogs and small utilities without changing normal app tiling."""
import json
import re
import subprocess
import sys


def output(args):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=1)
        return r.stdout if r.returncode == 0 else ''
    except (OSError, subprocess.TimeoutExpired):
        return ''


def consequences(window, class_name, instance, existing):
    props = output(['xprop', '-id', window, '_NET_WM_WINDOW_TYPE', 'WM_TRANSIENT_FOR', '_NET_WM_STATE'])
    dialog = ('_NET_WM_WINDOW_TYPE_DIALOG' in props or
              '_NET_WM_STATE_MODAL' in props or
              bool(re.search(r'WM_TRANSIENT_FOR.*window id # 0x[1-9a-fA-F]', props)))
    utility_type = '_NET_WM_WINDOW_TYPE_UTILITY' in props
    sizes = {
        'pavucontrol': (760, 500),
        'nm-connection-editor': (720, 500),
        'blueman-manager': (720, 480),
        'blueman-adapters': (600, 420),
        'gcr-prompter': (480, 320),
        'polkit-gnome-authentication-agent-1': (480, 320),
        'xfce-polkit': (480, 320),
    }
    size = sizes.get(class_name.casefold()) or sizes.get(instance.casefold())
    if class_name == 'DesktopLauncher':
        return 'state=floating center=on border=off'
    if not (dialog or utility_type or size):
        return ''
    result = 'state=floating center=on honor_size_hints=true'
    # Dialogs retain their requested size; known utility main windows get a cap.
    if size and not dialog:
        tree = output(['bspc', 'query', '-T', '-m', 'focused'])
        try:
            rect = json.loads(tree)['rectangle']
            width = min(size[0], max(240, rect['width'] - 80))
            height = min(size[1], max(160, rect['height'] - 120))
            result += f' rectangle={width}x{height}+0+0'
        except (ValueError, KeyError, TypeError):
            pass
    return result

if __name__ == '__main__' and len(sys.argv) >= 4:
    print(consequences(sys.argv[1], sys.argv[2], sys.argv[3], ' '.join(sys.argv[4:])))
