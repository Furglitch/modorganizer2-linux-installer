#!/usr/bin/env bash

if [ -n "${game_protontricks[*]}" ]; then
	case "$game_launcher" in
	steam)
		log_info "applying protontricks ${game_protontricks[@]}"
		"$utils/protontricks.sh" apply "$game_appid" "arial" "fontsmooth=rgb" "${game_protontricks[@]}"
		;;
	heroic)
		(
			log_info "applying winetricks ${game_protontricks[@]}"
			export WINEPREFIX="$heroic_game_wineprefix"
			if [ "$(basename "$heroic_game_wine")" = proton ]; then
				# Proton is a wrapper - find the actual wine executable for winetricks
				export WINE="$(dirname "$heroic_game_wine")/files/bin/wine"
			else
				# User picked a Wine release, not a Proton release
				export WINE="$heroic_game_wine"

			fi
			export executable_winetricks
			"$utils/winetricks.sh" apply "arial" "fontsmooth=rgb" "${game_protontricks[@]}"
		)
		;;
	esac | "$dialog" loading "Configuring game prefix\nThis may take a while.\n\nFailure at this step may indicate an issue with Winetricks/Protontricks."

	if [ "$?" != "0" ]; then
		"$dialog" errorbox \
			"Error while installing winetricks, check the terminal for more details"
		exit 1
	fi
fi
