import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

loader = importlib.machinery.SourceFileLoader('sxiv_tools', str(Path.home() / '.local/bin/sxiv-tools'))
spec = importlib.util.spec_from_loader(loader.name, loader)
tools = importlib.util.module_from_spec(spec)
loader.exec_module(tools)


class ToolTests(unittest.TestCase):
    def test_newest_screenshot_first_with_spaces_and_unicode(self):
        with tempfile.TemporaryDirectory() as temp:
            older, newer = Path(temp) / 'old shot.png', Path(temp) / 'new café.png'
            older.touch()
            newer.touch()
            os.utime(older, (100, 100))
            os.utime(newer, (200, 200))
            self.assertEqual(tools.images([temp], newest=True), [newer, older])

    def test_cancelled_action_menu_has_no_side_effects(self):
        with tempfile.TemporaryDirectory() as temp:
            image = Path(temp) / 'image.png'
            image.touch()
            with patch.object(tools, 'config', return_value={'editor': []}), \
                 patch.object(tools, 'editor_command', return_value=None), \
                 patch.object(tools.subprocess, 'run', return_value=subprocess.CompletedProcess([], 1, '', '')) as run:
                tools.action('a', [str(image)])
            self.assertEqual(run.call_count, 1)

    def test_open_folder_passes_parent_path_as_one_argument(self):
        with tempfile.TemporaryDirectory() as temp:
            image = Path(temp) / 'a picture.png'
            image.touch()
            with patch.object(tools, 'config', return_value={}), patch.object(tools.subprocess, 'run') as run:
                tools.action('o', [str(image)])
            self.assertEqual(run.call_args.args[0][-1], temp)

    def test_copy_converts_to_png_before_invoking_clipboard(self):
        import gi
        gi.require_version('GdkPixbuf', '2.0')
        from gi.repository import GdkPixbuf
        with tempfile.TemporaryDirectory() as temp:
            image = Path(temp) / 'a picture.bmp'
            pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, False, 8, 4, 4)
            pixbuf.fill(0x123456ff)
            pixbuf.savev(str(image), 'bmp', [], [])
            captured = []
            def run(args, **kwargs):
                if args[0] == 'xclip':
                    self.assertIn('image/png', args)
                    captured.append(Path(args[-1]).read_bytes())
                return subprocess.CompletedProcess(args, 0, '', '')
            with patch.object(tools.shutil, 'which', return_value='/fake/xclip'), \
                 patch.object(tools.subprocess, 'run', side_effect=run):
                tools.copy_image(image)
            self.assertTrue(captured[0].startswith(b'\x89PNG'))

    def test_copy_paths_preserves_spaces_unicode_and_multiple_marked_files(self):
        files = [Path('/tmp/a picture.png'), Path('/tmp/café.png')]
        with patch.object(tools.shutil, 'which', return_value='/fake/xclip'), \
             patch.object(tools.subprocess, 'run') as run:
            tools.copy_paths(files)
        command = run.call_args_list[0]
        self.assertIn('UTF8_STRING', command.args[0])
        self.assertEqual(command.kwargs['input'], '/tmp/a picture.png\n/tmp/café.png')


if __name__ == '__main__':
    unittest.main()
