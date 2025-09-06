#!/usr/bin/env bash

version="$1"

set -eu

if [ -z "$version" ]; then
	echo "ERROR: specify a version for the release" >&2
	exit 1
fi

script_root=$(realpath "$(dirname "${BASH_SOURCE[0]}")")

release_files=( \
	"gamesinfo" \
	"handlers" \
	"install.sh" \
	"LICENSE" \
	"pluginsinfo.json" \
	"README.md" \
	"steam-redirector/main.exe" \
	"step" \
	"utils" \
	"workarounds" \
)

original_workdir=$PWD
cd "$script_root/steam-redirector" || exit 1
x86_64-w64-mingw32-gcc -v -municode -static -static-libgcc -Bstatic -lpthread -mwindows -o main.exe main.c win32_utils.c

cd "$script_root" || exit 1
tar -czvf "$script_root/mo2installer-$version.tar.gz" "${release_files[@]}"

cd "$original_workdir" || exit 1

