# Desktop and application shortcut guide

Updated: 2026-11-02. Source of truth: this machine's current configuration,
installed manuals and the pinned upstream Yazi 26.9.1 defaults. Run
`~/.local/bin/update-shortcut-guide` after changing key files to refresh the generated sections.

Press **Alt+F1** to open this file in Neovim. Press **Space then /** for live fuzzy search,
type an app and action (examples: `yazi new tab`, `aerc attach`, `nchat send`, `print cancel`),
then Enter to jump to the result. Escape cancels. **Space f f** is an alternative.
The picker runs only when opened; there is no background indexing service.

For ordinary Neovim search use `/words` then Enter, `n` next and `N` previous.
`:ShortcutSearch` works from any Neovim buffer; `:Shortcuts` opens this guide.

Notation: **Win = Super**, **Ctrl = C**, **Alt = A/M**, **Shift = S**. `Space m t`
means press the keys in sequence; `Ctrl+X then Shift+P` means release Ctrl+X before
pressing Shift+P. Uppercase letters are case-sensitive. Neovim's leader is Space.
Tables say whether a key is custom, a default, or a configured value whose origin
has not been established. Context matters: aerc inbox and viewer keys differ,
and Neovim Normal/Insert/Visual/Terminal modes have different meanings.

Desktop shortcuts take priority over application shortcuts. This guide documents
existing behavior; it does not add all the defaults as new bindings.

## Contents and quick tasks

Search the section names with `/`, or use the fuzzy picker. Local file links open with
Enter, gf or gx. Heading links are not used because the current Markdown link helper
does not navigate heading anchors.

- Desktop / bspwm / launchers / notifications / monitors
- Printing / queue / cancel / Android / paper tray
- Yazi: every shipped keymap context plus local overrides
- nchat: effective keys and installed manual differences
- aerc: workflow and every configured context
- tremc and Transmission: every defined action, plus daemon commands
- Neovim: modes, navigation, editing, windows, search, completion, C builds
- Markdown notes and installed plugins: Markview, image.nvim, Minuet
- sxiv/nsxiv, Zathura, Firefox, Kitty, tmux, mpv, passwords and desktop menus
- Conflicts, source files, and how to update this guide

| Key or command | What it does | Origin |
| --- | --- | --- |
| Alt+F1 | Open this Markdown shortcut guide in Neovim | Custom |
| Space / (in this guide) | Fuzzy find any shortcut by app, action or key | Custom |
| Win+Y | Open normal Yazi file manager | Custom |
| Ctrl+Shift+P | Open Yazi print picker; Space selects files, Enter opens dialog | Custom |
| Win+M | Open aerc email | Custom |
| Win+W | Open nchat messaging | Custom |
| Win+T | Open tremc torrent client | Custom |
| Win+Shift+T | Torrent menu: add magnet/file, pause/resume all, Downloads | Custom |
| Win+F | Open Firefox with temporary private profile | Custom |
| Win+Shift+F | Choose Firefox profile | Custom |
| Win+Shift+B | Bookmarks menu | Custom |
| Win+Shift+P | Password menu (different from Ctrl+Shift+P printing) | Custom |

## Desktop — every configured sxhkd binding

Source: [sxhkdrc](/home/master/.config/sxhkd/sxhkdrc). Braces pair keys and directions in order. Alt+h/j/k/l means left/down/up/right.

| Shortcut | Action | Origin / status |
| --- | --- | --- |
| ctrl + shift + p | Open Yazi print picker and print dialog | Custom |
| alt + Tab | Focus previous desktop | Custom |
| alt + Return | Open terminal | Custom |
| super + space | Search and launch applications | Custom |
| super + f | Temporary private Firefox | Custom |
| super + shift + f | Choose Firefox profile | Custom |
| super + y | Open Yazi | Custom |
| alt + {h,j,k,l} | Focus left/down/up/right window | Custom |
| alt + ctrl + shift + {h,j,k,l} | Swap with left/down/up/right window | Custom |
| alt + shift + {h,j,k,l} | Resize window left/down/up/right | Custom |
| alt + {1-9} | Focus desktop 1–9 | Custom |
| alt + shift + {1-9} | Move window to desktop 1–9 and follow | Custom |
| alt + q | Close focused window | Custom |
| alt + f | Toggle fullscreen | Custom |
| alt + shift + space | Toggle floating | Custom |
| alt + space | Focus next local window | Custom |
| alt + m | Toggle tiled/monocle layout | Custom |
| alt + b | Balance window sizes | Custom |
| alt + shift + r | Reload menu: bspwm, shortcuts, bar, compositor, notifications | Custom |
| super + shift + q | Power menu: lock/shutdown/reboot/suspend/hibernate | Custom |
| alt + F1 | Open this guide in Neovim | Custom |
| Print | Screenshot menu; save and copy | Custom |
| alt + ctrl + p | Screenshot menu; save and copy | Custom; DUPLICATE binding |
| shift + Print | Select screenshot area directly | Custom |
| XF86AudioRaiseVolume | Volume +5% | Custom |
| XF86AudioLowerVolume | Volume -5% | Custom |
| XF86AudioMute | Toggle speaker mute | Custom |
| XF86AudioMicMute | Toggle microphone mute | Custom |
| XF86MonBrightnessUp | Increase brightness | Custom |
| XF86MonBrightnessDown | Decrease brightness | Custom |
| alt + n | Dismiss notification | Custom |
| alt + shift + n | Show notification history | Custom |
| alt + ctrl + n | Toggle do-not-disturb | Custom |
| alt + bracketleft | Focus previous monitor | Custom |
| alt + bracketright | Focus next monitor | Custom |
| alt + shift + bracketleft | Move window to previous monitor and follow | Custom |
| alt + shift + bracketright | Move window to next monitor and follow | Custom |
| alt + ctrl + p | Reapply automatic monitor layout | Custom; DUPLICATE binding |
| super + r | Open RustDesk remote desktop | Custom |
| super +  m | Open aerc email (background inbox checking continues) | Custom |
| super + ctrl + t | Choose complete desktop theme | Custom |
| super + shift + c | Choose clipboard history entry | Custom |
| super + shift + e | Choose emoji; paste with Ctrl+V | Custom |
| super + shift + d | Mount/open/unmount/eject drives | Custom |
| super + shift + w | Browse wallpapers in sxiv | Custom |
| super + shift + s | Browse screenshots in sxiv | Custom |
| super + shift + p | Choose encrypted account and copy password | Custom |
| super + shift + b | Open/add Firefox bookmarks | Custom |
| super + w | Open nchat/WhatsApp | Custom |
| super + shift + x | Choose tmux session or launch in a folder | Custom |
| super + shift + o | Select screen region and copy recognized text | Custom |
| super + s | Open Steam on desktop 7 with NVIDIA PRIME | Custom |
| super + h | Choose camera stream | Custom |
| super + t | Open tremc; downloads continue in background | Custom |
| super + shift + t | Add magnet/torrent; Downloads; pause/resume all | Custom |
| super + shift + l | Choose Amazon PDFs in Yazi; generate label sheet | Custom |

## Printing — files, queue, recovery and Android

Default printer: `Canon_LBP2900_Windows`. USB is attached to Windows; Linux forwards
Canon CAPT output through its Windows share. Windows, Linux and printer must stay on
for phone → Linux → Windows printing. Network loss can interrupt a job; CUPS uses
`retry-job` instead of stopping the entire queue. A completed Linux job confirms
handoff, not physical paper output.

| Key or command | What it does | Origin |
| --- | --- | --- |
| Ctrl+Shift+P (desktop) | Open print picker in Yazi; Space selects, Enter opens GtkLP, click Print to send | Custom |
| Ctrl+P (normal Yazi) | Open GtkLP for selected files or the hovered file | Custom |
| Ctrl+P (Zathura, after reopening) | Open GtkLP for current PDF; :print still uses limited built-in GTK 4 dialog | Custom |
| Ctrl+X then Shift+P (sxiv) | Open GtkLP for current image, or marked images in thumbnail mode | Custom |
| Space / then print cancel (this guide) | Fuzzy find queue and cancellation commands | Custom |
| q (Yazi print picker) | Cancel picker without opening print dialog | Custom |
| Cancel (GtkLP dialog) | Close dialog without sending the selected files | Custom |

| Key or command | What it does | Origin |
| --- | --- | --- |
| gtklpq | Open graphical CUPS queue manager; select job and cancel it | CUPS command |
| http://localhost:631/jobs/ | View/cancel jobs in browser on Linux | CUPS command |
| lpstat -o | List pending jobs and their IDs | CUPS command |
| lpstat -t | Show service, printer, default and pending jobs | CUPS command |
| lpstat -W all -l -o Canon_LBP2900_Windows | Show job details including held and completed jobs | CUPS command |
| cancel Canon_LBP2900_Windows-ID | Cancel one job; replace ID with actual number from lpstat | CUPS command |
| cancel -a Canon_LBP2900_Windows | Cancel all queued jobs for this printer | CUPS command |
| lp -i Canon_LBP2900_Windows-ID -H resume | Resume a held job; check whether it already physically printed first | CUPS command |
| lp -d Canon_LBP2900_Windows /path/file.pdf | Print immediately, without dialog | CUPS command |
| lp -n 2 /path/file.pdf | Print two copies immediately | CUPS command |
| lp -P 1-3 /path/file.pdf | Print document pages 1 through 3 | CUPS command |
| lpoptions -d Canon_LBP2900_Windows | Set per-user default printer | CUPS command |
| sudo cupsenable Canon_LBP2900_Windows | Resume disabled printer if needed; requires administrator rights | CUPS command |

### Android address and paper feed

Android CUPS printer URI: `http://master.local:631/printers/Canon_LBP2900_Windows`.
Enable CUPS Printing in Android Settings → Printing; choose the printer in a PDF's
Print menu. `master.local` follows Linux IP changes when the phone/app supports mDNS.
Avahi starts automatically and uses only a few MB of RAM. Windows is still addressed
as `192.168.29.197`; if that IP changes, the Linux queue must be updated or the Windows
IP reserved in the router. Changing Windows' account password also requires updating
the saved printer credentials. Credentials are not stored in this guide.

LBP2900 upper manual slot accepts one sheet and takes priority; lower multipurpose
tray is used when the upper slot is empty. Installed driver offers only Auto source.
To print from the lower tray, remove paper from the upper slot.

## Yazi — workflow, overrides and every shipped default

Source: local keymap merged over upstream **v26.9.1**. Default keys overridden locally
are replaced below, not presented as simultaneously active. `a` creates a file;
end its name with `/` to create a directory. **New tab is `t t`**, not just `t`, in
this installed version. `Space` toggles selection and advances; operations use
selected files, otherwise the hovered file. Uppercase `D` permanently deletes.
In chooser mode (`print-files`, aerc attachments, Amazon labels), Enter returns the
chosen paths instead of opening them in a viewer. Normal Yazi opens PDFs in Zathura,
images in sxiv, text in Neovim, media in mpv, and Office files in LibreOffice.

The default `z` fuzzy file finder requires fzf; `Z` directory jump requires zoxide
and its directory history. Missing optional executables can make a shipped binding
unavailable. Yazi's own F1/~ help shows the live effective keys.

### Yazi — mgr

| Key sequence | Action | Origin |
| --- | --- | --- |
| <C-p> | Print selected files | Custom |
| g then d | Go to download | Custom |
| g then c | Go to .config | Custom |
| g then s | Go to Screenshot | Custom |
| g then D | Go to Documents | Custom |
| g then h | Go home | Custom |
| g then n | Go to new volume | Custom |
| g then p | Go to  Pictures | Custom |
| g then r | Go to removable media (directory must exist) | Custom |
| <Esc> | Exit visual mode, clear selection, or cancel search | Default |
| <C-[> | Exit visual mode, clear selection, or cancel search | Default |
| q | Quit the process | Default |
| Q | Quit without outputting cwd-file | Default |
| <C-c> | Close the current tab, or quit if it's last | Default |
| <C-z> | Suspend the process | Default |
| k | Previous file | Default |
| j | Next file | Default |
| <Up> | Previous file | Default |
| <Down> | Next file | Default |
| g then g | Go to top | Default |
| G | Go to bottom | Default |
| <Home> | Go to top | Default |
| <End> | Go to bottom | Default |
| <C-u> | Move cursor up half page | Default |
| <C-d> | Move cursor down half page | Default |
| <C-b> | Move cursor up one page | Default |
| <C-f> | Move cursor down one page | Default |
| <S-PageUp> | Move cursor up half page | Default |
| <S-PageDown> | Move cursor down half page | Default |
| <PageUp> | Move cursor up one page | Default |
| <PageDown> | Move cursor down one page | Default |
| h | Back to the parent directory | Default |
| l | Enter the child directory | Default |
| <Left> | Back to the parent directory | Default |
| <Right> | Enter the child directory | Default |
| H | Back to previous directory | Default |
| L | Forward to next directory | Default |
| <Space> | Toggle the current selection state | Default |
| <C-a> | Select all files | Default |
| <C-r> | Invert selection of all files | Default |
| v | Enter visual mode (selection mode) | Default |
| V | Enter visual mode (unset mode) | Default |
| K | Seek up 5 units in the preview | Default |
| J | Seek down 5 units in the preview | Default |
| <Tab> | Spot hovered file | Default |
| o | Open selected files | Default |
| O | Open selected files interactively | Default |
| <Enter> | Open selected files | Default |
| <S-Enter> | Open selected files interactively | Default |
| y | Yank selected files (copy) | Default |
| x | Yank selected files (cut) | Default |
| p | Paste yanked files | Default |
| P | Paste yanked files (overwrite if the destination exists) | Default |
| - | Symlink the absolute path of yanked files | Default |
| _ | Symlink the relative path of yanked files | Default |
| <C--> | Hardlink yanked files | Default |
| Y | Cancel the yank status | Default |
| X | Cancel the yank status | Default |
| d | Trash selected files | Default |
| D | Permanently delete selected files | Default |
| a | Create a file (ends with / for directories) | Default |
| A | Bulk create files | Default |
| r | Rename selected file(s) | Default |
| ; | Run a shell command | Default |
| : | Run a shell command (block until finishes) | Default |
| . | Toggle the visibility of hidden files | Default |
| s | Search files by name via fd | Default |
| S | Search files by content via ripgrep | Default |
| <C-s> | Cancel the ongoing search | Default |
| z | Jump to a file/directory via fzf | Default |
| Z | Jump to a directory via zoxide | Default |
| m then s | Linemode: size | Default |
| m then p | Linemode: permissions | Default |
| m then b | Linemode: btime | Default |
| m then m | Linemode: mtime | Default |
| m then o | Linemode: owner | Default |
| m then n | Linemode: none | Default |
| c then c | Copy file path | Default |
| c then C | Copy file URL | Default |
| c then d | Copy directory path | Default |
| c then D | Copy directory URL | Default |
| c then f | Copy filename | Default |
| c then n | Copy filename without extension | Default |
| f | Filter files | Default |
| / | Find next file | Default |
| ? | Find previous file | Default |
| n | Next found | Default |
| N | Previous found | Default |
| , then m | Sort by modified time | Default |
| , then M | Sort by modified time (reverse) | Default |
| , then b | Sort by birth time | Default |
| , then B | Sort by birth time (reverse) | Default |
| , then e | Sort by extension | Default |
| , then E | Sort by extension (reverse) | Default |
| , then a | Sort alphabetically | Default |
| , then A | Sort alphabetically (reverse) | Default |
| , then n | Sort naturally | Default |
| , then N | Sort naturally (reverse) | Default |
| , then s | Sort by size | Default |
| , then S | Sort by size (reverse) | Default |
| , then r | Sort randomly | Default |
| g then t | Go to trash bin | Default |
| g then <Space> | Jump interactively | Default |
| g then f | Follow hovered symlink | Default |
| t then t | Create a new tab in CWD | Default |
| t then r | Rename current tab | Default |
| 1 | Switch to first tab | Default |
| 2 | Switch to second tab | Default |
| 3 | Switch to third tab | Default |
| 4 | Switch to fourth tab | Default |
| 5 | Switch to fifth tab | Default |
| 6 | Switch to sixth tab | Default |
| 7 | Switch to seventh tab | Default |
| 8 | Switch to eighth tab | Default |
| 9 | Switch to ninth tab | Default |
| [ | Switch to previous tab | Default |
| ] | Switch to next tab | Default |
| { | Swap current tab with previous tab | Default |
| } | Swap current tab with next tab | Default |
| w | Show task manager | Default |
| ~ | Open help | Default |
| <F1> | Open help | Default |

### Yazi — tasks

| Key sequence | Action | Origin |
| --- | --- | --- |
| <Esc> | Close task manager | Default |
| <C-[> | Close task manager | Default |
| <C-c> | Close task manager | Default |
| w | Close task manager | Default |
| k | Previous task | Default |
| j | Next task | Default |
| <Up> | Previous task | Default |
| <Down> | Next task | Default |
| <Enter> | Inspect the task | Default |
| x | Cancel the task | Default |
| ~ | Open help | Default |
| <F1> | Open help | Default |

### Yazi — spot

| Key sequence | Action | Origin |
| --- | --- | --- |
| <Esc> | Close the spot | Default |
| <C-[> | Close the spot | Default |
| <C-c> | Close the spot | Default |
| <Tab> | Close the spot | Default |
| k | Previous line | Default |
| j | Next line | Default |
| h | Swipe to previous file | Default |
| l | Swipe to next file | Default |
| <Up> | Previous line | Default |
| <Down> | Next line | Default |
| <Left> | Swipe to previous file | Default |
| <Right> | Swipe to next file | Default |
| c then c | Copy selected cell | Default |
| ~ | Open help | Default |
| <F1> | Open help | Default |

### Yazi — pick

| Key sequence | Action | Origin |
| --- | --- | --- |
| <Esc> | Cancel pick | Default |
| <C-[> | Cancel pick | Default |
| <C-c> | Cancel pick | Default |
| <Enter> | Submit the pick | Default |
| k | Previous option | Default |
| j | Next option | Default |
| <Up> | Previous option | Default |
| <Down> | Next option | Default |
| ~ | Open help | Default |
| <F1> | Open help | Default |

### Yazi — input

| Key sequence | Action | Origin |
| --- | --- | --- |
| <C-c> | Cancel input | Default |
| <Enter> | Submit input | Default |
| <Esc> | Back to normal mode, or cancel input | Default |
| <C-[> | Back to normal mode, or cancel input | Default |
| i | Enter insert mode | Default |
| I | Move to the BOL, and enter insert mode | Default |
| a | Enter append mode | Default |
| A | Move to the EOL, and enter append mode | Default |
| v | Enter visual mode | Default |
| r | Replace a single character | Default |
| V | Select from BOL to EOL | Default |
| <C-A> | Select from EOL to BOL | Default |
| <C-E> | Select from BOL to EOL | Default |
| h | Move back a character | Default |
| l | Move forward a character | Default |
| <Left> | Move back a character | Default |
| <Right> | Move forward a character | Default |
| <C-b> | Move back a character | Default |
| <C-f> | Move forward a character | Default |
| b | Move back to the start of the current or previous word | Default |
| B | Move back to the start of the current or previous WORD | Default |
| w | Move forward to the start of the next word | Default |
| W | Move forward to the start of the next WORD | Default |
| e | Move forward to the end of the current or next word | Default |
| E | Move forward to the end of the current or next WORD | Default |
| <A-b> | Move back to the start of the current or previous word | Default |
| <A-f> | Move forward to the end of the current or next word | Default |
| <C-Left> | Move back to the start of the current or previous word | Default |
| <C-Right> | Move forward to the end of the current or next word | Default |
| 0 | Move to the BOL | Default |
| $ | Move to the EOL | Default |
| _ | Move to the first non-whitespace character | Default |
| ^ | Move to the first non-whitespace character | Default |
| <C-a> | Move to the BOL | Default |
| <C-e> | Move to the EOL | Default |
| <Home> | Move to the BOL | Default |
| <End> | Move to the EOL | Default |
| <Backspace> | Delete the character before the cursor | Default |
| <Delete> | Delete the character under the cursor | Default |
| <C-h> | Delete the character before the cursor | Default |
| <C-d> | Delete the character under the cursor | Default |
| <C-u> | Kill backwards to the BOL | Default |
| <C-k> | Kill forwards to the EOL | Default |
| <C-w> | Kill backwards to the start of the current word | Default |
| <A-d> | Kill forwards to the end of the current word | Default |
| <C-Backspace> | Kill backwards to the start of the current word | Default |
| <C-Delete> | Kill forwards to the end of the current word | Default |
| d | Cut selected characters | Default |
| D | Cut until EOL | Default |
| c | Cut selected characters, and enter insert mode | Default |
| C | Cut until EOL, and enter insert mode | Default |
| s | Cut current character, and enter insert mode | Default |
| S | Cut from BOL until EOL, and enter insert mode | Default |
| x | Cut current character | Default |
| y | Copy selected characters | Default |
| p | Paste copied characters after the cursor | Default |
| P | Paste copied characters before the cursor | Default |
| u | Undo, or lowercase if in visual mode | Default |
| U | Uppercase | Default |
| <C-r> | Redo the last operation | Default |
| k | Recall previous input | Default |
| j | Recall next input | Default |
| <Up> | Recall previous input | Default |
| <Down> | Recall next input | Default |
| <C-p> | Recall previous input | Default |
| <C-n> | Recall next input | Default |
| ~ | Open help | Default |
| <F1> | Open help | Default |

### Yazi — confirm

| Key sequence | Action | Origin |
| --- | --- | --- |
| <Esc> | Cancel the confirm | Default |
| <C-[> | Cancel the confirm | Default |
| <C-c> | Cancel the confirm | Default |
| <Enter> | Submit the confirm | Default |
| n | Cancel the confirm | Default |
| y | Submit the confirm | Default |
| k | Previous line | Default |
| j | Next line | Default |
| <Up> | Previous line | Default |
| <Down> | Next line | Default |
| ~ | Open help | Default |
| <F1> | Open help | Default |

### Yazi — cmp

| Key sequence | Action | Origin |
| --- | --- | --- |
| <C-c> | Cancel completion | Default |
| <Tab> | Submit the completion | Default |
| <Enter> | Complete and submit the input | Default |
| <A-k> | Previous item | Default |
| <A-j> | Next item | Default |
| <Up> | Previous item | Default |
| <Down> | Next item | Default |
| <C-p> | Previous item | Default |
| <C-n> | Next item | Default |
| ~ | Open help | Default |
| <F1> | Open help | Default |

### Yazi — help

| Key sequence | Action | Origin |
| --- | --- | --- |
| <Esc> | Enter normal mode, or hide help menu | Default |
| <C-[> | Enter normal mode, or hide help menu | Default |
| <C-c> | Close help menu | Default |
| <Enter> | Close help menu and run selected action(s) | Default |
| k | Previous line | Default |
| j | Next line | Default |
| <Up> | Previous line | Default |
| <Down> | Next line | Default |
| <C-p> | Previous line | Default |
| <C-n> | Next line | Default |

## nchat — chats, messages, attachments and input

Launch with Win+W. Source: effective `~/.config/nchat/key.conf` and installed nchat
5.19.18 manual. The file includes defaults as well as changes; rows explicitly say
when a value differs from the installed manual. No Vim keymap is configured here.
Arrow Up selects a message; Down returns toward the composer. Enter inserts a newline;
Ctrl+X sends. Message actions require the message to be selected.

Ctrl+V is configured as Open; its helper uses inline Kitty image viewing where
possible, mpv for audio/video and the default application for other files.
Ctrl+W explicitly opens links with the configured Firefox private-window command.
The guide does not assume Ctrl+V pastes text: clipboard paste is Alt+V.
Ctrl+G toggles help and Ctrl+O shows additional commands.

Desktop Alt+N / Alt+P combinations may intercept app shortcuts; Alt+N is globally
assigned to dismiss notifications, so nchat's contact-search Alt+N can be intercepted.

| Key | Action | Origin |
| --- | --- | --- |
| Alt+a | Archive current chat | Configured; matches manual/default where listed |
| Alt+i | Automatically compose a reply (requires configured backend) | Configured; matches manual/default where listed |
| Backspace | Delete previous character | Configured; matches manual/default where listed |
| Alt+Backspace | Alternate backspace key | Configured; matches manual/default where listed |
| Alt+Backspace | Delete previous word | Configured; matches manual/default where listed |
| Alt+Left (terminal keycode) | Move backward one word | Configured; matches manual/default where listed |
| Ctrl+A | Start of input line | Configured; matches manual/default where listed |
| Ctrl+C | Cancel dialog/action | Configured; matches manual/default where listed |
| Ctrl+C | Clear input | Configured; matches manual/default where listed |
| Alt+c | Copy selected message or input text | Configured; matches manual/default where listed |
| Alt+x | Cut input text to clipboard | Configured; matches manual/default where listed |
| Alt+, | Narrow chat list | Configured; matches manual/default where listed |
| Delete | Delete next character | Configured; matches manual/default where listed |
| Alt+d | Delete/leave current chat | Configured; matches manual/default where listed |
| Ctrl+K | Delete input after cursor | Configured; matches manual/default where listed |
| Ctrl+U | Delete input before cursor | Configured; matches manual/default where listed |
| Ctrl+D | Delete selected message | Configured; matches manual/default where listed |
| Down | Select next message / move down | Configured; matches manual/default where listed |
| Ctrl+Z | Edit selected message | Configured; matches manual/default where listed |
| End | End | Configured; matches manual/default where listed |
| Ctrl+E | End of input line | Configured; matches manual/default where listed |
| Alt+t | External telephone call | Configured; matches manual/default where listed |
| Alt+e | Compose in external editor | Configured; matches manual/default where listed |
| Alt+/ | Find text in chat | Configured; matches manual/default where listed |
| Alt+? | Next chat search match | Configured; matches manual/default where listed |
| Alt+r | Forward selected message | Configured; matches manual/default where listed |
| Alt+Right (terminal keycode) | Move forward one word | Configured; matches manual/default where listed |
| Ctrl+N | Choose/jump to chat | Configured; matches manual/default where listed |
| Home | Home | Configured; matches manual/default where listed |
| Alt+. | Widen chat list | Configured; matches manual/default where listed |
| Ctrl+P | Jump to pinned message | Configured; differs from manual: Ctrl+P top bar / Alt+@ mention |
| Alt+q | Jump to quoted/replied message | Configured; matches manual/default where listed |
| Alt+Delete (terminal keycode) | Delete next word | Configured; matches manual/default where listed |
| Left | Move left | Configured; matches manual/default where listed |
| Enter | Insert newline in composer | Configured; matches manual/default where listed |
| Tab | Next chat | Configured; matches manual/default where listed |
| PageDown | Next history page | Configured; matches manual/default where listed |
| Enter | Confirm choice/dialog | Configured; matches manual/default where listed |
| Ctrl+V | Open selected attachment/message content | Configured; matches manual/default where listed |
| Ctrl+W | Open selected message link | Configured; matches manual/default where listed |
| Alt+w | Open message in external viewer | Configured; matches manual/default where listed |
| Ctrl+O | Show additional commands | Configured; matches manual/default where listed |
| Alt+v | Paste clipboard text | Configured; matches manual/default where listed |
| Alt+p | Pin/unpin current chat | Configured; matches manual/default where listed |
| Shift+Tab | Previous chat | Configured; matches manual/default where listed |
| PageUp | Previous history page | Configured; matches manual/default where listed |
| Ctrl+Q | Quit nchat UI | Configured; matches manual/default where listed |
| Alt+s | Add/remove selected message reaction | Configured; matches manual/default where listed |
| Right | Move right | Configured; matches manual/default where listed |
| Ctrl+R | Download/save selected attachment | Configured; matches manual/default where listed |
| Alt+n | Search/select contact | Configured; matches manual/default where listed |
| Ctrl+S | Insert emoji | Configured; matches manual/default where listed |
| Alt+2 | Insert mention (configured Alt+2) | Configured; differs from manual: Ctrl+P top bar / Alt+@ mention |
| Ctrl+X | Send message or reply to selected message | Configured; matches manual/default where listed |
| Alt+$ | External spell check | Configured; matches manual/default where listed |
| Alt+Tab | Literal Alt+Tab event | Configured; matches manual/default where listed |
| Ctrl+Y | Toggle displayed emojis | Configured; matches manual/default where listed |
| Ctrl+G | Toggle help bar | Configured; matches manual/default where listed |
| Ctrl+L | Toggle chat/contact list | Configured; matches manual/default where listed |
| Unbound | Toggle top bar (disabled) | Configured; differs from manual: Ctrl+P top bar / Alt+@ mention |
| Ctrl+T | Choose/send file attachment | Configured; matches manual/default where listed |
| Ctrl+F | Jump to unread chat | Configured; matches manual/default where listed |
| Up | Select previous message / move up | Configured; matches manual/default where listed |

## aerc — practical mail workflow

Win+M opens email. Use j/k to select mail, Enter to view, q to close viewer.
In the inbox, J/K selects folders; in the viewer J/K changes messages.
`m` composes. The embedded editor is Neovim: `:wq` saves/exits the body and opens
review; review `y` sends, `p` postpones, `a` opens the Yazi attachment picker.
In that picker select with Space and confirm with Enter. Review `n` discards
immediately, so do not use it as a navigation key. `d`/`D` in this configuration
moves mail to Gmail Trash, unlike upstream defaults that can delete it.

`Ctrl+J` / `Ctrl+K` moves MIME parts in the viewer; `o` opens the selected attachment,
`S` starts saving it. `Ctrl+L` opens a link chooser. `rr` replies to all; `Rr` replies
to sender. Gmail folder shortcuts assume English folder names.

The complete table below shows commands as well as keys; `:cf` means change folder,
`:next/:prev` navigate, `:mark` selects, and `:move` moves messages. `<Enter>` executes;
`<space>` at the end leaves a prompt for your argument. Global keys are inherited
except in contexts marked `$noinherit`. `$ex` is the command prompt key in that context,
usually Ctrl+X in compose/editor/terminal. These are live configured bindings, compared
against `/usr/share/aerc/binds.conf` to distinguish unchanged defaults.

### aerc — global

| Key or directive | Action / exact command | Origin |
| --- | --- | --- |
| <C-p> | :prev-tab<Enter> | Default (same as shipped) |
| <C-PgUp> | :prev-tab<Enter> | Default (same as shipped) |
| <C-n> | :next-tab<Enter> | Default (same as shipped) |
| <C-PgDn> | :next-tab<Enter> | Default (same as shipped) |
| \[t | :prev-tab<Enter> | Default (same as shipped) |
| \]t | :next-tab<Enter> | Default (same as shipped) |
| <C-t> | :term<Enter> | Default (same as shipped) |
| ? | :help keys<Enter> | Default (same as shipped) |
| <C-c> | :prompt 'Quit?' quit<Enter> | Default (same as shipped) |
| <C-q> | :prompt 'Quit?' quit<Enter> | Default (same as shipped) |
| <C-z> | :suspend<Enter> | Default (same as shipped) |

### aerc — messages

| Key or directive | Action / exact command | Origin |
| --- | --- | --- |
| gi | :cf INBOX<Enter> | Custom / local override |
| gs | :cf '[Gmail]/Sent Mail'<Enter> | Custom / local override |
| gd | :cf '[Gmail]/Drafts'<Enter> | Custom / local override |
| ga | :cf '[Gmail]/All Mail'<Enter> | Custom / local override |
| gt | :cf '[Gmail]/Trash'<Enter> | Custom / local override |
| gf | :cf '[Gmail]/Starred'<Enter> | Custom / local override |
| f | :forward<Enter> | Custom / local override |
| q | :prompt 'Quit?' quit<Enter> | Default (same as shipped) |
| . | :repeat | Default (same as shipped) |
| j | :next<Enter> | Default (same as shipped) |
| <Down> | :next<Enter> | Default (same as shipped) |
| <C-d> | :next 50%<Enter> | Default (same as shipped) |
| <C-f> | :next 100%<Enter> | Default (same as shipped) |
| <PgDn> | :next 100%<Enter> | Default (same as shipped) |
| k | :prev<Enter> | Default (same as shipped) |
| <Up> | :prev<Enter> | Default (same as shipped) |
| <C-u> | :prev 50%<Enter> | Default (same as shipped) |
| <C-b> | :prev 100%<Enter> | Default (same as shipped) |
| <PgUp> | :prev 100%<Enter> | Default (same as shipped) |
| gg | :select 0<Enter> | Custom / local override |
| G | :select -1<Enter> | Default (same as shipped) |
| J | :next-folder<Enter> | Default (same as shipped) |
| <C-Down> | :next-folder<Enter> | Default (same as shipped) |
| K | :prev-folder<Enter> | Default (same as shipped) |
| <C-Up> | :prev-folder<Enter> | Default (same as shipped) |
| H | :collapse-folder<Enter> | Default (same as shipped) |
| <C-Left> | :collapse-folder<Enter> | Default (same as shipped) |
| L | :expand-folder<Enter> | Default (same as shipped) |
| <C-Right> | :expand-folder<Enter> | Default (same as shipped) |
| tf | :toggle-folder<Enter> | Default (same as shipped) |
| v | :mark -t<Enter> | Default (same as shipped) |
| <Space> | :mark -t<Enter>:next<Enter> | Default (same as shipped) |
| V | :mark -v<Enter> | Default (same as shipped) |
| T | :toggle-threads<Enter> | Default (same as shipped) |
| zc | :fold<Enter> | Default (same as shipped) |
| zo | :unfold<Enter> | Default (same as shipped) |
| za | :fold -t<Enter> | Default (same as shipped) |
| zM | :fold -a<Enter> | Default (same as shipped) |
| zR | :unfold -a<Enter> | Default (same as shipped) |
| <tab> | :fold -t<Enter> | Default (same as shipped) |
| zz | :align center<Enter> | Default (same as shipped) |
| zt | :align top<Enter> | Default (same as shipped) |
| zb | :align bottom<Enter> | Default (same as shipped) |
| <Enter> | :view<Enter> | Default (same as shipped) |
| d | :move '[Gmail]/Trash'<Enter> | Custom / local override |
| D | :move '[Gmail]/Trash'<Enter> | Custom / local override |
| a | :archive flat<Enter> | Default (same as shipped) |
| A | :unmark -a<Enter>:mark -T<Enter>:archive flat<Enter> | Default (same as shipped) |
| C | :compose<Enter> | Default (same as shipped) |
| m | :compose<Enter> | Default (same as shipped) |
| b | :bounce<space> | Default (same as shipped) |
| rr | :reply -a<Enter> | Default (same as shipped) |
| rq | :reply -aq<Enter> | Default (same as shipped) |
| Rr | :reply<Enter> | Default (same as shipped) |
| Rq | :reply -q<Enter> | Default (same as shipped) |
| c | :cf<space> | Default (same as shipped) |
| $ | :term<space> | Default (same as shipped) |
| ! | :term<space> | Default (same as shipped) |
| &#124; | :pipe<space> | Default (same as shipped) |
| / | :search<space> | Default (same as shipped) |
| \ | :filter<space> | Default (same as shipped) |
| n | :next-result<Enter> | Default (same as shipped) |
| N | :prev-result<Enter> | Default (same as shipped) |
| <Esc> | :clear<Enter> | Default (same as shipped) |
| s | :split<Enter> | Default (same as shipped) |
| S | :vsplit<Enter> | Default (same as shipped) |
| pl | :patch list<Enter> | Default (same as shipped) |
| pa | :patch apply <Tab> | Default (same as shipped) |
| pd | :patch drop <Tab> | Default (same as shipped) |
| pb | :patch rebase<Enter> | Default (same as shipped) |
| pt | :patch term<Enter> | Default (same as shipped) |
| ps | :patch switch <Tab> | Default (same as shipped) |

### aerc — messages:folder=^(\[Gmail\]/)?Drafts$

| Key or directive | Action / exact command | Origin |
| --- | --- | --- |
| <Enter> | :recall<Enter> | Custom / local override |

### aerc — view

| Key or directive | Action / exact command | Origin |
| --- | --- | --- |
| d | :move '[Gmail]/Trash'<Enter> | Custom / local override |
| a | :archive flat<Enter> | Custom / local override |
| / | :toggle-key-passthrough<Enter>/ | Default (same as shipped) |
| q | :close<Enter> | Default (same as shipped) |
| O | :open<Enter> | Default (same as shipped) |
| o | :open<Enter> | Default (same as shipped) |
| S | :save<space> | Default (same as shipped) |
| &#124; | :pipe<space> | Default (same as shipped) |
| D | :move '[Gmail]/Trash'<Enter> | Custom / local override |
| A | :archive flat<Enter> | Default (same as shipped) |
| <C-y> | :copy-link <space> | Default (same as shipped) |
| <C-l> | :open-link <space> | Default (same as shipped) |
| f | :forward<Enter> | Default (same as shipped) |
| rr | :reply -a<Enter> | Default (same as shipped) |
| rq | :reply -aq<Enter> | Default (same as shipped) |
| Rr | :reply<Enter> | Default (same as shipped) |
| Rq | :reply -q<Enter> | Default (same as shipped) |
| H | :toggle-headers<Enter> | Default (same as shipped) |
| <C-k> | :prev-part<Enter> | Default (same as shipped) |
| <C-Up> | :prev-part<Enter> | Default (same as shipped) |
| <C-j> | :next-part<Enter> | Default (same as shipped) |
| <C-Down> | :next-part<Enter> | Default (same as shipped) |
| J | :next<Enter> | Default (same as shipped) |
| <C-Right> | :next<Enter> | Default (same as shipped) |
| K | :prev<Enter> | Default (same as shipped) |
| <C-Left> | :prev<Enter> | Default (same as shipped) |

### aerc — view::passthrough

| Key or directive | Action / exact command | Origin |
| --- | --- | --- |
| $noinherit | true | Default (same as shipped) |
| $ex | <C-x> | Default (same as shipped) |
| <Esc> | :toggle-key-passthrough<Enter> | Default (same as shipped) |

### aerc — compose

| Key or directive | Action / exact command | Origin |
| --- | --- | --- |
| $noinherit | true | Default (same as shipped) |
| $ex | <C-x> | Default (same as shipped) |
| $complete | <C-o> | Default (same as shipped) |
| <C-k> | :prev-field<Enter> | Default (same as shipped) |
| <C-Up> | :prev-field<Enter> | Default (same as shipped) |
| <C-j> | :next-field<Enter> | Default (same as shipped) |
| <C-Down> | :next-field<Enter> | Default (same as shipped) |
| <A-p> | :switch-account -p<Enter> | Default (same as shipped) |
| <A-n> | :switch-account -n<Enter> | Default (same as shipped) |
| <tab> | :next-field<Enter> | Default (same as shipped) |
| <backtab> | :prev-field<Enter> | Default (same as shipped) |
| <C-p> | :prev-tab<Enter> | Default (same as shipped) |
| <C-PgUp> | :prev-tab<Enter> | Default (same as shipped) |
| <C-n> | :next-tab<Enter> | Default (same as shipped) |
| <C-PgDn> | :next-tab<Enter> | Default (same as shipped) |

### aerc — compose::editor

| Key or directive | Action / exact command | Origin |
| --- | --- | --- |
| $noinherit | true | Default (same as shipped) |
| $ex | <C-x> | Default (same as shipped) |
| <C-k> | :prev-field<Enter> | Default (same as shipped) |
| <C-Up> | :prev-field<Enter> | Default (same as shipped) |
| <C-j> | :next-field<Enter> | Default (same as shipped) |
| <C-Down> | :next-field<Enter> | Default (same as shipped) |
| <C-p> | :prev-tab<Enter> | Default (same as shipped) |
| <C-PgUp> | :prev-tab<Enter> | Default (same as shipped) |
| <C-n> | :next-tab<Enter> | Default (same as shipped) |
| <C-PgDn> | :next-tab<Enter> | Default (same as shipped) |

### aerc — compose::review

| Key or directive | Action / exact command | Origin |
| --- | --- | --- |
| y | :send<Enter> # Send | Default (same as shipped) |
| n | :abort<Enter> # Abort (discard message, no confirmation) | Default (same as shipped) |
| s | :sign<Enter> # Toggle signing | Default (same as shipped) |
| x | :encrypt<Enter> # Toggle encryption to all recipients | Default (same as shipped) |
| v | :preview<Enter> # Preview message | Default (same as shipped) |
| p | :postpone<Enter> # Postpone | Default (same as shipped) |
| q | :choose -o d discard abort -o p postpone postpone<Enter> # Abort or postpone | Default (same as shipped) |
| e | :edit<Enter> # Edit (body and headers) | Default (same as shipped) |
| a | :attach -m<Enter> # Choose attachments with Yazi | Custom / local override |
| d | :detach<space> # Remove attachment | Default (same as shipped) |

### aerc — terminal

| Key or directive | Action / exact command | Origin |
| --- | --- | --- |
| $noinherit | true | Default (same as shipped) |
| $ex | <C-x> | Default (same as shipped) |
| <C-p> | :prev-tab<Enter> | Default (same as shipped) |
| <C-n> | :next-tab<Enter> | Default (same as shipped) |
| <C-PgUp> | :prev-tab<Enter> | Default (same as shipped) |
| <C-PgDn> | :next-tab<Enter> | Default (same as shipped) |

## tremc — every installed action and default key

Win+T opens tremc, the terminal UI for the Transmission daemon. Closing tremc with q
does not stop downloads. **Uppercase X asks the daemon to quit. Uppercase R deletes
downloaded data**, whereas lowercase r removes the torrent but keeps its files.
Space marks torrents; p pauses/resumes, a adds, / searches, f filters, s sorts.
Enter/l opens details. In details f selects Files; Enter opens a file through the
configured Yazi viewer. F1 or ? shows live help; backtick shows unbound actions.
No `[Keys]` overrides are configured, so the following keys are defaults extracted
from the installed `/usr/bin/tremc`. Empty key lists are explicitly marked unbound.
Some labels/groups depend on the Transmission RPC version.

| Key | Action | Context | Origin |
| --- | --- | --- | --- |
| F1, ? | List key bindings (list_key_bindings) | All | Default |
| Ctrl+W | Quit immediately (quit_now) | All | Default |
| q | Quit (quit) | Torrent list | Default |
| Backspace, q | Back to torrent list (leave_details) | Details | Default |
| Esc, Break | Unfocus or back to torrent list (go_back_or_unfocus) | Details | Default |
| X | Ask daemon to quit (daemon_quit) | All | Default |
| O | tremc options menu (options_dialog) | All | Default |
| Unbound | Save config file (save_config) | All | Default |
| o | Server options menu (server_options_dialog) | Torrent list | Default |
| C | Cycle torrent line height (toggle_compact_torrentlist) | Torrent list | Default |
| Unbound | Toggle torrent number in list (toggle_torrent_numbers) | Torrent list | Default |
| t | Toggle turtle mode (turtle_mode) | Torrent list | Default |
| ` | Show actions not mapped to keys (unmapped_actions) | All | Default |
| u | Set global upload (global_upload) | All | Default |
| d | Set global download limit (global_download) | All | Default |
| U | Set torrent maximum upload rate (torrent_upload) | All | Default |
| D | Set torrent maximum download rate (torrent_download) | All | Default |
| Unbound | Set group maximum upload rate (group_upload) | All | Default |
| Unbound | Set group maximum download rate (group_download) | All | Default |
| L | Set seed ratio limit for focused torrent (seed_ratio) | All | Default |
| + | Increase torrent bandwidth priority (bandwidth_priority_inc) | All | Default |
| - | Decrease torrent bandwidth priority (bandwidth_priority_dec) | All | Default |
| * | Toggle torrent honors session limits (honors_limits) | All | Default |
| Unbound | Toggle sequential download (sequential_download) | All | Default |
| p | Pause/Unpause torrent (pause_unpause_torrent) | All | Default |
| P | Pause/Unpause all torrents (pause_unpause_all_torrent) | All | Default |
| N | Start torrent now (start_now_torrent) | All | Default |
| v, y | Verify torrent (verify_torrent) | All | Default |
| m | Move torrent (move_torrent) | All | Default |
| F | Rename torrent/file (rename_torrent_selected_file) | All | Default |
| n | Reannounce torrent (reannounce_torrent) | All | Default |
| S | Show upload/download stats (show_stats) | All | Default |
| Delete, r | Remove selected/focused torrents, keeping content (remove) | Torrent list | Default |
| Unbound | Remove focused torrent keeping content (remove_focused) | Torrent list | Default |
| Ctrl+R | Remove selected torrents (remove_selected) | Torrent list | Default |
| Unbound | Remove selected/focused torrents and content (remove_data) | All | Default |
| Shift+Delete, R | Remove torrent and content (remove_focused_data) | All | Default |
| Unbound | Remove selected torrents and content (remove_selected_data) | Torrent list | Default |
| M | Copy Magnet Link to the System Clipboard (copy_magnet_link) | All | Default |
| Ctrl+L | Remove labels (remove_labels) | All | Default |
| b | Add label (add_label) | All | Default |
| B | Set labels (set_labels) | All | Default |
| Unbound | Set group (set_group) | All | Default |
| Unbound | Get group list (group_get) | All | Default |
| J | Move torrent down in queue (move_queue_down) | Torrent list | Default |
| K | Move torrent up in queue (move_queue_up) | Torrent list | Default |
| e | Profile menu (profile_menu) | Torrent list | Default |
| E | Save profile (save_profile) | Torrent list | Default |
| / | Find torrent (search_torrent) | Torrent list | Default |
| . | Find torrents matching regular expression (search_torrent_regex) | Torrent list | Default |
| Unbound | Find torrent (full text) (search_torrent_fulltext) | Torrent list | Default |
| Unbound | Find torrents matching regular expression (full text) (search_torrent_regex_fulltext) | Torrent list | Default |
| f | Set filter (set_filter) | Torrent list | Default |
| T | Add filter (add_filter) | Torrent list | Default |
| Ctrl+T | Add filter line (add_filter_line) | Torrent list | Default |
| I | Edit list of filters (edit_filters) | Torrent list | Default |
| ~ | Reverse filters (invert_filters) | Torrent list | Default |
| s | Sort torrent list (show_torrent_sort_order_menu) | Torrent list | Default |
| Space | Select/unselect torrent (select_unselect_torrent) | Torrent list | Default |
| A | Select/Deselect all torrents (select_unselect_torrents) | Torrent list | Default |
| i | Invert torrent selection (invert_selection_torrents) | Torrent list | Default |
| , | Select torrents matching pattern (select_search_torrent) | Torrent list | Default |
| < | Select torrents matching regex (select_search_torrent_regex) | Torrent list | Default |
| Unbound | Select torrents matching pattern (full text) (select_search_torrent_fulltext) | Torrent list | Default |
| Unbound | Select torrents matching regex (full text) (select_search_torrent_regex_fulltext) | Torrent list | Default |
| Enter, Right, l | Enter torrent details view (enter_details) | Torrent list | Default |
| a | Add torrent (add_torrent) | Torrent list | Default |
| Ctrl+A | Add torrent paused (add_torrent_paused) | Torrent list | Default |
| Esc, Break | Unfocus torrent (unfocus_torrent) | Torrent list | Default |
| o | Jump to overview (tab_overview) | Details | Default |
| f | Jump to file list (tab_files) | Details | Default |
| e | Jump to peer list (tab_peers) | Details | Default |
| t | Jump to tracker list (tab_trackers) | Details | Default |
| c | Jump to chunk list (tab_chunks) | Details | Default |
| Tab | Next details tab (next_details) | Details | Default |
| Shift+Tab | Previous details tab (prev_details) | Details | Default |
| Right, l | Raise file priority or Previous tab (file_priority_or_switch_details_next) | Details | Default |
| Left, h | Lower file priority or Previous tab (file_priority_or_switch_details_prev) | Details | Default |
| a | Select/Deselect all files or add torrent (add_tracker_or_select_all_files) | Details | Default |
| Enter | View file (view_file) | Files | Default |
| &#124; | Run command on file (view_file_command) | Files | Default |
| Unbound | View torrent's single file (view_torrent) | Torrent list | Default |
| Unbound | Run command on torrent's single file (view_torrent_command) | Torrent list | Default |
| J | Next diectory (move_to_next_directory) | Files | Default |
| K | Previous directory (move_to_previous_directory) | Files | Default |
| s | Sort file list (show_file_sort_order_menu) | Files | Default |
| V | Visually select files (visual_select_files) | Files | Default |
| , | Select files matching pattern (select_search_file) | Files | Default |
| A | Select/Deselect directory (select_files_dir) | Files | Default |
| / | Search file list (search_file) | Files | Default |
| C | Rename directory inside torrent (rename_dir) | Files | Default |
| < | Select files matching regex (select_search_file_regex) | Files | Default |
| . | Find files matching regex (search_file_regex) | Files | Default |
| i | Invert selection (invert_selection_files) | Files | Default |
| Space | Select/unselect file (select_file) | Files | Default |
| x | Show file info (file_info) | Files | Default |
| Delete, r | Remove tracker (remove_tracker) | Trackers | Default |
| Unbound | Remove all trackers from torrent (remove_all_trackers) | All | Default |
| PageUp, Ctrl+B | Page Up (page_up) | Movement | Default |
| PageDown, Ctrl+F | Page Down (page_down) | Movement | Default |
| Up, k, Ctrl+P | Up (line_up) | Movement | Default |
| Down, j, Ctrl+N | Down (line_down) | Movement | Default |
| Ctrl+K | Scroll one line up (scroll_line_up) | Movement | Default |
| Ctrl+I | Scroll one line down (scroll_line_down) | Movement | Default |
| Home, g | Home (go_home) | Movement | Default |
| End, G | End (go_end) | Movement | Default |

## Transmission — daemon, menus and CLI

Transmission is the background download engine; tremc is its UI. There is no
Transmission GTK application installed here, so GTK shortcuts are not claimed active.
Win+Shift+T offers Open client / Add magnet / Add torrent file / Downloads /
Pause all / Resume all. Win+T starts/connects to the managed daemon as needed.
The desktop menu reads your saved RPC authentication internally. Direct
`transmission-remote` commands need authentication from a private netrc file or
equivalent; the examples below intentionally do not embed the saved password.
Closing the UI keeps downloads running while the daemon/session is alive; this is
not a promise to download while the computer is powered off.

| Key or command | What it does | Origin |
| --- | --- | --- |
| transmission-remote --help | List all installed remote-control options | CLI, authentication required |
| transmission-remote -N /path/to/private.netrc -l | List torrents using a protected netrc authentication file | CLI, authentication required |
| transmission-remote -N /path/to/private.netrc -a /path/file.torrent | Add torrent file or magnet URI | CLI, authentication required |
| transmission-remote -N /path/to/private.netrc -t ID -S | Stop/pause one torrent | CLI, authentication required |
| transmission-remote -N /path/to/private.netrc -t ID -s | Start/resume one torrent | CLI, authentication required |
| transmission-remote -N /path/to/private.netrc -t ID -i | Show torrent information | CLI, authentication required |
| transmission-remote -N /path/to/private.netrc -t ID -f | List torrent files | CLI, authentication required |
| transmission-remote -N /path/to/private.netrc -t ID -v | Verify local torrent data | CLI, authentication required |
| transmission-remote -N /path/to/private.netrc -t ID -r | Remove torrent, keeping downloaded data | CLI, authentication required |
| transmission-remote -N /path/to/private.netrc -t ID -rad | Remove torrent AND delete data | CLI, authentication required |
| transmission-remote -N /path/to/private.netrc -t all -S | Pause all torrents | CLI, authentication required |
| transmission-remote -N /path/to/private.netrc -t all -s | Resume all torrents | CLI, authentication required |

## Neovim — modes, movement and editing defaults

Installed Neovim uses native packages, not Lazy or another plugin manager.
Leader is Space. Defaults below apply in Normal mode unless specified. Desktop
Alt shortcuts may be intercepted before Neovim sees them. Check `:verbose nmap KEY`
or `:verbose imap KEY` to see the actual mapping and where it was defined.
For exhaustive built-in help use `:help index`, `:help quickref` and `:help vim-differences`.

| Key or command | What it does | Origin |
| --- | --- | --- |
| Esc / Ctrl+[ | Return to Normal mode | Default |
| i / a | Insert before cursor / append after cursor | Default |
| I / A | Insert at line start / append at line end | Default |
| o / O | Open line below / above and enter Insert | Default |
| v / V / Ctrl+V | Character / line / block Visual selection | Default |
| h / l | Move left / right | Default |
| j / k | Move wrapped screen rows without a count; with count move physical lines (custom override) | Default |
| w / b / e | Next word start / previous word start / word end | Default |
| W / B / E | Same motions using whitespace-delimited WORDs | Default |
| 0 / ^ / $ | Start of line / first nonblank / end of line | Default |
| gg / G / 25G | First line / last line / line 25 | Default |
| { / } | Previous / next paragraph | Default |
| % | Jump to matching bracket | Default |
| f<char> / F<char> | Find character forward / backward on line | Default |
| t<char> / T<char> | Move just before character forward / backward | Default |
| ; / , | Repeat / reverse latest character-find motion | Default |
| Ctrl+D / Ctrl+U | Scroll half page down / up | Default |
| Ctrl+F / Ctrl+B | Scroll page down / up | Default |
| zz / zt / zb | Center cursor line / put at top / bottom | Default |
| Ctrl+O / Ctrl+I | Previous / next jump location | Default |
| ma / 'a / `a | Set mark a / jump to its line / exact position | Default |
| dd / 3dd | Delete/cut line / three lines | Default |
| dw / diw / daw | Delete to next word / inner word / word plus surrounding space | Default |
| d$ / D | Delete to end of line | Default |
| x / X | Delete character under / before cursor | Default |
| cc / ciw / C | Change line / inner word / to end of line | Default |
| yy / Y / yw | Yank line / to end of line / word motion | Default |
| p / P | Paste after / before cursor | Default |
| "+y / "+p | Copy to / paste from system clipboard when clipboard provider is available | Default |
| u / Ctrl+R | Undo / redo | Default |
| . | Repeat last editing change | Default |
| r<char> / R | Replace one character / enter Replace mode | Default |
| J | Join next line | Default |
| > / < (Visual) | Indent / unindent selection | Default |
| >> / << | Indent / unindent line | Default |
| == / gg=G | Reindent line / whole file | Default |
| ~ / g~motion / gu / gU | Toggle / change case using a motion | Default |
| qa ... q / @a / @@ | Record macro a / replay macro a / repeat last macro | Default |
| :w / :w filename | Save / save as | Default |
| :q / :wq / :q! | Quit / save and quit / discard buffer edits and quit | Default |
| :wa / :qa / :wqa | Save all / quit all / save all and quit | Default |
| :e filename | Open or create a file | Default |
| :enew | Open empty buffer | Default |
| :set paste / :set nopaste | Toggle paste mode if terminal paste needs it | Default |
| Ctrl+R + (Insert) | Insert system clipboard register | Default |
| Ctrl+W (Insert) | Delete previous word | Default |
| Ctrl+U (Insert) | Delete input back to line start | Default |
| Ctrl+O (Insert) | Execute one Normal-mode command then resume Insert | Default |

## Neovim — search, buffers, splits, tabs and diagnostics

| Key or command | What it does | Origin |
| --- | --- | --- |
| /text / ?text | Search forward / backward; Enter confirms | Default |
| n / N | Next / previous search match | Default |
| * / # | Search word under cursor forward / backward | Default |
| :noh | Clear search highlighting | Default |
| :%s/old/new/g | Replace all matches in file | Default |
| :%s/old/new/gc | Replace all with confirmation | Default |
| :s/old/new/g | Replace matches on current line | Default |
| :vimgrep /pattern/gj **/* | Search project files into quickfix (can be slow in large trees) | Default |
| :copen / :cclose | Open / close quickfix list | Default |
| :cnext / :cprevious | Next / previous quickfix entry | Default |
| :ls / :buffers | List buffers | Default |
| :b name / :buffer N | Switch to buffer by name / number | Default |
| :bnext / :bprevious | Next / previous buffer | Default |
| :bdelete | Close buffer; unsaved changes require save or explicit ! | Default |
| Ctrl+^ | Alternate buffer | Default |
| :split file / :vsplit file | Horizontal / vertical split | Default |
| Ctrl+W then h/j/k/l | Focus split left/down/up/right | Default |
| Ctrl+W then w | Cycle windows | Default |
| Ctrl+W then c / o | Close split / keep only current split | Default |
| Ctrl+W then = | Equalize split sizes | Default |
| Ctrl+W then + / - / > / < | Adjust split height / width | Default |
| :tabnew file | Create Neovim tab page | Default |
| gt / gT | Next / previous Neovim tab | Default |
| :tabclose | Close current tab page | Default |
| gf | Open file under cursor (overridden on Markdown links) | Default |
| :find filename | Find file using configured path | Default |
| :terminal | Open terminal in current window | Default |
| Ctrl+backslash then Ctrl+N (Terminal) | Leave terminal input mode | Default |
| i (terminal buffer Normal mode) | Re-enter terminal input | Default |
| :help topic | Open local Neovim help | Default |
| Ctrl+] / Ctrl+T (help) | Follow help tag / jump back | Default |
| :map / :nmap / :imap | List effective mappings | Default |
| :verbose nmap KEY | Show mapping definition and originating config | Default |
| :checkhealth | Check installed runtime and integrations | Default |

