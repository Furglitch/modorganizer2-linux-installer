#!/usr/bin/env bash

function log_info() {
	echo "INFO:" "$@" >&2
}

function log_warn() {
	echo "WARN:" "$@" >&2
}

function log_error() {
	echo "ERROR:" "$@" >&2
}

get_wine_variables() {
	local productid="$1"
	local game_config_json="$heroic_config_directory/GamesConfig/$productid.json"
	if [ ! -f "$game_config_json" ]; then
		return 1
	fi

	# Check for a set game-specific Wine version, then fall back to the Wine
	# version set as default.
	if ! heroic_game_wine="$(
		jq --exit-status --raw-output \
			".\"$productid\".wineVersion.bin | select(. != \"\")" \
			"$game_config_json"
	)" && ! heroic_game_wine="$(
		jq --exit-status --raw-output \
			".defaultSettings.wineVersion.bin | select(. != \"\")" \
			"$heroic_config_directory/config.json"
	)"; then
		log_error "wine version is unset for this game"
		return 1
	fi
	log_info "found Heroic WINE at '$heroic_game_wine'"

	if ! heroic_game_wineprefix="$(
		jq --exit-status --raw-output \
			".\"$productid\".winePrefix | select(. != \"\")" \
			"$game_config_json"
	)"; then
		log_error "wine prefix is unset for this game"
		return 1
	fi
	log_info "found Heroic WINEPREFIX at '$heroic_game_wineprefix'"
}

find_gog_game() {
	local gog_installed_json="$heroic_config_directory/gog_store/installed.json"
	if [ -z "$game_gog_productid" ]; then
		log_warn "empty game_gog_productid"
		return 1
	fi

	if [ ! -f "$gog_installed_json" ] || ! game_installation="$(
		jq --exit-status --raw-output \
			".installed[] | select(.appName == \"$game_gog_productid\") | .install_path" \
			"$gog_installed_json"
	)"; then
		log_info "Heroic GOG game not installed"
		return 1
	fi
	log_info "found Heroic GOG installation at '$game_installation'"

	heroic_game_runner=gog
	heroic_game_appname="$game_gog_productid"
	get_wine_variables "$game_gog_productid"
}

find_epic_game() {
	local epic_installed_json="$heroic_config_directory/legendaryConfig/legendary/installed.json"
	if [ -z "$game_epic_productid" ]; then
		log_warn "empty game_epic_productid"
		return 1
	fi

	if [ ! -f "$epic_installed_json" ] || ! game_installation="$(
		jq --exit-status --raw-output \
			".\"$game_epic_productid\".install_path" \
			"$epic_installed_json"
	)"; then
		log_info "Heroic Epic game not installed"
		return 1
	fi
	log_info "found Heroic Epic installation at '$game_installation'"

	heroic_game_runner=legendary
	heroic_game_appname="$game_epic_productid"
	get_wine_variables "$game_epic_productid"
}

declare -A heroic_install_candidates=(
	["$HOME/.config/heroic"]=system
	["$HOME/.var/app/com.heroicgameslauncher.hgl/config/heroic"]=flatpak
)

for heroic_config_directory in "${!heroic_install_candidates[@]}"; do
	heroic_release="${heroic_install_candidates["$heroic_config_directory"]}"
	if [ -d "$heroic_config_directory" ]; then
		log_info "found Heroic in '$heroic_config_directory'"

		if find_gog_game || find_epic_game; then
			echo "${game_installation@A}"
			echo "${heroic_release@A}"
			echo "${heroic_game_runner@A}"
			echo "${heroic_game_appname@A}"
			echo "${heroic_game_wine@A}"
			echo "${heroic_game_wineprefix@A}"
			exit 0
		fi
	fi
done
exit 1
