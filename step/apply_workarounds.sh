#!/usr/bin/env bash

if [ -n "$custom_workaround" ]; then
	game_workarounds="$custom_workaround"
else
	game_workarounds="$workarounds/$selected_game.sh"
fi

if [ -f "$game_workarounds" ]; then
	log_info "applying workarounds in '$game_workarounds'"
	source "$game_workarounds"
fi

