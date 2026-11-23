import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('switcher', Path(__file__).with_name('theme_switcher.py'))
switcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(switcher)


class SwitcherTests(unittest.TestCase):
    def test_void_slick_greeter_session_uses_desktop_filename(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            self.assertIsNone(switcher.slick_greeter_session(directory))
            (directory / 'slick-greeter.desktop').write_text('[Desktop Entry]\nExec=slick-greeter\n')
            self.assertEqual(switcher.slick_greeter_session(directory), 'slick-greeter')

    def test_alternative_slick_greeter_filename_is_supported(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory / 'lightdm-slick-greeter.desktop').write_text('[Desktop Entry]\n')
            self.assertEqual(switcher.slick_greeter_session(directory), 'lightdm-slick-greeter')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.root = self.home / '.config/desktop-themes'
        self.cache = self.home / '.cache/desktop-themes'
        for key, value in {'HOME': self.home, 'ROOT': self.root, 'CACHE': self.cache,
                           'STATE': self.root / 'current.json',
                           'PREVIOUS': self.root / 'previous.json'}.items():
            p = patch.object(switcher, key, value)
            p.start()
            self.addCleanup(p.stop)
        env = patch.dict(os.environ, {'XDG_CACHE_HOME': str(self.home / '.cache')})
        env.start()
        self.addCleanup(env.stop)
        self.directory = self.root / 'themes/example'
        self.directory.mkdir(parents=True)
        (self.directory / 'wallpaper.png').write_bytes(b'wallpaper')
        self.theme = {'name': 'Example', 'colors': {key: '#123456' for key in switcher.COLOR_KEYS},
                      'gtk': 'Example', 'icons': 'Example', 'cursor': 'Example',
                      'ui_font': 'Inter', 'mono_font': 'DejaVu Sans Mono'}
        self.save_theme()
        self.template = self.root / 'templates/.config/alacritty/alacritty.toml.tmpl'
        self.template.parent.mkdir(parents=True)
        self.template.write_text('[window]\nopacity = {{opacity}}\n[colors.primary]\nbackground = "{{bg}}"\n')

    def save_theme(self):
        (self.directory / 'theme.json').write_text(json.dumps(self.theme))

    def load(self):
        with patch.object(switcher, 'find_asset', return_value=self.directory):
            return switcher.load_theme('example')

    def test_invalid_palette_is_rejected_before_configuration_changes(self):
        self.theme['colors']['accent'] = '$(touch unwanted)'
        self.save_theme()
        with self.assertRaisesRegex(ValueError, 'colors.accent'):
            self.load()
        self.assertFalse((self.home / '.config/alacritty/alacritty.toml').exists())

    def test_missing_wallpaper_is_rejected(self):
        (self.directory / 'wallpaper.png').unlink()
        with self.assertRaisesRegex(ValueError, 'missing wallpaper'):
            self.load()

    def test_wallpaper_override_is_per_theme_and_does_not_modify_pack(self):
        chosen = self.home / 'chosen.png'
        chosen.write_bytes(b'chosen')
        overrides = self.root / 'overrides'
        overrides.mkdir()
        (overrides / 'example.json').write_text(json.dumps({'wallpaper': str(chosen)}))
        loaded = self.load()
        self.assertEqual(loaded['wallpaper'], str(chosen))
        self.assertNotIn('wallpaper', json.loads((self.directory / 'theme.json').read_text()))

    def test_override_cannot_replace_palette_or_execute_hooks(self):
        directory = self.root / 'overrides'
        directory.mkdir()
        (directory / 'example.json').write_text('{"colors": {}, "hook": "bad"}')
        with self.assertRaisesRegex(ValueError, 'only wallpaper'):
            self.load()

    def test_unknown_template_token_is_rejected(self):
        self.template.write_text('{{misspelled_color}}')
        with self.assertRaisesRegex(ValueError, 'Unknown template token'):
            switcher.render(self.load())

    def test_partial_write_failure_rolls_back_settings_state_and_cache(self):
        theme = self.load()
        target = self.home / '.config/alacritty/alacritty.toml'
        target.parent.mkdir(parents=True)
        target.write_text('original terminal settings')
        image = self.home / '.cache/betterlockscreen/current/lock_dimblur.png'
        image.parent.mkdir(parents=True)
        image.write_bytes(b'original lock image')
        prepared = self.home / 'prepared'
        prepared.mkdir()
        (prepared / image.name).write_bytes(b'new lock image')
        switcher.STATE.write_text('{"id": "old-theme"}')
        original_state = switcher.STATE.read_bytes()
        override = self.root / 'overrides/example.json'
        def fail_wallpaper(args, **kwargs):
            raise RuntimeError('Simulated wallpaper failure')
        with patch.object(switcher, 'ensure_display'), \
             patch.object(switcher.shutil, 'which', return_value='/fake/bin'), \
             patch.object(switcher, 'lock_cache', return_value=prepared), \
             patch.object(switcher, 'run', side_effect=fail_wallpaper):
            with self.assertRaisesRegex(RuntimeError, 'Simulated'):
                switcher.apply(theme, extra_files={override: '{"wallpaper":"new.png"}'})
        self.assertEqual(target.read_text(), 'original terminal settings')
        self.assertEqual(image.read_bytes(), b'original lock image')
        self.assertEqual(switcher.STATE.read_bytes(), original_state)
        self.assertFalse(switcher.PREVIOUS.exists())
        self.assertFalse(override.exists())

    def test_pinned_wallpaper_survives_source_removal_and_preserves_previous_theme(self):
        import gi
        gi.require_version('GdkPixbuf', '2.0')
        from gi.repository import GdkPixbuf
        source = self.home / 'source.png'
        pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, False, 8, 8, 8)
        pixbuf.fill(0x123456ff)
        pixbuf.savev(str(source), 'png', [], [])
        switcher.STATE.write_text('{"id":"example"}')
        switcher.PREVIOUS.write_text('{"id":"other-theme"}')
        prepared = self.home / 'prepared'
        prepared.mkdir()
        (prepared / 'lock_dimblur.png').write_bytes(b'lock')
        from subprocess import CompletedProcess
        with patch.object(switcher, 'find_asset', return_value=self.directory), \
             patch.object(switcher, 'ensure_display'), \
             patch.object(switcher.shutil, 'which', return_value='/fake/bin'), \
             patch.object(switcher, 'lock_cache', return_value=prepared), \
             patch.object(switcher, 'refresh', return_value=[]), \
             patch.object(switcher, 'run', return_value=CompletedProcess([], 0, '', '')):
            switcher.set_wallpaper(source)
            source.unlink()
            loaded = switcher.load_theme('example')
        self.assertTrue(Path(loaded['wallpaper']).read_bytes().startswith(b'\x89PNG'))
        self.assertEqual(switcher.read_state(switcher.PREVIOUS)['id'], 'other-theme')

    def test_cancel_menu_changes_nothing(self):
        from subprocess import CompletedProcess
        with patch.object(switcher, 'themes', return_value=[self.load()]), \
             patch.object(switcher, 'run', return_value=CompletedProcess([], 1, '', '')):
            self.assertIsNone(switcher.menu())
        self.assertFalse(switcher.STATE.exists())

    def test_all_tokens_render_and_result_is_valid_toml(self):
        rendered = switcher.render(self.load())
        self.assertEqual(len(rendered), 1)
        content = next(iter(rendered.values()))
        self.assertIn('#123456', content)
        self.assertNotIn('{{', content)

    def test_theme_template_overrides_common_template(self):
        override = self.directory / 'templates/.config/alacritty/alacritty.toml.tmpl'
        override.parent.mkdir(parents=True)
        override.write_text('[font]\nsize = 11\n')
        rendered = switcher.render(self.load())
        self.assertEqual(rendered[self.home / '.config/alacritty/alacritty.toml'],
                         '[font]\nsize = 11\n')

    def test_light_theme_renders_gtk_preference(self):
        self.theme['mode'] = 'light'
        self.save_theme()
        self.template.write_text('prefer_dark = {{prefer_dark}}\n')
        content = next(iter(switcher.render(self.load()).values()))
        self.assertEqual(content, 'prefer_dark = false\n')

    def test_invalid_window_geometry_is_rejected(self):
        self.theme['window_gap'] = -1
        self.save_theme()
        with self.assertRaisesRegex(ValueError, 'window_gap'):
            self.load()

    def test_new_json_pack_can_generate_its_own_assets(self):
        builder_spec = importlib.util.spec_from_file_location('builder', Path(__file__).with_name('build_presets.py'))
        builder = importlib.util.module_from_spec(builder_spec)
        builder_spec.loader.exec_module(builder)
        source = self.home / '.local/share/themes/catppuccin-mocha-mauve-standard+default'
        (source / 'gtk-3.0').mkdir(parents=True)
        (source / 'gtk-3.0/gtk.css').write_text('window {background: #1e1e2e; color: rgba(203, 166, 247, 0.5);}')
        with patch.object(builder, 'HOME', self.home), patch.object(builder, 'ROOT', self.root):
            builder.build_custom('example')
        updated = json.loads((self.directory / 'theme.json').read_text())
        self.assertEqual(updated['gtk'], 'Desktop-example')
        self.assertEqual(updated['icons'], 'Desktop-example')
        css = (self.home / '.local/share/themes/Desktop-example/gtk-3.0/gtk.css').read_text()
        self.assertIn('#123456', css)
        self.assertIn('rgba(18, 52, 86, 0.5)', css)
        self.assertTrue((self.directory / 'wallpaper.png').read_bytes().startswith(b'\x89PNG'))


if __name__ == '__main__':
    unittest.main()
