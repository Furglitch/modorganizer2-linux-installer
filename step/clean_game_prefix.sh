#!/usr/bin/env bash

confirm_cleaning_text=$(
	cat <<EOF
It is highly recommended to clean your current game prefix before starting the installation process.

Would you like to archive your current game prefix and create a new one?
EOF
)

create_clean_prefix_text=$(
	case "$game_launcher" in
	steam)
		cat <<EOF
Now you need to create a clean prefix:

1. On Steam: right click the game > Properties > Compatibility
2. Check the option "Force the use of a specific Steam Play compatibility tool"
3. Select the Proton version you would like to use
	* Proton 9.0 is the currently supported and recommended version
4. Launch the game and wait for Steam to finish its setup
5. Close the game. It must remain stopped through the entire install process
EOF
		;;
	heroic)
		cat <<EOF
Now you need to create a clean prefix:

1. On Heroic: right click the game > Settings > WINE
2. Under Wine Version, select the version you would like to use
	* Proton - Proton 9.0 (Beta) is the currently supported and recommended version
	* Note: this version is *not* in beta: it's stable, but Valve never changed the folder name after its release
	* If this version is not in the list, do the following:
		- Close the game settings
		- From the left sidebar, go to Settings > Advanced
		- Check "Allow using Valve Proton builds to run games"
		- Make sure Proton 9.0 is installed in Steam
		- Return to game settings
3. Optional: navigate to the OTHER tab and check "Use Steam Runtime". This is recommended and supported.
4. Launch the game and wait for Heroic to finish its setup
5. Close the game. It must remain stopped through the entire install process
EOF
		;;
	esac
)

function archive_existing_prefix() {
	game_compatdata_archive="$game_compatdata.$(date +%Y%m%d%H%M%S)"
	if [ -e "$game_compatdata_archive" ]; then
		log_error "cannot archive prefix, '$game_compatdata_archive' already exists"
		return 1
	fi
	log_info "moving '$game_compatdata' to '$game_compatdata_archive'"
	mv "$game_compatdata" "$game_compatdata_archive"
	echo "[$(date --iso-8601=minutes)] '$selected_game' prefix archived in '$game_compatdata_archive'" >>"$shared/archived_prefixes.log"
}

function restore_archived_userdata() {
	local src
	case "$game_launcher" in
	steam)
		src="$game_compatdata_archive/pfx/drive_c/users"
		;;
	heroic)
		src="$game_compatdata_archive/drive_c/users"
		;;

	esac
	local dst="$game_prefix/drive_c/users"

	log_info "achiving '$dst' to '$dst.bak'"
	mv "$dst" "$dst.bak"

	log_info "moving '$src' to '$dst'"
	mv "$src" "$dst"
}

function create_new_prefix() {
	confirmation=$(
		"$dialog" \
			radio \
			425 "$create_clean_prefix_text" \
			"1" "Cancel the installation" \
			"0" "All done. Let's continue"
	)

	echo "$confirmation"
}

function load_prefix_locations() {
	case "$game_launcher" in
	steam)
		game_prefix=$("$utils/protontricks.sh" get-prefix "$game_appid")
		if [ -n "$game_prefix" ]; then
			game_compatdata=$(dirname "$game_prefix")
		fi
		;;
	heroic)
		# The game's prefix might be set in configuration but not yet exist,
		# in particular if the game has been installed but never launched.
		# Only set the game_prefix variable if the prefix exists.
		if [ -d "$heroic_game_wineprefix" ]; then
			game_prefix="$heroic_game_wineprefix"
		fi
		if [ -n "$game_prefix" ]; then
			# The prefix folder is the very one we want to rename,
			# not its parent as with Steam games.
			game_compatdata="$game_prefix"
		fi
		;;
	esac
}

game_compatdata_archive=''
load_prefix_locations
if [ -n "$game_prefix" ]; then
	confirm_cleaning=$("$dialog" question "$confirm_cleaning_text")
	if [ "$confirm_cleaning" == "0" ]; then
		archive_existing_prefix
	else
		log_info "proceeding with existing prefix"
	fi
fi

confirm_new_prefix=$(create_new_prefix)
if [ "$confirm_new_prefix" != "0" ]; then
	log_error "installation cancelled by the user"
	exit 1
fi
log_info "user confirmed prefix setup"

load_prefix_locations
if [ -z "$game_prefix" ]; then
	log_error "no prefix found"
	"$dialog" \
		errorbox \
		"A prefix for the selected game could not be found.\nMake sure you have followed the instructions on creating a clean prefix.\nCheck the terminal output for more details."
	exit 1
fi

if [ -n "$game_compatdata_archive" ]; then
	restore_archived_userdata

	archive_information_text=$(
		cat <<EOF
Your old prefix has been archived at:
$game_compatdata_archive

Your personal data has been automatically moved to your new prefix.
You're free to delete the old archive after confirming your
mod lists and save files are intact.

A list of all archived prefixes is available at:
$shared/archived_prefixes.log
EOF
	)

	"$dialog" infobox "$archive_information_text"
fi
