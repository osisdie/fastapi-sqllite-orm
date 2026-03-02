"""Tests for SQL CRUD API (SQLAlchemy ORM)."""

import pytest
from fastapi.testclient import TestClient

BASE = "/api/v1/sqlalchemy/items"


@pytest.mark.parametrize(
    "payload,expected_status",
    [
        ({"name": "Item A", "description": "Desc A"}, 201),
        ({"name": "Item B"}, 201),
        ({}, 422),
        ({"name": ""}, 422),
    ],
)
def test_create_item(
    client: TestClient, payload: dict, expected_status: int
) -> None:
    """Create item via POST."""
    resp = client.post(BASE, json=payload)
    assert resp.status_code == expected_status
    if expected_status == 201:
        data = resp.json()
        assert "id" in data
        assert data["name"] == payload["name"]
        assert data.get("description") == payload.get("description")


def test_list_items(client: TestClient) -> None:
    """List items."""
    client.post(BASE, json={"name": "X", "description": "Y"})
    resp = client.get(BASE)
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    assert any(i["name"] == "X" for i in items)


def test_get_item(client: TestClient) -> None:
    """Get item by ID."""
    create = client.post(BASE, json={"name": "GetMe", "description": "D"})
    assert create.status_code == 201
    item_id = create.json()["id"]
    resp = client.get(f"{BASE}/{item_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "GetMe"


def test_get_item_not_found(client: TestClient) -> None:
    """Get non-existent item returns 404."""
    resp = client.get(f"{BASE}/99999")
    assert resp.status_code == 404


def test_update_item(client: TestClient) -> None:
    """Update item."""
    create = client.post(BASE, json={"name": "Old", "description": "D"})
    item_id = create.json()["id"]
    resp = client.patch(f"{BASE}/{item_id}", json={"name": "New"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "New"


def test_delete_item(client: TestClient) -> None:
    """Delete item."""
    create = client.post(BASE, json={"name": "ToDelete", "description": "D"})
    item_id = create.json()["id"]
    resp = client.delete(f"{BASE}/{item_id}")
    assert resp.status_code == 204
    get_resp = client.get(f"{BASE}/{item_id}")
    assert get_resp.status_code == 404
