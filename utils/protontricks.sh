#!/usr/bin/env bash

function log_error() {
	echo "ERROR: $@" >&2
}

function get_release() {
	if [ -n "$(command -v flatpak)" ]; then
		if flatpak info com.github.Matoking.protontricks &> /dev/null; then
			echo "flatpak"
			return 0
		fi
	fi

	if [ -n "$(command -v protontricks)" ]; then
		echo "system"
		return 0
	fi

	return 1
}

function do_protontricks() {
	release=$(get_release)

	case "$release" in
		flatpak)
			WINETRICKS='' \
			flatpak run 'com.github.Matoking.protontricks' --verbose "$@"
			return $?
		;;
		system)
			protontricks --verbose "$@"
			return $?
		;;
		*)
		log_error "Protontricks unavailable"
		return 1
		;;
	esac
}

function apply() {
	appid=$1; shift
	do_protontricks "$appid" -q --force "$@"
	return $?
}

function get_prefix() {
	local visible=$(do_protontricks -l | grep -o "$1")
	if [ -z "$visible" ]; then
		return 0
	fi

	local stdout=$( \
		do_protontricks -c 'echo $WINEPREFIX' "$1" || true \
	)

	if [ -d "$stdout" ]; then
		echo "$stdout"
	else
		log_error \
			"Protontricks did not find a valid prefix directory. " \
			"Stdout was:\n$stdout"
		return 1
	fi
}

action=$1
shift

case "$action" in
	get-prefix)
		get_prefix "$1"
	;;
	get-release)
		get_release
	;;
	apply)
		apply "$@"
	;;
	*)
		log_error "invalid action '$action'"
		exit 1
	;;
esac

