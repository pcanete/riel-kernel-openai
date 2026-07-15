#!/usr/bin/env sh
set -eu
TARGET=${1:-.}
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python3 "$SCRIPT_DIR/installer.py" --target "$TARGET"
