#!/usr/bin/python3
"""Search installed desktop applications using their names and themed icons."""
import json
from pathlib import Path
import subprocess
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GLib

class Launcher(Gtk.Window):
    def __init__(self):
        super().__init__(title='Applications')
        self.set_wmclass('desktop-launcher', 'DesktopLauncher')
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(600, 490)
        self.set_resizable(False)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.connect('destroy', Gtk.main_quit)
        self.connect('key-press-event', self.key)
        try:
            theme = json.loads((Path.home()/'.config/desktop-themes/current.json').read_text())
            c = theme['colors']
        except (OSError, ValueError, KeyError):
            c = dict(bg='#202321', fg='#e7e9e2', accent='#a8b99a', surface='#303630', muted='#939c90', overlay='#555f53')
        css = '''window { background: BG; color: FG; border: 1px solid OVERLAY; border-radius: 10px; }
        * { font-family: Inter; font-size: 14px; }
        label { color: FG; }
        .heading { font-size: 18px; font-weight: 600; }
        .hint { color: MUTED; font-size: 12px; }
        entry { background: SURFACE; color: FG; padding: 10px; border: 1px solid OVERLAY; border-radius: 7px; box-shadow: none; }
        entry:focus { border-color: ACCENT; }
        list, row { background: transparent; }
        row { padding: 9px 10px; border-radius: 6px; }
        row:selected { background: SURFACE; }
        row:hover { background: SURFACE; }
        scrolledwindow { border: none; }
        '''
        for key in ('bg', 'fg', 'accent', 'surface', 'muted', 'overlay'):
            css = css.replace(key.upper(), c[key])
        provider = Gtk.CssProvider(); provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        outer.set_border_width(20); self.add(outer)
        title = Gtk.Label(label='Applications', xalign=0); title.get_style_context().add_class('heading'); outer.pack_start(title, False, False, 0)
        self.search = Gtk.SearchEntry(placeholder_text='Search applications…')
        self.search.connect('search-changed', self.filter)
        self.search.connect('activate', self.activate_selected)
        outer.pack_start(self.search, False, False, 0)
        scroll = Gtk.ScrolledWindow(); scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.list = Gtk.ListBox(); self.list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.list.connect('row-activated', self.launch)
        scroll.add(self.list); outer.pack_start(scroll, True, True, 0)
        self.footer = Gtk.Label(xalign=0); self.footer.get_style_context().add_class('hint'); outer.pack_start(self.footer, False, False, 0)
        self.apps = sorted((a for a in Gio.AppInfo.get_all() if a.should_show()), key=lambda a: a.get_display_name().casefold())
        self.filter()
        self.show_all(); self.search.grab_focus()

    def filter(self, *_):
        query = self.search.get_text().casefold().strip()
        for row in self.list.get_children(): self.list.remove(row)
        for app in self.apps:
            keywords = ' '.join(app.get_keywords() or []) if hasattr(app, 'get_keywords') else ''
            haystack = ' '.join((app.get_display_name(), app.get_description() or '', app.get_executable() or '', keywords)).casefold()
            if not all(word in haystack for word in query.split()): continue
            row = Gtk.ListBoxRow(); row.app = app
            box = Gtk.Box(spacing=14); row.add(box)
            icon = app.get_icon() or Gio.ThemedIcon.new('application-x-executable')
            img = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.DIALOG); img.set_pixel_size(32); box.pack_start(img, False, False, 0)
            label = Gtk.Label(label=app.get_display_name(), xalign=0); box.pack_start(label, True, True, 0)
            row.set_tooltip_text(app.get_description() or app.get_display_name()); self.list.add(row)
        self.list.show_all()
        rows = self.list.get_children()
        if rows: self.list.select_row(rows[0])
        self.footer.set_text(('No matching applications' if not rows else f'{len(rows)} applications') + '    ·    ↑ ↓ navigate    Enter open    Esc close')

    def key(self, _, event):
        if event.keyval == Gdk.KEY_Escape: self.destroy(); return True
        if event.keyval in (Gdk.KEY_Down, Gdk.KEY_Up):
            rows = self.list.get_children()
            if rows:
                selected = self.list.get_selected_row()
                index = selected.get_index() if selected else 0
                row = rows[max(0, min(len(rows)-1, index + (1 if event.keyval == Gdk.KEY_Down else -1)))]
                self.list.select_row(row); row.grab_focus()
            return True
        # Typing while navigating returns to the search field.
        if self.get_focus() != self.search and event.string and event.string.isprintable() and not event.state & (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD1_MASK):
            self.search.grab_focus(); self.search.set_position(-1)
        return False

    def activate_selected(self, *_):
        row = self.list.get_selected_row()
        if row: self.launch(self.list, row)

    def launch(self, _, row):
        try:
            context = Gdk.Display.get_default().get_app_launch_context()
            context.set_timestamp(Gtk.get_current_event_time())
            if row.app.launch([], context): self.destroy()
        except GLib.Error as error:
            self.footer.set_text('Unable to open application')
            subprocess.run(['notify-send', 'Application could not open', str(error)], check=False)

if __name__ == '__main__':
    launcher = Launcher()
    if '--smoke-test' in sys.argv:
        def check():
            assert launcher.list.get_children(), 'No application entries'
            launcher.search.set_text('firefox'); launcher.filter()
            assert any('firefox' in r.app.get_display_name().casefold() for r in launcher.list.get_children()), 'Search failed'
            launcher.search.set_text('zzzz-no-such-app'); launcher.filter()
            assert not launcher.list.get_children(), 'Empty state failed'
            launcher.search.set_text(''); launcher.filter()
            subprocess.run(['import', '-window', 'root', str(Path.home()/'.cache/desktop-polish/launcher.png')], check=True)
            print('Launcher displayed; icons, search, and empty state checked.', flush=True)
            launcher.destroy(); return False
        GLib.timeout_add(700, check)
    Gtk.main()
