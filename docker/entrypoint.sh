#!/bin/sh
set -e

make _build

exec dist/mo2-lint install oblivion "${HOME}/Games/mo2-lint_oblivion-steam" --launcher steam --unattended -l trace "$@"
