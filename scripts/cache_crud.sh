#!/usr/bin/env bash
# Cache CRUD API via curl (with payload)
# Usage: ./scripts/cache_crud.sh [BASE_URL]

set -e
BASE_URL="${1:-http://localhost:8000}"

TOKEN=$(curl -s -X POST "${BASE_URL}/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "curl-user"}' | jq -r '.access_token')
if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
  echo "Failed to get token. Is backend running?"
  exit 1
fi
AUTH="Authorization: Bearer $TOKEN"

echo "=== Create cache item ==="
curl -s -X POST "${BASE_URL}/api/v1/cache" \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d '{"key": "user:1", "value": "Alice"}' | jq .

echo ""
echo "=== Get cache item ==="
curl -s -X GET "${BASE_URL}/api/v1/cache/user:1" -H "$AUTH" | jq .

echo ""
echo "=== Update cache item ==="
curl -s -X PATCH "${BASE_URL}/api/v1/cache/user:1" \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d '{"value": "Alice Updated"}' | jq .

echo ""
echo "=== Create another cache item ==="
curl -s -X POST "${BASE_URL}/api/v1/cache" \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d '{"key": "config:theme", "value": "dark"}' | jq .

echo ""
echo "=== Get cached value (5s TTL lru_cache) ==="
curl -s -X GET "${BASE_URL}/api/v1/cache/cached/foo" -H "$AUTH" | jq .

echo ""
echo "=== Delete cache item ==="
curl -s -X DELETE "${BASE_URL}/api/v1/cache/user:1" -H "$AUTH" -w "\nHTTP Status: %{http_code}\n"
