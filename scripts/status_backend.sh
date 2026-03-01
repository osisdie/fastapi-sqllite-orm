#!/usr/bin/env bash
# Check backend status
# Usage: ./scripts/status_backend.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_FILE="${PROJECT_ROOT}/.backend.pid"

if [ ! -f "$PID_FILE" ]; then
  echo "Backend not running (no PID file)"
  exit 1
fi

PID=$(cat "$PID_FILE")
if kill -0 "$PID" 2>/dev/null; then
  echo "Backend running (PID $PID)"
  exit 0
else
  echo "Backend not running (stale PID $PID)"
  rm -f "$PID_FILE"
  exit 1
fi
