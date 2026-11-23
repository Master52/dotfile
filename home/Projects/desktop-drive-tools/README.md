# Desktop drives

Alt+U opens the themed, centered drive menu. It shows filesystem volumes on
non-system disks, including the secondary SATA NTFS volume named New Volume.
Select a volume, then mount/open it in Yazi, mount it, or unmount it.
USB volumes also offer safely removing the whole USB disk, after unmounting its
volumes. Busy filesystems report an error; the script does not force unmounts.
Mount authentication uses the existing XFCE Polkit agent and UDisks2 policy.
NTFS uses the installed kernel's ntfs3 driver when supported by UDisks.

`~/.local/bin/drive-menu --watch` watches block-device events and notifies about
removable drive connections and removals. It starts with desktop-services.
There is no automatic mounting or automatic application launch on connection.
No disk partitioning, formatting, filesystem repair, or fstab editing is done.
The script rechecks the selected volume's path, UUID and size before operations.
The entire disk containing the running OS is excluded from the menu.

The current 465.8 GiB NTFS volume is on SATA; it can be mounted/opened and
unmounted, but the menu does not offer USB power-off for it.

Tests: `python3 -m unittest discover -s ~/Projects/desktop-drive-tools -v`.
These cover OS disk filtering, USB inheritance, replaced devices, menu
cancellation, and the Yazi terminal startup-lock inheritance regression.

## New Volume at startup

Run the archived setup-new-volume-automount script to configure the NTFS volume with
UUID 66CEB2CECEB29631 at /mnt/new-volume through /etc/fstab. This requires sudo.
The helper backs up fstab, verifies it before saving, and uses nofail. Existing
active mounts are preserved until the next boot. The volume uses ntfs3 with
uid=1000,gid=1000,umask=0022,windows_names.
