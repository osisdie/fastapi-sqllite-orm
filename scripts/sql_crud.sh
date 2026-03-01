#!/usr/bin/env bash
# SQL CRUD API via curl (with payload)
# Usage: ./scripts/sql_crud.sh [BASE_URL]
# Requires: JWT token (obtain via POST /api/v1/auth/token)

set -e
BASE_URL="${1:-http://localhost:8000}"

# Get JWT token
TOKEN=$(curl -s -X POST "${BASE_URL}/api/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "curl-user"}' | jq -r '.access_token')
if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
  echo "Failed to get token. Is backend running?"
  exit 1
fi
AUTH="Authorization: Bearer $TOKEN"

echo "=== Create item ==="
CREATE=$(curl -s -X POST "${BASE_URL}/api/v1/items" \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d '{"name": "Test Item", "description": "Created via curl"}')
echo "$CREATE" | jq .
ID=$(echo "$CREATE" | jq -r '.id')

echo ""
echo "=== List items ==="
curl -s -X GET "${BASE_URL}/api/v1/items" -H "$AUTH" | jq .

echo ""
echo "=== Get item by ID ($ID) ==="
curl -s -X GET "${BASE_URL}/api/v1/items/${ID}" -H "$AUTH" | jq .

echo ""
echo "=== Update item ==="
curl -s -X PATCH "${BASE_URL}/api/v1/items/${ID}" \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d '{"name": "Updated Item", "description": "Patched via curl"}' | jq .

echo ""
echo "=== Create category (for N+1 demo) ==="
CAT=$(curl -s -X POST "${BASE_URL}/api/v1/items/categories" \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d '{"name": "Electronics"}')
echo "$CAT" | jq .
CAT_ID=$(echo "$CAT" | jq -r '.id')

echo ""
echo "=== Create item with category_id ==="
curl -s -X POST "${BASE_URL}/api/v1/items" \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d "{\"name\": \"Phone\", \"description\": \"Smartphone\", \"category_id\": ${CAT_ID}}" | jq .

echo ""
echo "=== Categories with items (eager - no N+1) ==="
curl -s -X GET "${BASE_URL}/api/v1/items/categories-with-items/eager" -H "$AUTH" | jq .

echo ""
echo "=== Delete item ($ID) ==="
curl -s -X DELETE "${BASE_URL}/api/v1/items/${ID}" -H "$AUTH" -w "\nHTTP Status: %{http_code}\n"
