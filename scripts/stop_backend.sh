#!/usr/bin/env bash
# Stop backend
# Usage: ./scripts/stop_backend.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_FILE="${PROJECT_ROOT}/.backend.pid"

if [ ! -f "$PID_FILE" ]; then
  echo "Backend not running (no PID file)"
  exit 0
fi

PID=$(cat "$PID_FILE")
if kill -0 "$PID" 2>/dev/null; then
  kill "$PID" 2>/dev/null || true
  echo "Backend stopped (PID $PID)"
else
  echo "Backend not running (stale PID $PID)"
fi
rm -f "$PID_FILE"
