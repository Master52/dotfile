#!/usr/bin/env bash

set -o pipefail
URL='rtsp://admin:admin@123@{ip}:554/Streaming/Channels/201'
workdir=$(mktemp -d)
video_pipe="$workdir/video.pipe"
grid_pipe="$workdir/grid.pipe"
RCP_TIME_OUT="10000000"
DVR_MAC_ADD="24:0f:9b:2a:28:3e"


cleanup() {

    if [[ -n "${worker_pid:-}" ]]; then
        kill -TERM -- "-$worker_pid" 2>/dev/null
        wait "$worker_pid" 2>/dev/null
    fi

    if [[ -n "${publisher_pid:-}" ]]; then
        kill "$publisher_pid" 2>/dev/null
        wait "$publisher_pid" 2>/dev/null
    fi

    if [[ -n "${layout_pid:-}" ]]; then
	      kill "$layout_pid" 2>/dev/null
	      wait "$layout_pid" 2>/dev/null
    fi


    exec 3>&-

    rm -f -- "$video_pipe" \
        "$workdir/latest.rgb" \
        "$workdir/frame.rgb" \
        "$workdir/placeholder-next.rgb"

    rmdir -- "$workdir"
}


trap cleanup EXIT 

mkfifo "$video_pipe" "$grid_pipe"

ffmpeg -hide_banner -loglevel error -nostdin \
	-f rawvideo -pixel_format rgb24 \
	-video_size 480x270 -framerate 15 \
	-i "$video_pipe" \
	-re -stream_loop -1 \
	-f rawvideo -pixel_format rgb24 \
	-video_size 480x270 -framerate 15 \
	-i "$HOME/camera_placeholder.rgb" \
	-filter_complex \
	  '[0:v][1:v]xstack=inputs=2:layout=0_0|480_0[grid]' \
	-map '[grid]' -an -pix_fmt rgb24 -f rawvideo pipe:1 > "$grid_pipe" &

layout_pid=$!

mpv --no-config \
	--title='Camera grid prototype' \
	--demuxer=rawvideo \
	--demuxer-rawvideo-w=960 \
	--demuxer-rawvideo-h=270 \
	--demuxer-rawvideo-mp-format=rgb24 \
	--demuxer-rawvideo-fps=15 \
	"$grid_pipe" &


player_pid="$!"

exec 3>"$video_pipe"

cp "/home/master/camera_placeholder.rgb" "$workdir/latest.rgb"

publish_frames() {
	while true; do
		if ! cat "$workdir/latest.rgb" >&3; then
			break
		fi
		sleep 0.066667
	done
}

publish_frames &
publisher_pid=$!

show_placeholder() {
	cp -- "$HOME/camera_placeholder.rgb" "$workdir/placeholder-next.rgb" || return 1

	mv -- "$workdir/placeholder-next.rgb" "$workdir/latest.rgb" || return 1

	sleep 3
}


find_dvr_ip() {
#	ip neigh show dev wlo1 | \
#		awk -v mac="$DVR_MAC_ADD" 'tolower($3) == tolower(mac) {print $1; exit}'
	sudo -n arp-scan --interface=wlo1 --localnet | \
		awk -v mac="$DVR_MAC_ADD" '$2 == mac {print $1; exit}'
}


forward_frames() {
	local frame_file="$workdir/frame.rgb"
	local bytes result=0

	while true; do
		if ! dd bs=388800 count=1 iflag=fullblock \
			of="$frame_file" status=none; then
		result=1
		break
		fi

		bytes=$(wc -c <"$frame_file")

		if (( bytes == 0 )); then
			break
		elif (( bytes != 388800 )); then
			printf 'Frame Discarded since incomplelte \n' >&2
			result=1
			break
		fi

		if ! mv -- "$frame_file" "$workdir/latest.rgb" ; then
			result=1
			break
		fi
	done

	rm -f -- "$frame_file"
	return "$result"
	
}

show_camera() {
	local dvr_ip camera_url
	dvr_ip=$(find_dvr_ip)

	if [[ -z "$dvr_ip" ]]; then
		printf 'DVR IP not found for MAC %s\n' "$DVR_MAC_ADD" >&2
		return 1
	fi
	camera_url="${URL/\{ip\}/$dvr_ip}"
	ffmpeg \
		-hide_banner -loglevel error -nostdin \
		-rtsp_transport tcp -timeout "$RCP_TIME_OUT" -i "$camera_url" \
		 -an -vf 'scale=480x270,setsar=1,fps=15' \
		-pix_fmt rgb24 -f rawvideo pipe:1 | forward_frames
}



camera_worker() {
	for i in 1 2 3; do
		show_placeholder

		printf 'Camera Connecting attemp %s\n' "$i" >&2
			if show_camera; then
				printf 'Stream Ended..\n' >&2
			else
				result=$?
				printf 'Camera process failed: exit status %s\n' "$result" >&2
			fi
	done
	show_placeholder
}

export URL workdir DVR_MAC_ADD RCP_TIME_OUT

export -f find_dvr_ip show_placeholder forward_frames
export -f show_camera camera_worker

setsid bash -o pipefail -c 'camera_worker' 3>&- &
worker_pid=$!
wait "$player_pid"



## LIVE VIDEO
#ffmpeg \
#	-hide_banner -loglevel error -nostdin \
#	-rtsp_transport tcp -i "$URL" \
#	-an -vf 'scale=480x270,setsar=1,fps=15' \
#	-pix_fmt rgb24 -f rawvideo pipe:1 | 
#mpv \
#	--no-config  \
#	--title='Camera prototype'e\
#	--demuxer=rawvideo \
#	--demuxer-rawvideo-w=480 \
#	--demuxer-rawvideo-h=270 \
#	--demuxer-rawvideo-fps=15 \
#	--demuxer-rawvideo-mp-format=rgb24 \
#	--demuxer-rawvideo-fps=15 \
#	-
#
#




