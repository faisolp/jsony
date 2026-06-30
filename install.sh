#!/usr/bin/env bash
# Install jsony-reader to ~/.claude/scripts/jsony-reader
# Idempotent: safe to re-run. Requires python3 (stdlib only).
set -euo pipefail

DEST="${1:-$HOME/.claude/scripts/jsony-reader}"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$DEST"
cp "$SRC/jsony_core.py" "$DEST/jsony_core.py"
cp "$SRC/jsony-reader" "$DEST/jsony-reader"
chmod +x "$DEST/jsony-reader"

echo "installed jsony-reader -> $DEST/jsony-reader"
"$DEST/jsony-reader" --help >/dev/null && echo "self-check: ok"
