# Shared, read-only backlight discovery for desktop status and controls.
read_backlight() {
    local root=${1:-/sys/class/backlight} device
    local -a devices=()
    [[ ! -d "$root/intel_backlight" ]] || devices+=("$root/intel_backlight")
    for device in "$root"/*; do
        [[ "$device" == "$root/intel_backlight" ]] || devices+=("$device")
    done
    for device in "${devices[@]}"; do
        [[ -r "$device/brightness" && -r "$device/max_brightness" ]] || continue
        IFS= read -r BACKLIGHT_CURRENT < "$device/brightness" || continue
        IFS= read -r BACKLIGHT_MAX < "$device/max_brightness" || continue
        [[ "$BACKLIGHT_CURRENT" =~ ^[0-9]+$ && "$BACKLIGHT_MAX" =~ ^[0-9]+$ ]] || continue
        (( BACKLIGHT_MAX > 0 )) || continue
        BACKLIGHT_DEVICE=$device
        BACKLIGHT_PERCENT=$(( (BACKLIGHT_CURRENT * 100 + BACKLIGHT_MAX / 2) / BACKLIGHT_MAX ))
        return 0
    done
    return 1
}
