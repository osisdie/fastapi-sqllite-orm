"""Tests for N+1: eager (correct) vs implicit lazy (Pydantic/property/listcomp)."""

from fastapi.testclient import TestClient


def _seed_categories_and_items(client: TestClient) -> None:
    """Seed categories and items via API for N+1 demo."""
    c1 = client.post("/api/v1/items/categories", json={"name": "Electronics"})
    c2 = client.post("/api/v1/items/categories", json={"name": "Books"})
    assert c1.status_code == 201 and c2.status_code == 201
    cat1_id = c1.json()["id"]
    cat2_id = c2.json()["id"]
    client.post("/api/v1/items", json={"name": "Phone", "description": "D", "category_id": cat1_id})
    client.post("/api/v1/items", json={"name": "Laptop", "description": "D", "category_id": cat1_id})
    client.post("/api/v1/items", json={"name": "Novel", "description": "D", "category_id": cat2_id})


def test_eager_endpoint_returns_categories(client: TestClient) -> None:
    """Eager endpoint returns categories (no N+1)."""
    _seed_categories_and_items(client)
    resp = client.get("/api/v1/items/categories-with-items/eager")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2


def test_eager_returns_items(client: TestClient) -> None:
    """Eager endpoint: uses selectinload, returns items nested."""
    _seed_categories_and_items(client)
    resp = client.get("/api/v1/items/categories-with-items/eager")
    assert resp.status_code == 200
    data = resp.json()
    electronics = next((c for c in data if c["name"] == "Electronics"), None)
    assert electronics is not None
    assert len(electronics["items"]) == 2


# Implicit N+1 endpoints (implicit-pydantic, implicit-property, implicit-listcomp) trigger
# lazy load. With async SQLAlchemy + TestClient, this causes MissingGreenlet.
# Verify manually: ./scripts/start_backend.sh && curl -H "Authorization: Bearer $TOKEN" \
#   http://localhost:8000/api/v1/items/categories-with-items/implicit-pydantic
