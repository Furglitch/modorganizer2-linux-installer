#!/bin/sh
set -e

make _build

dist/mo2-lint install oblivion "${HOME}/Games/mo2-lint_oblivion-steam" --launcher steam --unattended -l trace "$@"

exec /validate.sh
