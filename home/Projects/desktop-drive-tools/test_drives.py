import importlib.machinery
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

HOME = Path.home()
loader = importlib.machinery.SourceFileLoader('drives', str(HOME / '.local/bin/drive-menu'))
spec = importlib.util.spec_from_loader(loader.name, loader)
drives = importlib.util.module_from_spec(spec)
loader.exec_module(drives)


class DriveTests(unittest.TestCase):
    def test_os_disk_and_all_its_sibling_partitions_are_excluded(self):
        data = {'blockdevices': [{'path': '/dev/sda', 'children': [
            {'path': '/dev/sda1', 'mountpoints': ['/']},
            {'path': '/dev/sda2', 'type': 'part', 'fstype': 'ntfs', 'size': 1234},
        ]}]}
        self.assertEqual(drives.volumes(data), [])

    def test_usb_status_is_inherited_from_parent_disk(self):
        data = {'blockdevices': [{'path': '/dev/sdz', 'tran': 'usb', 'children': [
            {'path': '/dev/sdz1', 'type': 'part', 'fstype': 'exfat', 'size': 1234,
             'mountpoints': [None], 'uuid': 'unique'},
        ]}]}
        result = drives.volumes(data)
        self.assertTrue(result[0]['usb'])
        self.assertEqual(result[0]['disk'], '/dev/sdz')
        self.assertEqual(result[0]['mountpoints'], [])

    def test_changed_device_is_not_operated_on(self):
        volume = {'path': '/dev/sdz1', 'uuid': 'original', 'size': 123}
        changed = dict(volume, uuid='replacement')
        with patch.object(drives, 'volumes', return_value=[changed]):
            with self.assertRaisesRegex(RuntimeError, 'disconnected or changed'):
                drives.recheck(volume)

    def test_cancel_menu_does_not_mount_anything(self):
        v = {'path': '/dev/sdz1', 'name': 'sdz1', 'disk': '/dev/sdz', 'uuid': 'one',
             'size': 1234, 'fstype': 'exfat', 'usb': True, 'mountpoints': []}
        with patch.object(drives, 'volumes', return_value=[v]), \
             patch.object(drives, 'choose', return_value=None), \
             patch.object(drives, 'command') as command:
            drives.menu()
            command.assert_not_called()

    def test_terminal_server_does_not_pass_startup_lock_to_kitty(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            binaries = root / 'bin'
            binaries.mkdir()
            kitty = binaries / 'kitty'
            kitty.write_text('''#!/usr/bin/python3
import os,socket
from pathlib import Path
root=Path(os.environ['XDG_RUNTIME_DIR'])/'desktop-yazi'
(root/'fd-inherited').write_text(str(Path('/proc/self/fd/9').exists()))
sock=socket.socket(socket.AF_UNIX)
sock.bind(str(root/'kitty.sock'))
''')
            kitten = binaries / 'kitten'
            kitten.write_text('#!/bin/sh\nexit 0\n')
            kitty.chmod(0o755)
            kitten.chmod(0o755)
            env = dict(os.environ, XDG_RUNTIME_DIR=str(root),
                       PATH=str(binaries) + ':' + os.environ['PATH'])
            helper = str(HOME / '.local/bin/yazi-terminal-server')
            subprocess.run([helper], env=env, check=True, timeout=3)
            self.assertEqual((root / 'desktop-yazi/fd-inherited').read_text(), 'False')
            subprocess.run([helper], env=env, check=True, timeout=3)


if __name__ == '__main__':
    unittest.main()
