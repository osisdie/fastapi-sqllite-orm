"""Tests for health endpoint."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "path,expected_status",
    [
        ("/api/v1/health", 200),
    ],
)
def test_health(client_no_auth: TestClient, path: str, expected_status: int) -> None:
    """Health endpoint returns ok and version (no auth required)."""
    resp = client_no_auth.get(path)
    assert resp.status_code == expected_status
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data
