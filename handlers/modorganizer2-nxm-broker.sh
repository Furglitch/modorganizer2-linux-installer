#!/bin/bash

###    PARSE POSITIONAL ARGS    ###
nxm_link=$1; shift

if [ -z "$nxm_link" ]; then
	echo "ERROR: please specify a NXM Link to download"
	exit 1
fi

nexus_game_id=${nxm_link#nxm://}
nexus_game_id=${nexus_game_id%%/*}
###    PARSE POSITIONAL ARGS    ###

instance_link="$HOME/.config/modorganizer2/instances/${nexus_game_id:?}"
instance_dir=$(readlink -f  "$instance_link")
if [ ! -d "$instance_dir" ]; then
	[ -L "$instance_link"] && rm "$instance_link"

	zenity --ok-label=Exit --ellipsize --error --text \
		"Could not download file because there is no Mod Organizer 2 instance for '$nexus_game_id'"
	exit 1
fi

game_appid=$(cat "$instance_dir/appid.txt")

steam -applaunch "$game_appid" "$nxm_link"

