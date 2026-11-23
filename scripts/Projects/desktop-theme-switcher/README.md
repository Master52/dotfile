# Desktop theme switcher

Press **Alt+Shift+T**, select a theme in dmenu, and press Enter.
Escape cancels. The last selection survives login, bspwm reloads and monitor changes.

Included: Catppuccin Mocha, Tokyo Night, Nord, Gruvbox Material, and Rosé Pine.
The GTK variants are local recolourings of your Catppuccin GTK theme, using the
named palettes; they are not the upstream GTK implementations of those themes.
Folder icons are palette variants of Papirus with Papirus-Dark application icons.
Wallpapers are locally generated SVG landscapes, except your existing Purple
Horizon wallpaper in the Catppuccin preset.

Changes cover GTK 2/3/4 settings, XFCE XSettings, terminal colours/transparency,
bspwm borders, Polybar, dmenu, Dunst, cursor, folder icons, desktop wallpaper,
and Betterlockscreen colours and cached wallpaper. Existing application shortcuts,
bar modules, compositor settings and window layout are preserved.
Alacritty reloads its colours automatically. Some other apps need reopening.
Apps that draw their own interface (including some libadwaita, browser and
Electron apps) may need their own theme setting.

## Firefox

The `default-default` Firefox profile (`djlncrei.default-default`) is integrated
through the templates in
`~/.config/desktop-themes/templates/.mozilla/firefox/djlncrei.default-default/chrome/`.
Theme switching generates its palette, browser styling and new-tab styling.
Fully quit and reopen Firefox after switching themes; Firefox loads these styles
at startup. Other Firefox profiles are unaffected.

The interface uses the desktop font, neutral toolbars, compact rounded tabs,
a quiet active-tab background and accent-colored address-bar focus. A single
visible tab hides the horizontal tab strip, while window controls appear in
the navigation bar. Pinned tabs count as tabs. The strip stays available for
tab groups, split views and toolbar customization. Vertical tabs retain their
normal behavior.

An enabled bookmarks toolbar appears when the pointer or keyboard focus enters
the toolbars. To enable it, use Firefox's Bookmarks Toolbar > Always Show.
Home and new-tab pages use the desktop palette. A small `user.js` block enables
custom CSS and disables news, sponsored shortcuts and weather on those pages.
Existing bookmarks, shortcuts and browsing data are preserved.

The pre-install files and restoration manifest are saved in
`~/.config/desktop-themes/backups/before-firefox-*`. To undo the integration,
remove the three Firefox templates, restore backed-up files according to that
manifest, remove newly created files, and restart Firefox. Back up any subsequent
personal CSS edits first. Firefox UI changes may require template adjustments.

## Commands

```sh
~/.local/bin/desktop-theme                     # dmenu picker
~/.local/bin/desktop-theme --list
~/.local/bin/desktop-theme --apply tokyo-night
~/.local/bin/desktop-theme --previous          # return to the last theme
~/.local/bin/desktop-theme --check nord        # validate without applying
~/.local/bin/desktop-theme --refresh           # restore live XSettings/borders
~/.local/bin/desktop-theme --sync-login        # explicit sudo login-screen sync
```

The login screen belongs to the system. Normal theme switching never asks for
sudo. Choose **Sync current theme to login screen (sudo)** in the menu when you
want to update it too. A terminal opens for your password. The helper installs
Slick Greeter if needed, copies assets to system-readable directories and backs
up its configuration. It does not restart LightDM or terminate your session.
Existing auto-login settings are preserved, so an enabled auto-login may bypass
the greeter. Login changes appear the next time the greeter is displayed.

## Add a theme without editing the script

Theme packs live in `~/.config/desktop-themes/themes/<id>/`.

1. Copy a pack, for example:

   ```sh
   cp -r ~/.config/desktop-themes/themes/nord ~/.config/desktop-themes/themes/my-theme
   ```

2. Edit `my-theme/theme.json`. Give it a unique `name` and change `colors`.
   Each colour is `#RRGGBB`. The required colour keys are:
   `bg`, `fg`, `accent`, `surface`, `muted`, `red`, `green`, `yellow`, `blue`,
   `cyan`, `subtext`, `overlay`, `crust`, `mantle`.
   You can also set `cursor`, `cursor_size`, `ui_font`, `mono_font`, and `opacity`.

3. Generate matching GTK assets, folder icons and the landscape wallpaper:

   ```sh
   ~/.local/bin/desktop-theme --build-assets my-theme
   ~/.local/bin/desktop-theme --check my-theme
   ```

4. Open the menu. Your theme appears automatically.

