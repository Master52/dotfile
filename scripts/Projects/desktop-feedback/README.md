# Desktop notifications and screenshots

Print Screen opens the centred screenshot menu: entire screen, select window,
or select area. Window capture shows instructions and waits for you to click a
visible window. Its border highlights on hover. Area selection uses a transparent
overlay so the desktop remains visible; drag in any direction. Escape or
right-click cancels. Instruction notifications close before capture.
Shift+Print selects an area directly. PNGs go to ~/Pictures/Screenshots with
unique timestamps and are copied to the clipboard when xclip is available.
The implementation uses the existing GTK/GDK X11 support, not scrot.

Volume, mute, microphone and brightness keys show short notifications with
progress bars. Dunst stack tags replace existing indicators instead of stacking.
Their settings are included in every desktop theme's Dunst template.

The battery watcher starts with desktop-services. It checks every 15 seconds,
warns once at 20%, escalates once at 10%, and resets after connecting a charger
or recovering to at least 25%. Charger changes notify with the battery percentage.
Critical battery notifications are replaced when charger state changes.
Multiple watcher instances are prevented with a session lock.

Drive menus notify after a successful mount, unmount or USB power-off. Busy
drive errors explain that files/folders should be closed before retrying.

Tests: python3 -m unittest discover -s ~/Projects/desktop-feedback -v
