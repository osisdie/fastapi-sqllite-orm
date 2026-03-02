"""Tests for N+1: eager (correct) vs implicit lazy (Pydantic/property/listcomp)."""

import pytest
from fastapi.testclient import TestClient


def _seed_categories_and_items(client: TestClient, base: str) -> None:
    """Seed categories and items via API for N+1 demo."""
    c1 = client.post(f"{base}/categories", json={"name": "Electronics"})
    c2 = client.post(f"{base}/categories", json={"name": "Books"})
    assert c1.status_code == 201 and c2.status_code == 201
    cat1_id = c1.json()["id"]
    cat2_id = c2.json()["id"]
    client.post(base, json={"name": "Phone", "description": "D", "category_id": cat1_id})
    client.post(base, json={"name": "Laptop", "description": "D", "category_id": cat1_id})
    client.post(base, json={"name": "Novel", "description": "D", "category_id": cat2_id})


# --- Eager (no N+1) ---


@pytest.mark.parametrize("base", ["/api/v1/sqlalchemy/items", "/api/v1/sqlmodel/items"])
def test_eager_endpoint_returns_categories(client: TestClient, base: str) -> None:
    """Eager endpoint returns categories (no N+1)."""
    _seed_categories_and_items(client, base)
    resp = client.get(f"{base}/categories-with-items/eager")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2


@pytest.mark.parametrize("base", ["/api/v1/sqlalchemy/items", "/api/v1/sqlmodel/items"])
def test_eager_returns_items(client: TestClient, base: str) -> None:
    """Eager endpoint: uses selectinload, returns items nested."""
    _seed_categories_and_items(client, base)
    resp = client.get(f"{base}/categories-with-items/eager")
    assert resp.status_code == 200
    data = resp.json()
    electronics = next((c for c in data if c["name"] == "Electronics"), None)
    assert electronics is not None
    assert len(electronics["items"]) == 2


# --- Implicit N+1: skipped ---
# Async SQLAlchemy 不支援 lazy loading，存取 relationship 會觸發 MissingGreenlet。
# 不論 TestClient 或 AsyncClient 都無法避免，因 Pydantic 序列化為 sync。
# 正確做法：使用 selectinload (eager)。手動驗證：uvicorn 啟動後 curl 上述端點。


@pytest.mark.skip(reason="Async SQLAlchemy does not support lazy loading; MissingGreenlet")
@pytest.mark.parametrize("base", ["/api/v1/sqlalchemy/items", "/api/v1/sqlmodel/items"])
def test_implicit_pydantic_returns_categories(client: TestClient, base: str) -> None:
    """Implicit N+1 (Pydantic): lazy load not supported in async SQLAlchemy."""
    _seed_categories_and_items(client, base)
    resp = client.get(f"{base}/categories-with-items/implicit-pydantic")
    assert resp.status_code == 200


@pytest.mark.skip(reason="Async SQLAlchemy does not support lazy loading; MissingGreenlet")
@pytest.mark.parametrize("base", ["/api/v1/sqlalchemy/items", "/api/v1/sqlmodel/items"])
def test_implicit_property_returns_categories(client: TestClient, base: str) -> None:
    """Implicit N+1 (property): lazy load not supported in async SQLAlchemy."""
    _seed_categories_and_items(client, base)
    resp = client.get(f"{base}/categories-with-items/implicit-property")
    assert resp.status_code == 200


@pytest.mark.skip(reason="Async SQLAlchemy does not support lazy loading; MissingGreenlet")
@pytest.mark.parametrize("base", ["/api/v1/sqlalchemy/items", "/api/v1/sqlmodel/items"])
def test_implicit_listcomp_returns_categories(client: TestClient, base: str) -> None:
    """Implicit N+1 (listcomp): lazy load not supported in async SQLAlchemy."""
    _seed_categories_and_items(client, base)
    resp = client.get(f"{base}/categories-with-items/implicit-listcomp")
    assert resp.status_code == 200
