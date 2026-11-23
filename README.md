# Dotfiles for Void Linux and bspwm

Install GNU Stow and Git, then clone or check out this repository at `~/dotfile`.
Preview and apply the five packages from the repository directory.

```bash
stow --no-folding --simulate --verbose --target="$HOME" shell desktop apps scripts themes
stow --no-folding --target="$HOME" shell desktop apps scripts themes
```

If Stow reports a conflict, compare the existing file and move it to a backup
before retrying. Edit the linked files in place and commit from this repository.

The desktop theme switcher generates the active Polybar, Picom, Dunst, Kitty,
GTK, and related files from the theme templates. Keep the generated files local.
On a new machine, initialize those files with
`python3 ~/Projects/desktop-theme-switcher/theme_switcher.py --apply graphite`
after installing the relevant desktop programs. The local desktop and camera
wrappers can rely on installed programs, machine-specific paths, and devices.
