#!/usr/bin/env bash
# One Bash controller; FFmpeg decodes and composes, mpv displays.
set -o pipefail
umask 077

# Camera settings live here, not in camera.md. Keep this file private.
RTSP_TEMPLATE='rtsp://admin:admin@123@{ip}:554/Streaming/Channels/{channel}'
CHANNELS=(101 201 301 401 501 601 701 801 901 1001 1101)
declare -A CAMERA_NAMES=(
    [101]='Shop Enternce Right'
    [201]='Shop Enterence Left'
    [301]='Shop Counter Back'
    [401]='Shop Middle'
    [501]='Back side'
    [601]='Center to Back Facing'
    [701]=Fabrication
    [801]='Home Entery View'
    [901]='Storage View'
    [1001]='2nd Floor Entery View'
    [1101]='Amazon packing'
)
INTERFACE=wlo1
DVR_MAC=24:0f:9b:2a:28:3e
WIDTH=480
HEIGHT=270
FPS=15
READ_TIMEOUT=10000000
STALL_TIMEOUT=30
INTEL_DEVICE=/dev/dri/by-path/pci-0000:00:02.0-render
FONT=/usr/share/fonts/TTF/DejaVuSans.ttf
SELF=$(readlink -f -- "${BASH_SOURCE[0]}")

error() { printf 'Camera Viewer: %s\n' "$*" >&2; }

# Discover once at startup. All workers keep this address until the viewer exits.
discover() {
    local ip
    ip=$(sudo -n /usr/bin/arp-scan --interface="$INTERFACE" --localnet |
        awk -v mac="$DVR_MAC" 'tolower($2)==tolower(mac) {found=$1} END {if(found) print found}') || return 1
    [[ -n "$ip" ]] || return 1
    printf '%s\n' "$ip"
}

placeholder() {
    cp -- "$1/offline.rgb" "$1/placeholder-next.rgb" &&
        mv -- "$1/placeholder-next.rgb" "$1/latest.rgb"
}