For a custom wallpaper, put `my-wallpaper.jpg` in the pack and set
`"wallpaper": "my-wallpaper.jpg"`. A relative path is relative to the pack;
absolute paths and `~/...` also work. The builder regenerates `wallpaper.png`
when that is the chosen filename, so use another name for your own image.
To use an existing GTK/icon theme, set `gtk` and `icons` to its installed names
and skip `--build-assets`. Cursor themes must also be installed first.
There are no executable hooks in theme packs.

## Templates and backups

`~/.config/desktop-themes/templates/` contains ordinary configuration files with
tokens such as `{{bg}}`, `{{accent}}`, `{{gtk}}`, and `{{mono_font}}`.
Use `{{bg_hex}}` for colours without the `#` (Betterlockscreen uses this form).
Edit templates for permanent changes; editing generated files directly is
overwritten the next time you choose a theme.

The original setup is saved under
`~/.local/share/desktop-rice/backups/before-theme-switcher-*`.
The most recent switch transaction is saved under
`~/.cache/desktop-themes/last-transaction/manifest.json`.
Theme changes validate assets and prepare the lock image first. Critical write
or wallpaper errors restore the original generated files and state. Live reload
warnings are reported separately, so a failed optional reload can be retried.
Multiple theme switchers cannot apply changes concurrently.

Tests: `python3 -m unittest discover -s ~/Projects/desktop-theme-switcher -p 'test_*.py' -v`.

Assets: Catppuccin GTK v1.0.3 (`github.com/catppuccin/gtk`), Papirus
(`github.com/PapirusDevelopmentTeam/papirus-icon-theme`), Bibata v2.0.7
(`github.com/ful1e5/Bibata_Cursor`). Original asset licences remain with their files.

## Yazi file manager

Alt+Shift+E launches Yazi in a dedicated Kitty window for native image previews.
File icons use Symbols Nerd Font Mono. Enter opens files, Shift+O chooses an
opener, Space selects, and q quits. GIFs and video files open in mpv; the preview
pane shows still previews. Configuration is in ~/.config/yazi/yazi.toml.
Yazi and its Kitty window have templates in the theme switcher; reopen the file
manager after changing themes to load their new colours.
Run the archived setup-yazi script to install the required Void packages.

### File-manager launch speed

A hidden Kitty instance in the `desktop-yazi` group is started with the desktop
by `~/.local/bin/yazi-terminal-server`. File-manager windows reuse its renderer
and font cache. The local control socket lives in the private desktop-yazi
runtime directory; it is used to reload the selected theme before opening a
window. The helper starts the server automatically if it is not running.
Measured terminal-ready time on this machine: approximately 986 ms for a fresh
Kitty process versus 48–52 ms for a reused process (before Yazi startup).

## sxiv wallpaper picker

Alt+Shift+W opens wallpaper thumbnails. Ctrl+X then w applies the image to the
current desktop theme and Betterlockscreen. The script stores a managed PNG
and a per-theme override; switching themes and restarting the session keep
that choice. `desktop-theme --set-wallpaper IMAGE` performs the same operation.
Alt+Shift+S opens the screenshot browser. See ~/Projects/sxiv-tools/README.md
for copying images, opening folders and configuring editor actions.

## Graphite

Graphite is a dark Apple-inspired preset with Inter, JetBrains Mono, a blue
accent, original dark wave wallpaper, a centered clock, and explicit
selection contrast. Choose it in Super+Shift+T or run `desktop-theme --apply
graphite`. Use `desktop-theme --previous` to return to the previous preset.

Theme packs may provide a `templates/` directory mirroring the common templates;
these override only that pack. Optional `mode` (`light` or `dark`), `window_gap`,
`border_width`, and `ui_font_size` control appearance. aerc uses the generated
`desktop` styleset; reload aerc after switching. Vim loads `desktop` on startup.

## Liquid Glass

Choose **Liquid Glass** with **Super+Shift+T**, or run
`desktop-theme --apply liquid-glass`. The pack includes original 2560×1440
abstract glass wallpaper, a frosted floating bar, cyan folder icons inheriting
Papirus-Dark, Bibata Ice cursors, Inter UI text, JetBrains Mono terminal text,
and Symbols Nerd Font Mono bar/file icons. All fonts are already installed.
Picom v13 provides rounded corners, dual-Kawase background blur, soft shadows,
280 ms opening, 200 ms closing, and 220 ms tiling transitions. Terminals use
82% opacity; file-manager, notification, and menu surfaces have selective
transparency. Fullscreen media retains its application opacity.

All overrides live in `~/.config/desktop-themes/themes/liquid-glass/templates/`;
other presets retain their own settings. `desktop-theme --previous` restores
the previous preset. Reopen applications that do not reload theme settings.
The glass effect uses blur and transparency, without optical refraction.
