#!/usr/bin/env bash

if [ -z "$custom_game" ]; then
	load_gameinfo="$gamesinfo/$selected_game.sh"
else
	load_gameinfo="$custom_game"
fi

if [ ! -f "$load_gameinfo" ]; then
	log_error "no gameinfo for '$selected_game'"
	"$dialog" errorbox \
		"Could not find information on '$selected_game'"
	exit 1
fi

source "$load_gameinfo"

if [ -z "$game_appid" ]; then
	log_error "empty game_appid"
	exit 1
elif [ -z "$game_steam_subdirectory" ]; then
	log_error "empty steam_subdirectory"
	exit 1
fi

steam_library=$("$utils/find-library-for-file.sh" "$game_steam_subdirectory/$game_executable")

if [ ! -d "$steam_library" ]; then
	if { [ "$game_appid" -eq 22300 ] || [ "$game_appid" -eq 22370 ]; } && [ -f "$steam_library/$game_steam_subdirectory/Fallout3Launcher.exe" ]; then
		log_error "Fallout 3 and Fallout 3 GOTY require the game version to be downgraded. Instructions have been provided in the workarounds folder."
		"$dialog" errorbox \
			"Fallout 3 and Fallout 3 GOTY require the game version to be downgraded. Instructions have been provided in the workarounds folder."
	fi 
	log_error "could not find any Steam library containing a game with appid '$game_appid'. If you know exactly where the library is, you can specify it using the environment variable STEAM_LIBRARY"
	"$dialog" errorbox \
		"Could not find '$game_steam_subdirectory' in any of your Steam libraries\nMake sure the game is installed and that you've run it at least once"
	exit 1
	
fi

if [ -n "$game_scriptextender_url" ] || { [ -n "$game_scriptextender_modid" ] && [ -n "$game_scriptextender_fileid" ]; }; then
	hasScriptExtender=true
	if [ -z "$game_scriptextender_url" ] && { [ -n "$game_scriptextender_modid" ] || [ -n "$game_scriptextender_fileid" ]; }; then
		nexus_scriptextender=true
	fi
else
	hasScriptExtender=false
fi
echo $nexus_scriptextender

game_installation="$steam_library/steamapps/common/$game_steam_subdirectory"

# defer loading these variables to step/clean_game_prefix.sh
game_prefix=''
game_compatdata=''