## Neovim — local custom keys and C development

| Key or command | What it does | Origin |
| --- | --- | --- |
| Space e | Toggle netrw tree sidebar using :Lexplore 28 | Custom |
| Space n / Space p | Next / previous compiler quickfix diagnostic | Custom |
| Space h | Clear search highlighting | Custom |
| F5 / :CBuild | Save and build C source; nearest Makefile or GCC/Clang C17 | Custom |
| F6 / :CRun | Build then run in terminal; Makefile projects ask executable path | Custom |
| Esc then Esc (Terminal) | Leave terminal input mode | Custom |
| Tab (Insert) | Accept visible Minuet AI suggestion; otherwise insert Tab | Custom |
| Space / or Space f f (guide only) | Open live fuzzy shortcut search | Custom |
| :Shortcuts | Open this guide from any buffer | Custom |
| :ShortcutSearch | Open this guide and fuzzy search from any buffer | Custom |

| Key or command | What it does | Origin |
| --- | --- | --- |
| Ctrl+N / Ctrl+P (Insert) | Next / previous built-in completion candidate | Default |
| Ctrl+X then Ctrl+F (Insert) | Complete filesystem path | Default |
| Ctrl+X then Ctrl+O (Insert, C/C++) | Built-in C omni completion; not a language server | Default |
| Ctrl+Y / Ctrl+E (completion menu) | Accept / cancel completion | Default |
| Enter (netrw sidebar) | Open hovered file in editing window | Default |
| - (netrw) | Parent directory | Default |
| d / % / R / D (netrw) | Create directory / create file / rename / delete; confirm destructive operations | Default |
| i (netrw) | Cycle listing style | Default |
| :bdelete! (terminal Normal mode) | Force-close terminal buffer; may terminate a running program | Default |

