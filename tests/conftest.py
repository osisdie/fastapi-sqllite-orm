"""Pytest configuration and fixtures."""

import os

# Use file-based SQLite for tests (in-memory creates new DB per connection)
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import _engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def ensure_tables():
    """Ensure DB tables exist before any test runs."""
    import asyncio

    async def _create():
        from app.db.models import Category, Item  # noqa: F401

        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_create())
    yield


class AuthTestClient(TestClient):
    """TestClient that adds JWT auth headers to all requests."""

    def __init__(self, app, *args, auth_headers: dict[str, str] | None = None, **kwargs):
        super().__init__(app, *args, **kwargs)
        self._auth_headers = auth_headers or {}

    def request(self, *args, **kwargs):
        headers = dict(kwargs.get("headers") or {})
        headers.update(self._auth_headers)
        kwargs["headers"] = headers
        return super().request(*args, **kwargs)


@pytest.fixture
def client_no_auth() -> TestClient:
    """Test client without auth (for testing 401 on protected endpoints)."""
    return TestClient(app)


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client with JWT auth (for non-exempt endpoints)."""
    raw = TestClient(app)
    resp = raw.post("/api/v1/auth/token", json={"username": "testuser"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return AuthTestClient(app, auth_headers={"Authorization": f"Bearer {token}"})


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    """Headers with valid JWT for authenticated requests."""
    resp = client.post("/api/v1/auth/token", json={"username": "testuser"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
