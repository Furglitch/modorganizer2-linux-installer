#!/usr/bin/env bash

# For testing bugfixes and features locally before releasing.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RELEASE_VERSION="TEST"
ARCHIVE_NAME="mo2installer-${RELEASE_VERSION}.tar.gz"
DEST_DIR="$HOME/Downloads/mo2-test"

# Run the pack-release script
"$SCRIPT_DIR/pack-release.sh" "$RELEASE_VERSION"

# Create destination directory
mkdir -p "$DEST_DIR"

# Extract the resulting archive to the destination directory
if [ -f "$SCRIPT_DIR/$ARCHIVE_NAME" ]; then
	tar -xzvf "$SCRIPT_DIR/$ARCHIVE_NAME" -C "$DEST_DIR"
	echo "Extraction complete to $DEST_DIR."
else
	echo "ERROR: Archive $ARCHIVE_NAME not found!" >&2
	exit 1
fi