C builds use `-std=c17 -Wall -Wextra -Wpedantic -g` for single files and put
the executable beside the source. Makefile projects control their flags/output.
C indentation is four spaces. Makefiles retain tabs. There is **no configured
LSP server, Telescope, nvim-cmp, orgmode.nvim or lazy.nvim** in this setup.

## Markdown notes — links, preview, images and organization

Your org-style workflow currently uses ordinary Markdown, Markview and the custom
link helper; it is not orgmode.nvim. Use `#`, `##`, `###` headings; `-` lists;
`- [ ]` tasks and `- [x]` completed tasks; Markdown tables; and fenced code blocks.
Checkboxes are edited as text: no task-toggle key is configured. Folding headings
or inserting new list markers automatically is not configured either.

Use `[Note](notes/topic.md)` or `[[notes/topic]]` to connect files. The helper creates
missing parent directories and files; wiki targets without an extension get `.md`.
Relative paths are resolved beside the current note. URL targets open in the
configured browser. File fragments after # are stripped; heading navigation is
not implemented. Enter/gf/gx do nothing useful away from a recognized inline or
wiki link. Markdown rendering uses two-space indentation.

| Key or command | What it does | Origin |
| --- | --- | --- |
| Enter / gf / gx (Markdown Normal) | Open link under cursor; create missing local target note | Custom / configured plugin commands |
| Space m t | Toggle Markview rendered Markdown preview for current buffer | Custom / configured plugin commands |
| Space m s | Toggle separate Markview split preview | Custom / configured plugin commands |
| :Markview toggle | Toggle current preview | Custom / configured plugin commands |
| :Markview splitToggle | Toggle rendered split preview | Custom / configured plugin commands |
| :help markview.nvim | Open installed Markview reference | Custom / configured plugin commands |
| :edit notes/topic.md | Create/open note directly | Custom / configured plugin commands |
| :write | Save current note | Custom / configured plugin commands |
| /TODO | Search task text using normal Neovim search | Custom / configured plugin commands |
| Space / (this guide) | Fuzzy search commands and shortcuts | Custom / configured plugin commands |

