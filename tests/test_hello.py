"""Tests for hello endpoints with parametrize."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "path,method,expected_status",
    [
        ("/api/v1/hello", "GET", 200),
        ("/api/v1/hello", "POST", 422),  # POST without body fails validation
    ],
)
def test_hello_methods(
    client: TestClient, path: str, method: str, expected_status: int
) -> None:
    """Hello endpoint responds correctly by method."""
    if method == "GET":
        resp = client.get(path)
    else:
        resp = client.post(path, json={})
    assert resp.status_code == expected_status


@pytest.mark.parametrize(
    "payload,expected_status,expected_message_contains",
    [
        ({"name": "Alice"}, 200, "Alice"),
        ({"name": "  Bob  "}, 200, "Bob"),
        ({}, 422, None),
        ({"name": ""}, 422, None),
        ({"name": "   "}, 422, None),
        ({"name": "x" * 101}, 422, None),
    ],
)
def test_hello_post_validation(
    client: TestClient,
    payload: dict,
    expected_status: int,
    expected_message_contains: str | None,
) -> None:
    """Hello POST validates request body with Pydantic."""
    resp = client.post("/api/v1/hello", json=payload)
    assert resp.status_code == expected_status
    if expected_status == 200:
        assert expected_message_contains in resp.json()["message"]


def test_hello_get_unauthenticated(client_no_auth: TestClient) -> None:
    """Hello GET without auth returns 401 (JWT required)."""
    resp = client_no_auth.get("/api/v1/hello")
    assert resp.status_code == 401


def test_hello_get_authenticated(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Hello GET with auth returns greeting to username."""
    resp = client.get("/api/v1/hello", headers=auth_headers)
    assert resp.status_code == 200
    assert "testuser" in resp.json()["message"]
