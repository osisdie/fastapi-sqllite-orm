"""Benchmark: SQLAlchemy vs SQLModel - same operations, same syntax."""

import pytest
from fastapi.testclient import TestClient


def _seed_sa(client: TestClient, n_cats: int = 20, items_per_cat: int = 10) -> list[int]:
    """Seed SQLAlchemy tables. Returns category IDs."""
    base = "/api/v1/sqlalchemy/items"
    cat_ids = []
    for i in range(n_cats):
        r = client.post(f"{base}/categories", json={"name": f"Cat{i}"})
        assert r.status_code == 201
        cat_ids.append(r.json()["id"])
    for cid in cat_ids:
        for j in range(items_per_cat):
            client.post(f"{base}", json={"name": f"Item{j}", "description": "D", "category_id": cid})
    return cat_ids


def _seed_sm(client: TestClient, n_cats: int = 20, items_per_cat: int = 10) -> list[int]:
    """Seed SQLModel tables. Returns category IDs."""
    base = "/api/v1/sqlmodel/items"
    cat_ids = []
    for i in range(n_cats):
        r = client.post(f"{base}/categories", json={"name": f"Cat{i}"})
        assert r.status_code == 201
        cat_ids.append(r.json()["id"])
    for cid in cat_ids:
        for j in range(items_per_cat):
            client.post(f"{base}", json={"name": f"Item{j}", "description": "D", "category_id": cid})
    return cat_ids


def test_benchmark_create_item_sa(client: TestClient, benchmark: pytest.BenchmarkFixture) -> None:
    """Benchmark create item (SQLAlchemy)."""
    _seed_sa(client, n_cats=1, items_per_cat=0)
    base = "/api/v1/sqlalchemy/items"

    def run():
        r = client.post(base, json={"name": "X", "description": "D", "category_id": 1})
        assert r.status_code == 201

    benchmark(run)


def test_benchmark_create_item_sm(client: TestClient, benchmark: pytest.BenchmarkFixture) -> None:
    """Benchmark create item (SQLModel)."""
    _seed_sm(client, n_cats=1, items_per_cat=0)
    base = "/api/v1/sqlmodel/items"

    def run():
        r = client.post(base, json={"name": "X", "description": "D", "category_id": 1})
        assert r.status_code == 201

    benchmark(run)


def test_benchmark_list_items_sa(client: TestClient, benchmark: pytest.BenchmarkFixture) -> None:
    """Benchmark list items (SQLAlchemy)."""
    _seed_sa(client, n_cats=5, items_per_cat=20)

    def run():
        r = client.get("/api/v1/sqlalchemy/items")
        assert r.status_code == 200
        return len(r.json())

    result = benchmark(run)
    assert result >= 100


def test_benchmark_list_items_sm(client: TestClient, benchmark: pytest.BenchmarkFixture) -> None:
    """Benchmark list items (SQLModel)."""
    _seed_sm(client, n_cats=5, items_per_cat=20)

    def run():
        r = client.get("/api/v1/sqlmodel/items")
        assert r.status_code == 200
        return len(r.json())

    result = benchmark(run)
    assert result >= 100


def test_benchmark_get_item_sa(client: TestClient, benchmark: pytest.BenchmarkFixture) -> None:
    """Benchmark get item by ID (SQLAlchemy)."""
    _seed_sa(client, n_cats=1, items_per_cat=1)

    def run():
        r = client.get("/api/v1/sqlalchemy/items/1")
        assert r.status_code == 200

    benchmark(run)


def test_benchmark_get_item_sm(client: TestClient, benchmark: pytest.BenchmarkFixture) -> None:
    """Benchmark get item by ID (SQLModel)."""
    _seed_sm(client, n_cats=1, items_per_cat=1)

    def run():
        r = client.get("/api/v1/sqlmodel/items/1")
        assert r.status_code == 200

    benchmark(run)


def test_benchmark_categories_eager_sa(client: TestClient, benchmark: pytest.BenchmarkFixture) -> None:
    """Benchmark categories-with-items eager (SQLAlchemy, no N+1)."""
    _seed_sa(client, n_cats=20, items_per_cat=10)

    def run():
        r = client.get("/api/v1/sqlalchemy/items/categories-with-items/eager")
        assert r.status_code == 200
        return len(r.json())

    result = benchmark(run)
    assert result >= 20


def test_benchmark_categories_eager_sm(client: TestClient, benchmark: pytest.BenchmarkFixture) -> None:
    """Benchmark categories-with-items eager (SQLModel, no N+1)."""
    _seed_sm(client, n_cats=20, items_per_cat=10)

    def run():
        r = client.get("/api/v1/sqlmodel/items/categories-with-items/eager")
        assert r.status_code == 200
        return len(r.json())

    result = benchmark(run)
    assert result >= 20