### Installed plugins and their actual controls

**Markview** renders headings, bullets, checkboxes, tables, code and links. It renders
in Normal/command/Insert modes, with hybrid editing in Insert. Its gx mapping is disabled
so the custom note-link helper handles gx. Controls are Space m t and Space m s above.

**image.nvim** displays inline Markdown images in interactive Kitty; tmux passthrough
is enabled. No image manipulation shortcut is configured. Local image embeds such as
`![diagram](images/diagram.png)` render automatically. Remote image downloading is
enabled and can use network/data on opening a document. Images clear while inserting
and render only while the editor is focused. It is disabled in headless sessions.

**Minuet AI / Gemini** provides inline suggestions. Context is sent to Google when
enabled, so use `:AIToggle` when you do not want suggestions/network requests in a buffer.
This guide is opened with AI auto-trigger disabled for its buffer. API credentials
are kept separately and never included in this document.

| Key or command | What it does | Origin |
| --- | --- | --- |
| Tab (Insert, AI suggestion visible) | Accept complete suggestion | Custom Minuet/Gemini configuration |
| Ctrl+G then Ctrl+J (Insert) | Accept one suggestion line | Custom Minuet/Gemini configuration |
| Ctrl+G then Ctrl+N (Insert) | Next suggestion | Custom Minuet/Gemini configuration |
| Ctrl+G then Ctrl+P (Insert) | Previous suggestion | Custom Minuet/Gemini configuration |
| Ctrl+] (Insert) | Dismiss suggestion | Custom Minuet/Gemini configuration |
| :AIToggle | Toggle automatic suggestions in current buffer | Custom Minuet/Gemini configuration |
| :GeminiStatus | Show whether key exists and current model; does not show key | Custom Minuet/Gemini configuration |
| :GeminiCheck | Test API access; makes network request | Custom Minuet/Gemini configuration |
| :GeminiSetup | Enter API key in masked prompt and test access | Custom Minuet/Gemini configuration |

