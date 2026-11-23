# This file contains no clipboard data, only exclusion checks.
password_copy_active() {
    local guard owner deadline now
    now=$(date +%s)
    for guard in "$HOME/.cache/password-clipboard-guard/"*.guard; do
        [ -f "$guard" ] || continue
        read -r owner deadline < "$guard" || return 0
        [[ "$owner" =~ ^[0-9]+$ && "$deadline" =~ ^[0-9]+$ ]] || return 0
        if { [ "$owner" -gt 0 ] && kill -0 "$owner" 2>/dev/null; } || [ "$deadline" -gt "$now" ]; then
            return 0
        fi
        rm -f -- "$guard"
    done
    return 1
}
