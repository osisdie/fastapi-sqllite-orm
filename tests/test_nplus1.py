"""Tests for N+1 query comparison: eager (no N+1) vs lazy (causes N+1)."""

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


def test_eager_vs_nplus1_returns_same_data(client: TestClient) -> None:
    """Both eager (no N+1) and nplus1 endpoints return identical data."""
    _seed_categories_and_items(client)

    resp_eager = client.get("/api/v1/items/categories-with-items/eager")
    assert resp_eager.status_code == 200
    eager_data = resp_eager.json()

    resp_nplus1 = client.get("/api/v1/items/categories-with-items/nplus1")
    assert resp_nplus1.status_code == 200
    nplus1_data = resp_nplus1.json()

    assert len(eager_data) == len(nplus1_data)
    for e, n in zip(eager_data, nplus1_data):
        assert e["id"] == n["id"]
        assert e["name"] == n["name"]
        assert len(e["items"]) == len(n["items"])


def test_eager_no_nplus1(client: TestClient) -> None:
    """Eager endpoint: uses selectinload, 2 queries total (categories + items)."""
    _seed_categories_and_items(client)
    resp = client.get("/api/v1/items/categories-with-items/eager")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2
    electronics = next((c for c in data if c["name"] == "Electronics"), None)
    assert electronics is not None
    assert len(electronics["items"]) == 2


def test_nplus1_causes_extra_queries(client: TestClient) -> None:
    """N+1 endpoint: lazy load in loop causes 1 + N queries (documented behavior)."""
    _seed_categories_and_items(client)
    resp = client.get("/api/v1/items/categories-with-items/nplus1")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2