## sxiv / nsxiv — image viewer

`sxiv` is a symlink to nsxiv. Uppercase P by itself means previous marked image;
printing requires the Ctrl+X prefix. The external handler receives marked files
in thumbnail mode, otherwise the current file. Ctrl+P alone is **not** a print
binding; it moves backward through animation frames in image mode.

| Key or command | What it does | Origin |
| --- | --- | --- |
| Ctrl+X then Shift+P | Open print dialog for current/marked images | Custom |
| Ctrl+X then a | Image action menu (includes Print images) | Custom |
| Ctrl+X then p | Copy path(s) to clipboard | Custom |
| Ctrl+X then y | Copy image to clipboard | Custom |
| Ctrl+X then o | Open containing folder | Custom |
| Ctrl+X then e | Open configured/available image editor | Custom |
| Ctrl+X then i | Show image dimensions and information | Custom |
| Ctrl+X then w | Apply wallpaper and matching lock screen | Custom |

| Key or command | What it does | Origin |
| --- | --- | --- |
| Enter | Switch image / thumbnail mode | Default |
| q / Q | Quit; Q also outputs current file with -o when no marks | Default |
| h/j/k/l / arrows (thumbnails) | Move thumbnail selection | Default |
| h/j/k/l / arrows (image) | Pan image | Default |
| n / Space | Next image | Default |
| p / Backspace | Previous image | Default |
| g / G | First / last image; a numeric count selects image index | Default |
| [ / ] | Jump backward / forward ten images | Default |
| m / M | Mark image / mark range from previous mark | Default |
| Ctrl+M / Ctrl+U | Invert / clear marks | Default |
| N / P | Next / previous marked image | Default |
| + / - | Zoom in / out | Default |
| = | 100% zoom; count sets a percentage | Default |
| w / W / F | Fit large image without upscaling / fit window / fill window | Default |
| e / E | Fit width / height | Default |
| f / b | Toggle fullscreen / status bar | Default |
| r / R (thumbnail) | Reload image / reload all thumbnails | Default |
| D | Remove image from viewer list, not delete file | Default |
| < / > / ? | Rotate left 90° / right 90° / 180° | Default |
| &#124; / _ | Flip horizontally / vertically | Default |
| s | Toggle slideshow; count sets delay | Default |
| a / A | Toggle antialiasing / transparency display | Default |
| Ctrl+N / Ctrl+P | Next / previous animation frame | Default |
| Ctrl+A / Ctrl+Space | Play/pause animation | Default |
| { / } / Ctrl+G | Decrease / increase / reset gamma | Default |

