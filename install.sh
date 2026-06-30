#!/usr/bin/env bash
# Install jsony-reader to ~/.claude/scripts/jsony-reader (or custom DEST).
# Idempotent: safe to re-run. Requires Python 3 (stdlib only).
set -euo pipefail

DEST="${1:-$HOME/.claude/scripts/jsony-reader}"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find python3 or python
PYTHON=
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null && "$cmd" --version 2>&1 | grep -qi "^Python 3"; then
        PYTHON="$cmd"
        break
    fi
done
if [ -z "$PYTHON" ]; then
    echo "error: Python 3 is required but not found on PATH" >&2
    exit 1
fi
echo "[ok] found $PYTHON"

mkdir -p "$DEST"
cp "$SRC/jsony_core.py" "$DEST/jsony_core.py"
cp "$SRC/jsony-reader" "$DEST/jsony-reader"
chmod +x "$DEST/jsony-reader"
echo "[ok] copied jsony_core.py + jsony-reader"

# Copy the .cmd wrapper too (no-op on Unix, but harmless)
if [ -f "$SRC/jsony-reader.cmd" ]; then
    cp "$SRC/jsony-reader.cmd" "$DEST/jsony-reader.cmd"
    echo "[ok] copied jsony-reader.cmd (Windows wrapper)"
fi

echo ""
echo "installed jsony-reader -> $DEST/jsony-reader"
"$PYTHON" "$DEST/jsony-reader" --help >/dev/null && echo "self-check: ok"
