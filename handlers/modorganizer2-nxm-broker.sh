#!/usr/bin/env bash

###    PARSE POSITIONAL ARGS    ###
nxm_link=$1
shift

if [ -z "$nxm_link" ]; then
	echo "ERROR: please specify a NXM Link to download"
	exit 1
fi

nexus_game_id=${nxm_link#nxm://}
nexus_game_id=${nexus_game_id%%/*}
###    PARSE POSITIONAL ARGS    ###

instance_link="$HOME/.config/modorganizer2/instances/${nexus_game_id:?}"
instance_dir=$(readlink -f "$instance_link")
if [ ! -d "$instance_dir" ]; then
	[ -L "$instance_link" ] && rm "$instance_link"

	zenity --ok-label=Exit --error --text \
		"Could not download file because there is no Mod Organizer 2 instance for '$nexus_game_id'"
	exit 1
fi

instance_dir_windowspath="Z:$(sed 's/\//\\\\/g' <<<"$instance_dir")"
pgrep -f "$instance_dir_windowspath\\\\modorganizer2\\\\ModOrganizer.exe"
process_search_status=$?

if [ -r "$instance_dir/variables.sh" ]; then
	source "$instance_dir/variables.sh"

	case "$game_launcher" in
	steam) : ;;
	heroic)
		# The user may have changed their Wine/Proton selection for this
		# game at some time after installing MO2, and we don't have
		# protontricks to look it up for us. Therefore, we need to look
		# up the latest values ourselves.
		source <(
			export game_gog_productid game_epic_productid
			"$(realpath "$(dirname "${BASH_SOURCE[0]}")")/find-heroic-game-installation.sh"
		)
		export WINEPREFIX="$heroic_game_wineprefix"
		if [ "$(basename "$heroic_game_wine")" = proton ]; then
			# Proton is a wrapper - find the actual wine executable
			export WINE="$(dirname "$heroic_game_wine")/files/bin/wine"
		else
			# User picked a Wine release, not a Proton release
			export WINE="$heroic_game_wine"

		fi
		;;
	esac

elif [ -r "$instance_dir/appid.txt" ]; then
	# Backwards compatibility for older instances.
	#
	# These have a one-line text file "appid.txt" which contain only the
	# Steam appid of the game.
	#
	# These instances are always Steam games, as they predate support for
	# other launchers.
	game_appid=$(cat "$instance_dir/appid.txt")
	game_launcher=steam
fi

if [ "$process_search_status" == "0" ]; then
	echo "INFO: sending download '$nxm_link' to running Mod Organizer 2 instance"
	case "$game_launcher" in
	steam)
		download_start_output=$(WINEESYNC=1 WINEFSYNC=1 protontricks-launch --appid "$game_appid" "$instance_dir/modorganizer2/nxmhandler.exe" "$nxm_link")
		;;
	heroic)
		case "$heroic_release" in
		system)
			download_start_output=$(WINEESYNC=1 WINEFSYNC=1 "$WINE" "$instance_dir/modorganizer2/nxmhandler.exe" "$nxm_link")
			;;
		flatpak)
			download_start_output=$(WINEESYNC=1 WINEFSYNC=1 flatpak run --command="$WINE" com.heroicgameslauncher.hgl "$instance_dir/modorganizer2/nxmhandler.exe" "$nxm_link")
			;;
		esac
		;;
	esac
	download_start_status=$?
else
	echo "INFO: starting Mod Organizer 2 to download '$nxm_link'"
	case "$game_launcher" in
	steam)
		download_start_output=$(steam -applaunch "$game_appid" "$nxm_link")
		;;
	heroic)
		heroic_launch_url="heroic://launch?appName=$(
			echo "$heroic_game_appname" | jq --raw-input --raw-output @uri
		)&runner=$(
			echo "$heroic_game_runner" | jq --raw-input --raw-output @uri
		)&arg=$(
			echo "$nxm_link" | jq --raw-input --raw-output @uri
		)"
		echo "INFO: launching heroic with protocol url '$heroic_launch_url'"
		download_start_output=$(
			xdg-open "$heroic_launch_url"
		)
		;;
	esac
	download_start_status=$?
fi

if [ "$download_start_status" != "0" ]; then
	zenity --ok-label=Exit --error --text \
		"Failed to start download:\n\n$download_start_output"
	exit 1
fi
