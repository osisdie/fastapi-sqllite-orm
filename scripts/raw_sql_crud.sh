#!/usr/bin/env bash
# Raw SQL CRUD API via curl (SQL from files, variables injected)
# Usage: ./scripts/raw_sql_crud.sh [BASE_URL]

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

echo "=== Create raw item ==="
CREATE=$(curl -s -X POST "${BASE_URL}/api/v1/raw-items" \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d '{"name": "Raw Item", "description": "From SQL file"}')
echo "$CREATE" | jq .
ID=$(echo "$CREATE" | jq -r '.id')

echo ""
echo "=== List raw items ==="
curl -s -X GET "${BASE_URL}/api/v1/raw-items" -H "$AUTH" | jq .

echo ""
echo "=== Get raw item by ID ($ID) ==="
curl -s -X GET "${BASE_URL}/api/v1/raw-items/${ID}" -H "$AUTH" | jq .

echo ""
echo "=== Update raw item ==="
curl -s -X PATCH "${BASE_URL}/api/v1/raw-items/${ID}" \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d '{"name": "Raw Updated", "description": "Patched"}' | jq .

echo ""
echo "=== Delete raw item ==="
curl -s -X DELETE "${BASE_URL}/api/v1/raw-items/${ID}" -H "$AUTH" -w "\nHTTP Status: %{http_code}\n"
