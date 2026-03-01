"""Tests for raw SQL CRUD API."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "payload,expected_status",
    [
        ({"name": "Raw A", "description": "Desc A"}, 201),
        ({"name": "Raw B"}, 201),
        ({}, 422),
        ({"name": ""}, 422),
    ],
)
def test_create_raw_item(
    client: TestClient, payload: dict, expected_status: int
) -> None:
    """Create item via raw SQL."""
    resp = client.post("/api/v1/raw-items", json=payload)
    assert resp.status_code == expected_status
    if expected_status == 201:
        data = resp.json()
        assert "id" in data
        assert data["name"] == payload["name"]


def test_list_raw_items(client: TestClient) -> None:
    """List items via raw SQL."""
    client.post("/api/v1/raw-items", json={"name": "X", "description": "Y"})
    resp = client.get("/api/v1/raw-items")
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    assert any(i["name"] == "X" for i in items)


def test_get_raw_item(client: TestClient) -> None:
    """Get item by ID via raw SQL."""
    create = client.post("/api/v1/raw-items", json={"name": "GetMe", "description": "D"})
    assert create.status_code == 201
    item_id = create.json()["id"]
    resp = client.get(f"/api/v1/raw-items/{item_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "GetMe"


def test_get_raw_item_not_found(client: TestClient) -> None:
    """Get non-existent item returns 404."""
    resp = client.get("/api/v1/raw-items/99999")
    assert resp.status_code == 404


def test_update_raw_item(client: TestClient) -> None:
    """Update item via raw SQL."""
    create = client.post("/api/v1/raw-items", json={"name": "Old", "description": "D"})
    item_id = create.json()["id"]
    resp = client.patch(f"/api/v1/raw-items/{item_id}", json={"name": "New"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "New"


def test_delete_raw_item(client: TestClient) -> None:
    """Delete item via raw SQL."""
    create = client.post("/api/v1/raw-items", json={"name": "ToDelete", "description": "D"})
    item_id = create.json()["id"]
    resp = client.delete(f"/api/v1/raw-items/{item_id}")
    assert resp.status_code == 204
    get_resp = client.get(f"/api/v1/raw-items/{item_id}")
    assert get_resp.status_code == 404
