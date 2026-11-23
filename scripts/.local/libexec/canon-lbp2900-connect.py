#!/usr/bin/python3
"""Request Windows credentials locally; never log passwords."""
import json
import os
import subprocess

p = subprocess.run(['zenity', '--password', '--title=Windows printer login',
    '--text=Enter the Windows account password for ROYAL-FURNITURE\\gc (not the Windows PIN).\nIt will be saved in administrator-only CUPS printer settings.'], capture_output=True)
if p.returncode:
    raise SystemExit('Password dialog cancelled; printer connection was not changed.')
password = p.stdout.rstrip(b'\n').decode()
r, w = os.pipe()
os.write(w, password.encode() + b'\n')
os.close(w)
env = dict(os.environ)
env.pop('PASSWD', None)
env['PASSWD_FD'] = str(r)
try:
    result = subprocess.run(['smbclient', '//ROYAL-FURNITURE/Canon LBP2900',
        '-I', '192.168.29.197', '-U', 'ROYAL-FURNITURE\\gc',
        '--option=client min protocol=SMB2', '-c', 'queue'],
        env=env, pass_fds=(r,), stdin=subprocess.DEVNULL, capture_output=True, timeout=30)
finally:
    os.close(r)
if result.returncode:
    output = (result.stdout + result.stderr).decode(errors='replace')
    statuses = [word for word in output.split() if word.startswith('NT_STATUS_')]
    print('Windows printer login failed:', ', '.join(statuses) or 'connection rejected')
    raise SystemExit(1)
print('Windows printer authentication passed.')
result = subprocess.run(['pkexec', '/usr/bin/python3',
    '/home/master/.local/libexec/canon-lbp2900-admin.py', 'configure'],
    input=json.dumps({'password': password}).encode(), capture_output=True)
print(result.stdout.decode(errors='replace').strip())
if result.returncode:
    print('Local queue configuration failed; no print job sent.')
raise SystemExit(result.returncode)
