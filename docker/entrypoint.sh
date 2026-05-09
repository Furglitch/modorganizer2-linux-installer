#!/bin/sh
set -e

make _build

exec dist/mo2-lint "$@"