# Each decoder replaces the cached picture only after a whole frame is written.
# No binary data is stored in shell variables and no per-frame shell loop is needed.
feed() {
    local dir=$1 channel=$2 ip=$3 url escaped decoder='' delay=2
    local started now modified rc mode=hardware transform
    local -a acceleration=()
    [[ -r $INTEL_DEVICE && -w $INTEL_DEVICE ]] || mode=software
    trap '[[ -n "$decoder" ]] && kill "$decoder" 2>/dev/null; exit 0' TERM INT HUP
    url=${RTSP_TEMPLATE/\{ip\}/$ip}
    url=${url/\{channel\}/$channel}
    # FFconcat keeps credentials out of process command arguments.
    escaped=${url//\'/\'\\\'\'}
    printf "ffconcat version 1.0\nfile '%s'\noption rtsp_transport tcp\noption timeout %s\n" \
        "$escaped" "$READ_TIMEOUT" > "$dir/source.ffconcat"
    while true; do
        placeholder "$dir" || return 1
        acceleration=()
        if [[ $mode == hardware ]]; then
            acceleration=(-hwaccel vaapi -hwaccel_device "$INTEL_DEVICE" -hwaccel_output_format vaapi)
            transform="scale_vaapi=w=$WIDTH:h=$HEIGHT:format=nv12,hwdownload,format=nv12"
        else
            transform="scale=$WIDTH:$HEIGHT"
        fi
        started=$(date +%s)
        # i965 supports decoding and GPU resizing on this laptop's Intel UHD 620.
        LIBVA_DRIVER_NAME=i965 ffmpeg -y -hide_banner -loglevel error -nostdin -threads 2 \
            "${acceleration[@]}" \
            -protocol_whitelist file,rtsp,tcp,udp,rtp,crypto \
            -f concat -safe 0 -i "$dir/source.ffconcat" \
            -map 0:v:0 -an -sn -dn -filter_threads 1 \
            -vf "$transform,setsar=1,fps=$FPS,drawtext=fontfile=$FONT:textfile=$dir/name.txt:expansion=none:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6:x=8:y=8" \
            -threads 1 -c:v rawvideo -pix_fmt rgb24 -f image2 \
            -update 1 -atomic_writing 1 "$dir/latest.rgb" \
            > /dev/null 2> "$dir/decoder-error.log" &
        decoder=$!
        while kill -0 "$decoder" 2>/dev/null; do
            sleep 1
            now=$(date +%s)
            modified=$(stat -c %Y "$dir/latest.rgb") || modified=$started
            if (( now - modified >= STALL_TIMEOUT )); then
                kill -TERM "$decoder" 2>/dev/null
                sleep 1
                kill -KILL "$decoder" 2>/dev/null
                break
            fi
        done
        rc=0
        wait "$decoder" 2>/dev/null || rc=$?
        decoder=''
        placeholder "$dir" || return 1
        # GPU/codec incompatibility falls back immediately for this feed only.
        # Network/authentication errors retain hardware mode and use normal retries.
        if [[ $mode == hardware ]] && (( rc != 0 )) &&
            grep -Eiq 'Failed to initialise VAAPI|No VA display found|Device creation failed|No device available for decoder|Failed setup for format vaapi|vaInitialize failed|Failed to create a VAAPI|vaCreateConfig failed|Failed to create processing pipeline|Failed to configure output pad on Parsed_scale_vaapi|Hardware does not support|Device setup failed|No usable decoding device' "$dir/decoder-error.log"; then
            mode=software
            continue
        fi
        now=$(date +%s)
        (( now - started >= 60 )) && delay=2
        sleep "$delay"
        (( delay < 30 )) && delay=$((delay * 2 > 30 ? 30 : delay * 2))
    done
}

# Image2 reopens the latest cached image on every iteration. Each input therefore
# keeps advancing even while its decoder is offline or being restarted.
layout() {
    local session=$1 count=$2 columns=$3 i x y filter='' labels='' positions=''
    local -a inputs=()
    for ((i=0; i<count; i++)); do
        inputs+=(-thread_queue_size 2 -re -analyzeduration 0 -probesize 32 \
            -fpsprobesize 0 -f image2 -pattern_type none -loop 1 \
            -framerate "$FPS" -video_size "${WIDTH}x${HEIGHT}" \
            -pixel_format rgb24 -c:v rawvideo -i "$session/feed-$i/latest.rgb")
        labels+="[$i:v]"
        x=$((i % columns * WIDTH)); y=$((i / columns * HEIGHT))
        [[ -n "$positions" ]] && positions+='|'
        positions+="${x}_${y}"
    done
    if (( count == 1 )); then
        filter='[0:v]null[grid]'
    else
        filter="${labels}xstack=inputs=$count:layout=$positions:fill=black[grid]"
    fi
    exec ffmpeg -hide_banner -loglevel error -nostdin \
        "${inputs[@]}" -filter_complex_threads 1 -filter_complex "$filter" \
        -map '[grid]' -an -threads 1 -c:v rawvideo -pix_fmt rgb24 \
        -f rawvideo pipe:1 > "$session/grid.pipe" 2> "$session/layout-error.log"
}

main() {
    local list=0 all=0 arg ch label selection dvr_ip
    local session='' layout_pid='' player_pid='' columns=1 rows count i stream
    local -a selected=() groups=()
    local -A seen=() label_channel=()
    while (($#)); do
        arg=$1; shift
        case "$arg" in
            --all|'All Camera'|Default) all=1 ;;
            --watch) (($#)) || { error '--watch needs a channel'; return 2; } ;;
            --list) list=1 ;;
            --help|-h)
                printf '%s\n' 'camera-viewer [CHANNEL ... | --all]' \
                    'No arguments: camera menu; multiple selections share one grid.' \
                    'camera-viewer --list'
                return ;;
            *)
                [[ -v CAMERA_NAMES[$arg] ]] || { error "Unknown channel: $arg"; return 2; }
                if [[ ! -v seen[$arg] ]]; then selected+=("$arg"); seen[$arg]=1; fi ;;
        esac
    done
    if (( list )); then
        for ch in "${CHANNELS[@]}"; do printf '%s: %s\n' "$ch" "${CAMERA_NAMES[$ch]}"; done
        return
    fi
    if ((all)); then selected=("${CHANNELS[@]}"); fi
    if ((${#selected[@]} == 0)); then
        for ch in "${CHANNELS[@]}"; do label_channel["${CAMERA_NAMES[$ch]} [$ch]"]=$ch; done
        selection=$({
            printf 'All Camera\n'
            for ch in "${CHANNELS[@]}"; do printf '%s [%s]\n' "${CAMERA_NAMES[$ch]}" "$ch"; done
        } | "$HOME/.local/bin/desktop-menu" -p 'Cameras: Ctrl+Enter add | Enter open') || return 0
        while IFS= read -r label; do
            [[ -n $label ]] || continue
            if [[ $label == 'All Camera' ]]; then selected=("${CHANNELS[@]}"); break; fi
            [[ -v label_channel[$label] ]] || continue
            ch=${label_channel[$label]}
            if [[ ! -v seen[$ch] ]]; then selected+=("$ch"); seen[$ch]=1; fi
        done <<< "$selection"
        ((${#selected[@]})) || return 0
    fi
    for arg in ffmpeg mpv setsid stat sudo awk; do
        command -v "$arg" >/dev/null || { error "Missing command: $arg"; return 1; }
    done
    [[ -r $FONT ]] || { error "Font missing: $FONT"; return 1; }
    if ! dvr_ip=$(discover); then
        error 'DVR discovery failed. Check the network and password-free arp-scan permission, then restart.'
        return 1
    fi
    # Runtime directories are usually tmpfs: frame caches stay off persistent storage.
    session=$(mktemp -d "${XDG_RUNTIME_DIR:-/tmp}/camera-bash.XXXXXXXX") || return 1

    cleanup() {
        trap '' INT TERM HUP
        local pid
        for pid in "${groups[@]}"; do kill -TERM -- "-$pid" 2>/dev/null; done
        [[ -n $player_pid ]] && kill -TERM "$player_pid" 2>/dev/null
        sleep 0.2
        for pid in "${groups[@]}"; do kill -KILL -- "-$pid" 2>/dev/null; done
        [[ -n $player_pid ]] && kill -KILL "$player_pid" 2>/dev/null
        for pid in "${groups[@]}"; do wait "$pid" 2>/dev/null; done
        [[ -n $player_pid ]] && wait "$player_pid" 2>/dev/null
        # session is exclusively created by mktemp above and contains only our files.
        rm -rf -- "$session"
    }
    trap cleanup EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM HUP
    count=${#selected[@]}
    while (( columns * columns < count )); do ((columns++)); done
    rows=$(((count + columns - 1) / columns))
    for ((i=0; i<count; i++)); do
        ch=${selected[$i]}
        mkdir "$session/feed-$i" || exit 1
        printf '%s' "${CAMERA_NAMES[$ch]}" > "$session/feed-$i/name.txt"
        ffmpeg -y -hide_banner -loglevel error -nostdin -f lavfi \
            -i "color=c=0x202331:s=${WIDTH}x${HEIGHT}:r=$FPS" \
            -vf "drawtext=fontfile=$FONT:textfile=$session/feed-$i/name.txt:expansion=none:fontsize=20:fontcolor=white:x=(w-text_w)/2:y=h/2-35,drawtext=fontfile=$FONT:text='Connecting...':fontsize=24:fontcolor=white:x=(w-text_w)/2:y=h/2+5" \
            -frames:v 1 -threads 1 -c:v rawvideo -pix_fmt rgb24 -f rawvideo \
            "$session/feed-$i/offline.rgb" || exit 1
        placeholder "$session/feed-$i" || exit 1
    done
    mkfifo "$session/grid.pipe" || exit 1
    setsid "$SELF" --internal-layout "$session" "$count" "$columns" &
    layout_pid=$!; groups+=("$layout_pid")
    mpv --no-config --no-terminal --msg-level=all=error \
        --title="Cameras ($count)" --no-audio --cache=no --cache-pause=no \
        --demuxer=rawvideo --demuxer-rawvideo-w="$((WIDTH * columns))" \
        --demuxer-rawvideo-h="$((HEIGHT * rows))" \
        --demuxer-rawvideo-mp-format=rgb24 --demuxer-rawvideo-fps="$FPS" \
        --demuxer-max-bytes=8MiB --demuxer-readahead-secs=0 \
        --no-resume-playback --no-save-position-on-quit \
        "$session/grid.pipe" \
        > /dev/null 2> "$session/player-error.log" &
    player_pid=$!
    for ((i=0; i<count; i++)); do
        stream=${selected[$i]}
        # Hikvision substreams reduce decode load for multi-camera layouts.
        if (( count > 1 )) && [[ $stream == *01 ]]; then stream=${stream%01}02; fi
        setsid "$SELF" --internal-feed "$session/feed-$i" "$stream" "$dvr_ip" \
            > /dev/null 2> "$session/feed-$i/worker-error.log" &
        groups+=("$!")
        sleep 0.15
    done
    printf 'Viewing %s camera(s). Close mpv or press q to stop.\n' "$count"
    # Observe both compositor and player so a failed layout cannot leave a window hanging.
    local finished='' result=0
    if wait -n -p finished "$player_pid" "$layout_pid"; then result=0; else result=$?; fi
    if [[ $finished == "$layout_pid" ]]; then
        # Closing mpv also makes FFmpeg see a broken output pipe. Either child
        # may be reported first; this is a normal shutdown, not a layout failure.
        sleep 0.1
        if ! kill -0 "$player_pid" 2>/dev/null; then
            if wait "$player_pid"; then result=0; else result=$?; fi
            if (( result == 0 || result == 143 )); then exit 0; fi
        fi
        error 'Video layout ended; closing viewer.'
        tail -n 5 "$session/layout-error.log" >&2
        tail -n 5 "$session/player-error.log" >&2
        exit 1
    fi
    if (( result != 0 && result != 143 )) && [[ -s "$session/player-error.log" ]]; then
        tail -n 5 "$session/player-error.log" >&2
    fi
    # Execute EXIT cleanup while main's local process IDs are still in scope.
    exit 0
}

case ${1:-} in
    --internal-feed) shift; feed "$@" ;;
    --internal-layout) shift; layout "$@" ;;
    *) main "$@" ;;
esac
