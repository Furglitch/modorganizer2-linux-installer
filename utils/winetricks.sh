#!/usr/bin/env bash

function log_error() {
	echo "ERROR: $@" >&2
}

function get_release() {
	if [ -x "$executable_winetricks" ]; then
		echo "downloaded"
		return 0
	fi

	if [ -n "$(command -v flatpak)" ]; then
		if flatpak info com.github.Matoking.protontricks &>/dev/null; then
			echo "flatpak"
			return 0
		fi
	fi

	if [ -n "$(command -v winetricks)" ]; then
		echo "system"
		return 0
	fi

	return 1
}

function do_winetricks() {
	release=$(get_release)

	case "$release" in
	downloaded)
		"$executable_winetricks" --force "$@"
		return
		;;
	flatpak)
		WINETRICKS='' \
			flatpak run --command=winetricks 'com.github.Matoking.protontricks' --force "$@"
		return
		;;
	system)
		winetricks --force "$@"
		return
		;;
	*)
		log_error "Winetricks unavailable"
		return 1
		;;
	esac
}

action=$1
shift

case "$action" in
get-release)
	get_release
	;;
apply)
	do_winetricks "$@"
	;;
*)
	log_error "invalid action '$action'"
	exit 1
	;;
esac
