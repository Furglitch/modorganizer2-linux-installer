#!/usr/bin/env bash

picker_text=$( \
cat << EOF
Select where you would like to install Mod Organizer 2
EOF
)

screen_text=$( \
cat << EOF
The selected directory is outside of your /home directory.

This should not cause issues, as long as you make sure Steam has permission to access this folder by setting the STEAM_COMPAT_MOUNTS argument in the game's properties.
More information can be found in the Post-Installation instruction on GitHub.
EOF
)

directory=$( \
	"$dialog" \
		directorypicker \
		"$picker_text" \
		"$HOME/Games/mod-organizer-2-${game_nexusid}" \
)

if [ -z "$directory" ]; then
	log_error "no install directory selected"
	exit 1
fi

if [[ "$directory" != $HOME/* ]]; then
	button=$( \
		"$dialog" \
		infobox \
		"$screen_text"
	)
fi

echo "$directory"

