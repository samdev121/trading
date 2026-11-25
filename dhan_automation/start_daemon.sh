#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
  if [[ -x "/opt/homebrew/bin/python3.13" ]]; then
    PYTHON_BIN="/opt/homebrew/bin/python3.13"
  else
    PYTHON_BIN="$(command -v python3)"
  fi
fi

echo "============================================"
echo " IMLT LIVE WS DAEMON — DhanHQ WebSocket"
echo " Run this at 09:00 AM before market opens"
echo "============================================"

cd "$SCRIPT_DIR"
exec "$PYTHON_BIN" "$SCRIPT_DIR/live_ws_daemon.py"
