#!/usr/bin/env bash

picker_text=$(
	cat <<EOF
Select where you would like to install Mod Organizer 2
EOF
)

screen_text=$(
	cat <<EOF
The selected directory is outside of your /home directory.

This should not cause issues, as long as you make sure Steam has permission to access this folder by setting the STEAM_COMPAT_MOUNTS argument in the game's properties.
More information can be found in the Post-Installation instruction on GitHub.
EOF
)

directory=$(
	case "$game_launcher" in
	steam)
		default_directory="$HOME/Games/mod-organizer-2-${game_nexusid}"
		;;
	heroic)
		# In the Heroic official flatpak, com.heroicgameslauncher.hgl,
		# the launcher is not permitted to read outside the
		# ~/Games/Heroic folder. So, if we don't install here, we will
		# cause the steam-redirector to fail after installation.
		default_directory="$HOME/Games/Heroic/mod-organizer-2-${game_nexusid}"
		;;

	esac
	"$dialog" \
		directorypicker \
		"$picker_text" \
		"$default_directory"
)

if [ -z "$directory" ]; then
	log_error "no install directory selected"
	exit 1
fi

if [[ "$directory" != $HOME/* ]]; then
	button=$(
		"$dialog" \
			infobox \
			"$screen_text"
	)
fi

echo "$directory"
