#!/bin/sh
set -eu
[ "$(id -u)" -eq 0 ] || { echo 'This step requires sudo.' >&2; exit 1; }
base=/home/master/.local/share/desktop-rice
test -f /usr/share/xgreeters/slick-greeter.desktop
backup="/etc/lightdm/rice-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup"
cp -a /etc/lightdm/lightdm.conf "$backup/"
for file in /etc/lightdm/slick-greeter.conf /etc/lightdm/lightdm.conf.d/90-desktop-rice.conf; do
    [ ! -f "$file" ] || cp -a "$file" "$backup/"
done
install -d -m 755 /usr/local/share/themes /usr/local/share/icons /usr/local/share/backgrounds /etc/lightdm/lightdm.conf.d
cp -R /home/master/.local/share/themes/catppuccin-mocha-mauve-standard+default /usr/local/share/themes/
cp -R /home/master/.local/share/icons/Bibata-Modern-Ice /usr/local/share/icons/
chmod -R a+rX /usr/local/share/themes/catppuccin-mocha-mauve-standard+default /usr/local/share/icons/Bibata-Modern-Ice
install -m 644 /home/master/Pictures/Wallpapers/purple-horizon.jpg /usr/local/share/backgrounds/purple-horizon.jpg
install -m 644 "$base/slick-greeter.conf" /etc/lightdm/slick-greeter.conf
install -m 644 "$base/90-desktop-rice.conf" /etc/lightdm/lightdm.conf.d/90-desktop-rice.conf
lightdm --show-config > "$backup/effective-config.txt"
echo "Login configuration saved. System backup: $backup"
