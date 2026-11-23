import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

BIN=Path.home()/'.local/bin'
LIB=Path.home()/'.local/libexec'

class ShellToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.home=Path(self.temp.name); self.bin=self.home/'.local/bin';self.bin.mkdir(parents=True)
        self.lib=self.home/'.local/libexec';self.lib.mkdir(parents=True)
        self.log=self.home/'calls.json'
        self.env=dict(os.environ,HOME=str(self.home),PATH=str(self.bin)+':'+os.environ['PATH'],CALL_LOG=str(self.log))
        self.stub('notify-send','import json,os,sys;open(os.environ["CALL_LOG"],"w").write(json.dumps(sys.argv[1:]))')
        self.stub('wpctl','import os;print(os.environ.get("TEST_VOLUME","Volume: 0.65"))')
        (self.lib/'desktop-backlight.sh').write_text('read_backlight() { BACKLIGHT_DEVICE=/sys/class/backlight/intel_backlight; BACKLIGHT_MAX=100; BACKLIGHT_CURRENT=${TEST_BRIGHTNESS:-99}; BACKLIGHT_PERCENT=$BACKLIGHT_CURRENT; }\n')

    def stub(self,name,code):
        p=self.bin/name;p.write_text('#!/usr/bin/python3\n'+code+'\n');p.chmod(0o755)

    def run_tool(self,name,*args,success=True):
        r=subprocess.run([str(BIN/name),*args],env=self.env,capture_output=True,text=True)
        if success:self.assertEqual(r.returncode,0,r.stderr)
        return r

    def test_volume_notification_preserves_percentage(self):
        self.run_tool('desktop-notify','volume');args=json.loads(self.log.read_text())
        self.assertEqual(args[-2:],['Volume','65%']);self.assertIn('int:value:65',args)

    def test_muted_microphone_has_correct_icon_and_progress(self):
        self.env['TEST_VOLUME']='Volume: 0.80 [MUTED]'
        self.run_tool('desktop-notify','mic');args=json.loads(self.log.read_text())
        self.assertEqual(args[-2:],['Microphone','Muted']);self.assertIn('int:value:0',args)
        self.assertIn('microphone-sensitivity-muted',args)

    def test_amplified_volume_only_clamps_progress_bar(self):
        self.env['TEST_VOLUME']='Volume: 1.25'
        self.run_tool('desktop-notify','volume');args=json.loads(self.log.read_text())
        self.assertEqual(args[-1],'125%');self.assertIn('int:value:100',args)

    def test_backlight_discovery_prefers_intel_and_skips_zero_max(self):
        root=self.home/'backlights'
        for name,cur,maximum in [('other',10,100),('intel_backlight',30,100)]:
            d=root/name;d.mkdir(parents=True);(d/'brightness').write_text(str(cur)+'\n');(d/'max_brightness').write_text(str(maximum)+'\n')
        code='source "$1"; read_backlight "$2"; printf "%s %s" "${BACKLIGHT_DEVICE##*/}" "$BACKLIGHT_PERCENT"'
        r=subprocess.check_output(['bash','-c',code,'test',str(LIB/'desktop-backlight.sh'),str(root)],text=True)
        self.assertEqual(r,'intel_backlight 30')
        (root/'intel_backlight/max_brightness').write_text('0\n')
        r=subprocess.check_output(['bash','-c',code,'test',str(LIB/'desktop-backlight.sh'),str(root)],text=True)
        self.assertEqual(r,'other 10')

    def test_brightness_limits_and_local_session_arguments(self):
        self.stub('loginctl','import os,sys;print("7 "+str(os.getuid())+" user seat0" if sys.argv[1]=="list-sessions" else "Active=yes\\nRemote=no")')
        self.stub('busctl','import json,os,sys\nif "GetSession" in sys.argv: print(\'o "/org/freedesktop/login1/session/_37"\')\nelse: open(os.environ["CALL_LOG"],"w").write(json.dumps(sys.argv[1:]))')
        self.stub('desktop-notify','pass')
        self.run_tool('desktop-brightness','up');args=json.loads(self.log.read_text())
        self.assertEqual(args[-3:],['backlight','intel_backlight','100'])
        self.assertIn('/org/freedesktop/login1/session/_37',args)
        self.env['TEST_BRIGHTNESS']='1'
        self.run_tool('desktop-brightness','down');self.assertEqual(json.loads(self.log.read_text())[-1],'1')

    def password_fixture(self):
        store=self.home/'.password-store';(store/'example.com').mkdir(parents=True)
        (store/'.gpg-id').write_text('test-key\n')
        (store/'example.com/user with spaces.gpg').write_text('synthetic encrypted fixture')
        (store/'example.com/symlink.gpg').symlink_to(store/'example.com/user with spaces.gpg')
        self.stub('desktop-menu','import os,sys;sys.stdin.read();print(os.environ["MENU_CHOICE"])')
        self.stub('pass','import json,os,sys;open(os.environ["CALL_LOG"]+".pass","w").write(json.dumps(sys.argv[1:]))')

    def test_password_menu_preserves_spaces_and_uses_guarded_pass(self):
        self.password_fixture();self.env['MENU_CHOICE']='example.com/user with spaces'
        self.run_tool('password-menu')
        args=json.loads(Path(str(self.log)+'.pass').read_text())
        self.assertEqual(args,['show','--clip','example.com/user with spaces'])

    def test_password_menu_rejects_typed_commands_and_symlinks(self):
        self.password_fixture()
        for choice in ['$(touch bad)','example.com/symlink','']:
            self.env['MENU_CHOICE']=choice;self.run_tool('password-menu')
            self.assertFalse(Path(str(self.log)+'.pass').exists())

    def test_dotfile_export_preserves_symlinks_and_excludes_backups(self):
        (self.bin/'link').symlink_to('/a/synthetic/target')
        (self.bin/'old.before-test').write_text('obsolete')
        self.run_tool('save-desktop-dotfiles')
        exported=self.home/'Projects/desktop-dotfiles/.local/bin'
        self.assertEqual(os.readlink(exported/'link'),'/a/synthetic/target')
        self.assertFalse((exported/'old.before-test').exists())

if __name__=='__main__':unittest.main()
