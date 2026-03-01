#!/usr/bin/env bash
# Health check via curl
# Usage: ./scripts/health_check.sh [BASE_URL]

set -e
BASE_URL="${1:-http://localhost:8000}"

echo "=== Health Check ==="
curl -s -X GET "${BASE_URL}/api/v1/health" | jq .