## Zathura — PDF viewer

| Key or command | What it does | Origin |
| --- | --- | --- |
| Ctrl+P | Open GtkLP print dialog for current PDF | Custom |

| Key or command | What it does | Origin |
| --- | --- | --- |
| j/k / arrows | Scroll down/up | Default |
| Space / Shift+Space | Scroll forward/back a page | Default |
| J / K | Next / previous page | Default |
| gg / G / 5G | First / last / page 5 | Default |
| / / ? | Search forward / backward | Default |
| n / N | Next / previous search result | Default |
| a / s | Fit height / width | Default |
| + / - / = | Zoom in / out / original zoom | Default |
| f / F | Follow link / display link target | Default |
| Tab | Show table of contents | Default |
| d | Toggle dual-page layout | Default |
| r | Rotate 90 degrees | Default |
| Ctrl+R | Recolor/invert | Default |
| F5 / F11 | Presentation / fullscreen | Default |
| o / O | Open another document | Default |
| m<letter> / '<letter> | Set / jump to quickmark | Default |
| :print | Built-in GTK 4 print dialog; this installation lists Print to File only | Default |
| :write filename | Save PDF | Default |
| q | Quit | Default |

## Firefox — profiles, bookmarks and browser defaults

Default launcher opens temporary private Firefox. Bookmark rules route Netflix,
Prime Video and JioHotstar to Persnal; Royal Ledger, Seller Central and Seller Flow
to Shop. Persnal is encrypted with gocryptfs and prompts to unlock on a cold unlock.
An already unlocked/running profile does not need mounting again. Closing a browser
window alone is not proof that its encrypted profile was locked.
Sources: ~/.local/bin/firefox-profiles and ~/.config/firefox-launcher/sites.json.

