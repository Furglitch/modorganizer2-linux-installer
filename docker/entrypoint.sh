#!/bin/sh
set -e

make _build

dist/mo2-lint install oblivion "${HOME}/Games/mo2-lint_oblivion-steam" --launcher steam --unattended -l trace "$@"

dist/mo2-lint install oblivion "${HOME}/Games/mo2-lint_oblivion-epic" --launcher epic --unattended -l trace "$@"

dist/mo2-lint install oblivion "${HOME}/Games/mo2-lint_oblivion-gog" --launcher gog --unattended -l trace "$@"

exec /validate.sh
