#!/bin/sh
set -e

export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/tmp/xdg-runtime-$(id -u)}"
mkdir -p "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"

if [ -z "${DISPLAY:-}" ]; then
	export DISPLAY=:99
	Xvfb "$DISPLAY" -screen 0 1024x768x24 >/tmp/mo2-lint-xvfb.log 2>&1 &
	XVFB_PID=$!
	trap 'kill "$XVFB_PID" 2>/dev/null || true' EXIT INT TERM
fi

WINEDEBUG=-all \
WINEDLLOVERRIDES="mscoree,mshtml=" \
WINEPREFIX="${HOME}/.local/share/Steam/steamapps/compatdata/22330/pfx" \
wineboot --update >/tmp/mo2-lint-wineboot.log 2>&1 || true
wineserver -w >/dev/null 2>&1 || true

make _build

dist/mo2-lint install oblivion "${HOME}/Games/mo2-lint_oblivion-steam" --launcher steam --unattended -l trace "$@"

dist/mo2-lint install oblivion "${HOME}/Games/mo2-lint_oblivion-epic" --launcher epic --unattended -l trace "$@"

dist/mo2-lint install oblivion "${HOME}/Games/mo2-lint_oblivion-gog" --launcher gog --unattended -l trace "$@"

exec /validate.sh
