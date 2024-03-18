#! /bin/zsh

set_touchpad_scroll() {

    local touch_pad_id=$(xinput --list-props 14 | \
                            grep -E "libinput Tapping Enabled \(" | \
                            grep -oP '\(\K\d+(?=\))')
    local scroll_id=$(xinput --list-props 14 | \
                            grep -E "libinput Natural Scrolling Enabled \(" | \
                            grep -oP '\(\K\d+(?=\))')

    echo "Setting Touchpad id" "$touch_pad_id"
    xinput --set-prop 14 "$touch_pad_id" 1
    echo "Setting  Naturl Scroll" "$scroll_id"
    xinput --set-prop 14 "$scroll_id" 1
}

function main() {
    echo "Sxhkd..."
    sxhkd &

    echo "Enabling nm-applet..."
    nm-applet &
    echo "Enabling clipmenud..."
    clipmenud &
    echo "Setting touchpad setting..."
    set_touchpad_scroll
    echo "Setting setting last Background..."
    feh --bg-scale ~/.bg
    echo "Setting Composite Panel..."
    picom -b
    echo "Writing dwmblocks..."
    dwmblocks &
    echo "Opening Tilda..."
    tilda &
    #echo "Starting auto_affiliate bot"
    #/home/master/scripts/autobot_affiliate.sh && notify-send " 󱜙 Bot has Started"

    echo "Setting up flags..."
    echo "0" > /tmp/low_charge_flag

}


main > log.txt
