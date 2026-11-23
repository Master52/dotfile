#!/usr/bin/python3
"""Install the prebuilt Canon filter and configure this Windows printer queue."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.parse import quote

STAGE = Path('/home/master/.cache/canon-lbp2900-setup')
CAPT = STAGE / 'cndrvcups-capt_2.71-1_amd64/usr'
COMMON = STAGE / 'cndrvcups-common_3.21-1_amd64/usr'
PREFIX = Path('/usr/lib/canon-capt')
QUEUE = 'Canon_LBP2900_Windows'
PPD = Path('/usr/share/cups/model/CNCUPSLBP2900CAPTK.ppd')


def install():
    for directory in (PREFIX / 'bin', PREFIX / 'lib', PPD.parent, Path('/usr/lib/cups/filter')):
        directory.mkdir(parents=True, exist_ok=True)
    for package in (COMMON, CAPT):
        for source in (package / 'lib').glob('*.so*'):
            target = PREFIX / 'lib' / source.name
            if source.is_symlink():
                if target.is_symlink():
                    target.unlink()
                target.symlink_to(os.readlink(source))
            elif source.is_file():
                shutil.copy2(source, target)
        for name in ('caepcm', 'captfilter'):
            source = package / 'share' / name
            if source.is_dir():
                shutil.copytree(source, Path('/usr/share') / name, dirs_exist_ok=True)
    for name in ('captfilter', 'captdrv'):
        target = PREFIX / 'bin' / name
        shutil.copy2(CAPT / 'bin' / name, target)
        target.chmod(0o755)
        wrapper = Path('/usr/bin') / name
        wrapper.write_text('#!/bin/sh\nexport LD_LIBRARY_PATH=/usr/lib/canon-capt/lib\n'
                           f'exec /usr/lib/canon-capt/bin/{name} "$@"\n')
        wrapper.chmod(0o755)
    shutil.copy2(CAPT / 'lib/cups/filter/pstocapt', '/usr/lib/cups/filter/pstocapt')
    Path('/usr/lib/cups/filter/pstocapt').chmod(0o755)
    shutil.copy2(CAPT / 'share/cups/model' / PPD.name, PPD)
    service = Path('/var/service/cupsd')
    if not service.exists():
        service.symlink_to('/etc/sv/cupsd', target_is_directory=True)
    subprocess.run(['sv', 'up', str(service)], check=True)
    print('Canon prebuilt filter installed; CUPS enabled. No print job sent.')


def configure():
    import cups
    credentials = json.load(sys.stdin)
    password = credentials['password']
    authority = quote('gc', safe='') + ':' + quote(password, safe='')
    uri = f'smb://{authority}@ROYAL-FURNITURE/192.168.29.197/Canon%20LBP2900'
    connection = cups.Connection()
    connection.addPrinter(QUEUE, device=uri, filename=str(PPD),
                          info='Canon LBP2900 via Windows', location='ROYAL-FURNITURE (192.168.29.197)')
    connection.addPrinterOptionDefault(QUEUE, 'PageSize', 'A4')
    connection.setPrinterShared(QUEUE, False)
    connection.enablePrinter(QUEUE)
    connection.acceptJobs(QUEUE)
    print('Configured Canon_LBP2900_Windows with A4 paper. No print job sent.')


def repair():
    import cups
    text = Path('/etc/cups/printers.conf').read_text()
    section = text.split('<Printer ' + QUEUE + '>')[-1].split('</Printer>')[0]
    if section == text:
        raise ValueError('Queue section not found')
    uri = next(line.split(' ', 1)[1] for line in section.splitlines() if line.startswith('DeviceURI '))
    old = 'smb://ROYAL-FURNITURE;gc:'
    if not uri.startswith(old):
        raise ValueError('Unexpected URI format')
    credentials, destination = uri[len(old):].rsplit('@', 1)
    new_uri = 'smb://gc:' + credentials + '@ROYAL-FURNITURE/' + destination
    connection = cups.Connection()
    connection.addPrinter(QUEUE, device=new_uri)
    connection.enablePrinter(QUEUE)
    connection.acceptJobs(QUEUE)
    connection.setJobHoldUntil(1, 'no-hold')
    print('Corrected account format and released existing test job.')


if __name__ == '__main__':
    if os.geteuid() != 0:
        raise SystemExit('Run this administrator step through pkexec.')
    try:
        if sys.argv[1:] == ['install']:
            install()
        elif sys.argv[1:] == ['configure']:
            configure()
        elif sys.argv[1:] == ['repair']:
            repair()
        else:
            raise ValueError('Expected install or configure.')
    except Exception as error:
        # Connection settings can contain a password; never echo them on errors.
        print('Canon printer setup failed (' + type(error).__name__ + '). No password was logged.', file=sys.stderr)
        sys.exit(1)
