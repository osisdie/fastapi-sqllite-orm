"""Tests for Cache CRUD API."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "payload,expected_status",
    [
        ({"key": "k1", "value": "v1"}, 201),
        ({"key": "k2", "value": "v2"}, 201),
        ({}, 422),
        ({"key": ""}, 422),
    ],
)
def test_create_cache_item(
    client: TestClient, payload: dict, expected_status: int
) -> None:
    """Create cache item via POST."""
    resp = client.post("/api/v1/cache", json=payload)
    assert resp.status_code == expected_status
    if expected_status == 201:
        data = resp.json()
        assert data["key"] == payload["key"]
        assert data["value"] == payload["value"]


def test_get_cache_item(client: TestClient) -> None:
    """Get cache value by key."""
    client.post("/api/v1/cache", json={"key": "k1", "value": "v1"})
    resp = client.get("/api/v1/cache/k1")
    assert resp.status_code == 200
    assert resp.json()["value"] == "v1"


def test_get_cache_item_not_found(client: TestClient) -> None:
    """Get non-existent key returns 404."""
    resp = client.get("/api/v1/cache/nonexistent")
    assert resp.status_code == 404


def test_update_cache_item(client: TestClient) -> None:
    """Update cache value."""
    client.post("/api/v1/cache", json={"key": "k1", "value": "v1"})
    resp = client.patch("/api/v1/cache/k1", json={"value": "v2"})
    assert resp.status_code == 200
    assert resp.json()["value"] == "v2"


def test_delete_cache_item(client: TestClient) -> None:
    """Delete cache key."""
    client.post("/api/v1/cache", json={"key": "k1", "value": "v1"})
    resp = client.delete("/api/v1/cache/k1")
    assert resp.status_code == 204
    get_resp = client.get("/api/v1/cache/k1")
    assert get_resp.status_code == 404


def test_cached_endpoint_5s_ttl(client: TestClient) -> None:
    """Cached endpoint returns value (5s TTL)."""
    resp = client.get("/api/v1/cache/cached/foo")
    assert resp.status_code == 200
    data = resp.json()
    assert data["key"] == "foo"
    assert "cached:" in data["value"]