| Key or command | What it does | Origin |
| --- | --- | --- |
| Win+F | Open temporary private Firefox | Desktop custom / Firefox defaults as described |
| Win+Shift+F | Choose Firefox profile | Desktop custom / Firefox defaults as described |
| Win+Shift+B | Open bookmark menu or add bookmark | Desktop custom / Firefox defaults as described |
| Ctrl+L | Focus address bar | Desktop custom / Firefox defaults as described |
| Ctrl+T / Ctrl+W | New tab / close tab | Desktop custom / Firefox defaults as described |
| Ctrl+Shift+T | Restore closed tab (private browsing restoration is limited) | Desktop custom / Firefox defaults as described |
| Ctrl+Tab / Ctrl+Shift+Tab | Next / previous tab | Desktop custom / Firefox defaults as described |
| Alt+Left / Alt+Right | Back / forward | Desktop custom / Firefox defaults as described |
| Ctrl+R / Ctrl+Shift+R | Reload / reload bypassing cache | Desktop custom / Firefox defaults as described |
| Ctrl+F | Find on page | Desktop custom / Firefox defaults as described |
| Ctrl+D | Bookmark current page | Desktop custom / Firefox defaults as described |
| Ctrl+P | Browser print dialog | Desktop custom / Firefox defaults as described |
| Ctrl+Plus / Ctrl+Minus / Ctrl+0 | Zoom in / out / reset | Desktop custom / Firefox defaults as described |
| F11 | Fullscreen | Desktop custom / Firefox defaults as described |
| about:logins | Saved logins page | Desktop custom / Firefox defaults as described |

## Kitty terminal, shell and tmux

Kitty has no custom map lines in kitty.conf; the table lists standard default keys.
Ctrl+Shift+P is globally captured for the print picker, so Kitty's default prefix
using that chord is unavailable here. tmux prefix is **Ctrl+A**, not the default
Ctrl+B. tmux keys below require pressing/releasing Ctrl+A first unless stated.

