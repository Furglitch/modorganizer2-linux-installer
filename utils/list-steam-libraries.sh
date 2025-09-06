#!/usr/bin/env bash

function log_info() {
	echo "INFO:" "$@" >&2
}

steam_install_candidates=( \
	"$(readlink -f "$HOME/.steam/root")" \
	"$HOME/.var/app/com.valvesoftware.Steam/.local/share/Steam" \
)

for steam_install in "${steam_install_candidates[@]}"; do
	if [ -d "$steam_install" ]; then
		log_info "found Steam in '$steam_install'"

		if [ -d "$steam_install/steamapps" ]; then
			main_library="$steam_install"
		else
			main_library="$steam_install/steam"
		fi

		grep -oE '/[^"]+' "$main_library/steamapps/libraryfolders.vdf"
		exit 0
	else
		log_info "steam not found in '$steam_install'"
	fi
done

