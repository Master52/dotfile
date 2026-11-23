# dmenu 5.4 with the native center patch

Source: https://dl.suckless.org/tools/dmenu-5.4.tar.gz
Patch: https://tools.suckless.org/dmenu/patches/center/dmenu-center-20250407-b1e217b.diff

The upstream patch applies cleanly to dmenu 5.4. Local settings use a 640-pixel
minimum width (clamped to the monitor) and a height ratio of 2 for true vertical
centering. Centering is opt-in through `-c`.

Run `the archived install-centered-dmenu script` to install missing Void development
packages, build the source, install `~/.local/bin/dmenu`, and update the menu
launcher plus its theme template. System dmenu is preserved.

The shared launcher supplies `-c`, so the app, theme, session and reload menus
all use the native patch. Theme switches preserve this setting.