| Key or command | What it does | Origin |
| --- | --- | --- |
| Ctrl+Shift+C / Ctrl+Shift+V | Copy selection / paste clipboard in Kitty | Default |
| Ctrl+Shift+Enter | New Kitty window (split) | Default |
| Ctrl+Shift+T | New Kitty tab | Default |
| Ctrl+Shift+Q | Close Kitty tab | Default |
| Ctrl+Shift+W | Close Kitty window | Default |
| Ctrl+Shift+Right / Ctrl+Shift+Left | Next / previous Kitty tab | Default |
| Ctrl+Shift+] / Ctrl+Shift+[ | Next / previous Kitty window | Default |
| Ctrl+Shift+L | Cycle Kitty layouts | Default |
| Ctrl+Shift+Plus / Ctrl+Shift+Minus | Increase / decrease terminal font size | Default |
| Ctrl+Shift+Backspace | Reset font size | Default |
| Ctrl+C (shell) | Interrupt foreground command | Default |
| Ctrl+D (empty shell prompt) | End input / exit shell | Default |
| Ctrl+Z (shell) | Suspend foreground job; fg resumes it | Default |
| Ctrl+R (bash) | Reverse history search | Default |
| Ctrl+A / Ctrl+E (bash outside tmux) | Start / end of input line | Default |
| Ctrl+W / Ctrl+U / Ctrl+K (bash) | Delete previous word / back to start / to end | Default |
| Tab (shell) | Complete command/path | Default |

| Key or command | What it does | Origin |
| --- | --- | --- |
| Ctrl+A then h/j/k/l | Focus tmux pane left/down/up/right | Custom tmux |
| Ctrl+A then Ctrl+H/J/K/L | Resize pane by five cells | Custom tmux |
| Ctrl+A then b | Paste tmux buffer to pane on the right | Custom tmux |
| Ctrl+A then o | Select configured active-only layout (requires tmux layout support) | Custom tmux |
| Ctrl+A then Alt+- / Alt+&#124; | Even-vertical / even-horizontal layout | Custom tmux |
| Ctrl+A then Alt+R | Rotate tmux window panes | Custom tmux |
| Enter (tmux vi copy mode) | Copy selection to system clipboard using xsel | Custom tmux |
| Shift+mouse-wheel-up | Enter tmux history/copy mode | Custom tmux |
| Mouse wheel over Codex | Scroll tmux history when configured conditions match | Custom tmux |

| Key or command | What it does | Origin |
| --- | --- | --- |
| Ctrl+A then c | Create tmux window | tmux defaults with custom prefix |
| Ctrl+A then n / p | Next / previous tmux window | tmux defaults with custom prefix |
| Ctrl+A then 0..9 | Select tmux window number | tmux defaults with custom prefix |
| Ctrl+A then , | Rename tmux window | tmux defaults with custom prefix |
| Ctrl+A then % / " | Split vertically / horizontally | tmux defaults with custom prefix |
| Ctrl+A then x | Kill pane after confirmation | tmux defaults with custom prefix |
| Ctrl+A then z | Toggle pane zoom | tmux defaults with custom prefix |
| Ctrl+A then d | Detach tmux session; processes continue | tmux defaults with custom prefix |
| Ctrl+A then s / w | Session / window chooser | tmux defaults with custom prefix |
| Ctrl+A then [ | Enter copy mode; move with vi keys | tmux defaults with custom prefix |
| Space then movement (vi copy mode) | Start/extend selection | tmux defaults with custom prefix |
| q (copy mode) | Exit copy mode | tmux defaults with custom prefix |
| Ctrl+A then ? | List all effective tmux bindings | tmux defaults with custom prefix |
| Ctrl+A then : | tmux command prompt | tmux defaults with custom prefix |
| Ctrl+A then :send-prefix Enter | Send literal configured prefix Ctrl+A to the application (old Ctrl+B send-prefix binding is unbound) | tmux defaults with custom prefix |

## mpv — video and audio playback defaults

| Key or command | What it does | Origin |
| --- | --- | --- |
| Space / p | Pause / resume | Default |
| q / Q | Quit / quit and remember playback position | Default |
| Left / Right | Seek back / forward five seconds | Default |
| Up / Down | Seek forward / back one minute | Default |
| Shift+Left / Shift+Right | Precise one-second seek | Default |
| < / > | Previous / next playlist item | Default |
| 9 / 0 | Volume down / up | Default |
| m | Mute | Default |
| f | Fullscreen | Default |
| s / S | Screenshot / screenshot without subtitles | Default |
| j / J | Next / previous subtitle track | Default |
| v | Toggle subtitle visibility | Default |
| # | Cycle audio tracks | Default |
| [ / ] / Backspace | Decrease / increase / reset speed | Default |
| . / , | Step forward / backward one frame while paused | Default |
| o / O | Show progress / toggle persistent progress | Default |
| i / I | Show statistics / toggle persistent statistics | Default |

## Passwords, menus, screenshots and file workflows

| Key or command | What it does | Origin |
| --- | --- | --- |
| Win+Shift+P | Password picker; choose account, then paste password with Ctrl+V | Custom workflow / standard commands |
| pass insert site/account | Add encrypted login using local password prompts | Custom workflow / standard commands |
| pass generate -c site/account 24 | Generate password and copy it to clipboard | Custom workflow / standard commands |
| pass -c site/account | Copy existing password without printing it in terminal | Custom workflow / standard commands |
| Win+Shift+C | Clipboard history chooser | Custom workflow / standard commands |
| Win+Shift+E | Emoji chooser | Custom workflow / standard commands |
| Win+Shift+D | Drive menu: mount/open/unmount/safely remove | Custom workflow / standard commands |
| Win+Shift+O | OCR: select screen area, copy recognized text | Custom workflow / standard commands |
| Print | Screenshot menu: screen/window/area | Custom workflow / standard commands |
| Shift+Print | Capture selected area directly | Custom workflow / standard commands |
| Esc / right-click (screenshot/OCR selection) | Cancel selection | Custom workflow / standard commands |
| Win+Shift+W | Wallpaper browser in sxiv | Custom workflow / standard commands |
| Win+Shift+S | Screenshot browser in sxiv | Custom workflow / standard commands |
| Win+Shift+L | Amazon labels picker; select PDFs with Space then Enter | Custom workflow / standard commands |
| Win+Shift+X | Choose existing tmux/Codex session or create one in chosen folder | Custom workflow / standard commands |
| Alt+Shift+R | Reload menu for desktop components | Custom workflow / standard commands |
| Esc (dmenu-style menus) | Cancel menu | Custom workflow / standard commands |
| Up/Down or Ctrl+P/Ctrl+N (dmenu) | Move selection where supported; Enter confirms | Custom workflow / standard commands |

Screenshots are saved in ~/Pictures/Screenshots and copied to clipboard. The
password manager uses pass/GPG; unlock prompts are local. A private Firefox window
does not save streaming logins; use the configured persistent Persnal profile for
Netflix/Prime/Hotstar. Do not put passwords, API keys, mail account files or torrent
RPC credentials into notes or this guide.

## Known conflicts and limits — read before assuming a key is broken

- **Alt+Ctrl+P is defined twice** in sxhkd: screenshot menu and monitor refresh.
  This is an existing conflict; the documentation update leaves both unchanged.
  Use Print for screenshots. Use the command ~/.local/bin/monitor-layout --refresh
  if monitor refresh does not respond to that chord.
- Desktop Alt+N dismisses a notification and can intercept nchat contact search.
- **Ctrl+Shift+P is global printing**, including inside terminal applications.
- sxiv printing is **Ctrl+X then Shift+P**, not Ctrl+P. Lowercase p after Ctrl+X copies paths.
- aerc Ctrl+P switches tabs; Yazi/Zathura Ctrl+P prints. Context matters.
- Yazi **t t** creates a tab in version 26.9.1; a trailing / makes a new directory.
- Markdown links support local files and wiki links, not heading jumps. This is a
  Markdown workflow, not an installed Org-mode task/calendar system.
- Only native Neovim packages currently installed are documented. No invented
  Telescope/LSP/Org-mode leader shortcuts are listed as active.
- Old SHORTCUTS.txt is a pointer to this guide; it is no longer the maintained list.
- Defaults can change with package upgrades. Regenerate and compare pinned defaults
  when upgrading; use the application's live help for the running version.

## Sources, live help and maintenance

### Local configuration links

- [Desktop shortcuts](/home/master/.config/sxhkd/sxhkdrc)
- [Desktop help launcher](/home/master/.local/bin/desktop-control)
- [Yazi keys](/home/master/.config/yazi/keymap.toml)
- [Yazi file openers](/home/master/.config/yazi/yazi.toml)
- [nchat keys](/home/master/.config/nchat/key.conf)
- [aerc keys](/home/master/.config/aerc/binds.conf)
- [Neovim configuration](/home/master/.config/nvim/init.lua)
- [Markdown configuration](/home/master/.config/nvim/lua/markdown_setup.lua)
- [Markdown link helper](/home/master/.config/nvim/lua/markdown_links.lua)
- [sxiv actions](/home/master/.local/bin/sxiv-tools)
- [Zathura keys](/home/master/.config/zathura/zathurarc)
- [tmux configuration](/home/master/.tmux.conf)
- [Kitty configuration](/home/master/.config/kitty/kitty.conf)
- [Print picker](/home/master/.local/bin/print-files)
- [Guide generator](/home/master/.local/bin/update-shortcut-guide)

### Authoritative defaults and deeper help

- Yazi 26.9.1 defaults: https://github.com/sxyazi/yazi/blob/v26.9.1/yazi-config/preset/keymap-default.toml
- Yazi keymap commands: https://yazi-rs.github.io/docs/configuration/keymap/
- nchat: installed `man nchat`, Ctrl+G help, Ctrl+O additional commands; upstream https://github.com/d99kris/nchat
- aerc: `?`, `:help keys`, `man aerc`, `man aerc-binds`; installed /usr/share/aerc/binds.conf
- tremc: installed /usr/bin/tremc action definitions; F1 / ? and backtick menus
- Transmission: `man transmission-remote` and `transmission-remote --help`
- Neovim: `:help index`, `:help quickref`, `:help netrw`, `:help usr_02.txt`
- Markview: `:help markview.nvim`; installed plugin docs under ~/.local/share/nvim/site/pack/markdown/start/markview.nvim/doc
- Minuet: ~/.local/share/nvim/site/pack/ai/start/minuet-ai.nvim/README.md
- image.nvim: ~/.local/share/nvim/site/pack/markdown/start/image.nvim/README.md
- sxiv/nsxiv: `man nsxiv`; Zathura: `man zathura`; Kitty: `man kitty`; tmux: `Ctrl+A ?` / `man tmux`
- Printing: `man lp`, `man cancel`, `man lpstat`; Canon tray priority: https://files.canon-europe.com/files/soft26391/Manual/LBP2900_UG_EN.PDF

### Updating without losing accuracy

Run `~/.local/bin/update-shortcut-guide` after changing local bindings. It rereads
desktop, aerc, nchat, Yazi overrides and the installed tremc action table. It compares
aerc to installed defaults and Yazi to the cached pinned 26.9.1 default file.
Curated Neovim/other-app explanations live in the generator and must be reviewed when
their configuration changes. It does not claim those static sections self-update.
No credentials, chat history, message bodies or browser databases are read by the
generator. This generated file will be overwritten when regenerated; keep personal
notes in another linked Markdown document.
