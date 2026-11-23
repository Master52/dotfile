# sxiv wallpaper picker and screenshot browser

- **Alt+Shift+W** — wallpaper thumbnails, from ~/Pictures/Wallpapers and theme packs.
- **Alt+Shift+S** — screenshot thumbnails, newest first, from ~/Pictures/Screenshots.

Use Enter to switch between thumbnails and an image, arrow keys or hjkl to
navigate, m to mark images, and q to quit. To run an action, press Ctrl+X,
release it, then press the lowercase action key:

| Key after Ctrl+X | Action |
| --- | --- |
| w | Set the current image as wallpaper and rebuild Betterlockscreen |
| y | Copy the current image to the clipboard as PNG |
| p | Copy the current/marked file paths as plain text |
| o | Open its containing folder in Yazi |
| a | Open a themed dmenu with image actions |
| i | Show image dimensions, size and folder |
| e | Open the current/marked images in an installed image editor |

If multiple images are marked, clipboard, wallpaper and folder actions use
the first one. Editor actions use all marked images. sxiv's status bar shows
the most useful keys for the current browser.

Wallpapers are saved **per desktop theme**. A managed PNG copy in
~/.config/desktop-themes/wallpapers keeps it available after moving the source.
The per-theme override is in ~/.config/desktop-themes/overrides/<id>.json.
Switching away and back restores the chosen wallpaper. Root-screen startup,
monitor changes, and the optional login-screen sync use that override too.
GIF wallpaper selections use a static first frame.

To restore a theme's original wallpaper, choose its original wallpaper image
from the picker, or remove its override JSON and reapply that desktop theme.
The original theme pack is preserved; selecting a wallpaper also preserves
the previous-theme shortcut history. Desktop and lock images update in the
same transaction, with rollback if applying the wallpaper fails.

Configuration: ~/.config/sxiv-tools/config.json. Add folders under
wallpaper_directories, change screenshot_directory, or set an editor command
as an array, e.g. "editor": ["gimp"]. If no editor is configured, GIMP, Pinta,
Krita and mtPaint are detected if installed. No editor is installed automatically.
Newline characters in image filenames cannot be represented by sxiv's file-list
protocol and are omitted from the browser.

All other sxiv launches, including from Yazi, also get the Ctrl+X image actions.
No images are deleted or moved by these tools.

Commands: ~/.local/bin/wallpaper-picker [folder],
~/.local/bin/screenshot-browser [folder].

Tests: python3 -m unittest discover -s ~/Projects/sxiv-tools -v

Void provides sxiv through nsxiv. Its handlers live in ~/.config/nsxiv/exec,
linked to the shared handlers in ~/.config/sxiv/exec. Both thumbnail and image
mode show the action hints. After Ctrl+X, release both keys before pressing
the action key (for example lowercase a).

Image copying produces image/png for apps that accept pasted images. A terminal
or plain-text field may not accept image data; use Ctrl+X then p to paste the
file path there. Multiple marked paths are separated by newlines.
