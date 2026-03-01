"""Tests for auth endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "payload,expected_status",
    [
        ({"username": "alice"}, 200),
        ({"username": "bob"}, 200),
        ({}, 422),
        ({"username": ""}, 422),
    ],
)
def test_create_token(
    client_no_auth: TestClient, payload: dict, expected_status: int
) -> None:
    """Token endpoint validates request and returns JWT."""
    resp = client_no_auth.post("/api/v1/auth/token", json=payload)
    assert resp.status_code == expected_status
    if expected_status == 200:
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


def test_me_requires_auth(client_no_auth: TestClient) -> None:
    """GET /auth/me returns 401 without Bearer token."""
    resp = client_no_auth.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_with_valid_token(client: TestClient, auth_headers: dict[str, str]) -> None:
    """GET /auth/me returns username with valid token."""
    resp = client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser"
