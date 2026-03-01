#!/usr/bin/env bash
# Start backend (uvicorn) in background
# Usage: ./scripts/start_backend.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_FILE="${PROJECT_ROOT}/.backend.pid"
LOG_FILE="${PROJECT_ROOT}/.backend.log"

cd "$PROJECT_ROOT" || exit 1

if [ -f "$PID_FILE" ]; then
  OLD_PID=$(cat "$PID_FILE")
  if kill -0 "$OLD_PID" 2>/dev/null; then
    echo "Backend already running (PID $OLD_PID)"
    exit 0
  fi
  rm -f "$PID_FILE"
fi

echo "Starting backend..."
PYTHONPATH=src uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 >> "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
echo "Backend started (PID $(cat "$PID_FILE")). Log: $LOG_FILE"
