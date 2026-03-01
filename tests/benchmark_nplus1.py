"""Benchmark: SQL with vs without N+1 (eager vs nplus1 endpoints)."""

import pytest
from fastapi.testclient import TestClient


def _seed(client: TestClient, n_categories: int = 20, items_per_cat: int = 10) -> None:
    """Seed N categories with M items each."""
    cat_ids = []
    for i in range(n_categories):
        r = client.post("/api/v1/items/categories", json={"name": f"Cat{i}"})
        assert r.status_code == 201
        cat_ids.append(r.json()["id"])
    for cid in cat_ids:
        for j in range(items_per_cat):
            client.post(
                "/api/v1/items",
                json={"name": f"Item{j}", "description": "D", "category_id": cid},
            )


def test_benchmark_eager(client: TestClient, benchmark: pytest.BenchmarkFixture) -> None:
    """Benchmark eager load (no N+1): 2 queries total."""
    _seed(client, n_categories=20, items_per_cat=10)

    def run():
        r = client.get("/api/v1/items/categories-with-items/eager")
        assert r.status_code == 200
        return len(r.json())

    result = benchmark(run)
    assert result >= 20


def test_benchmark_nplus1(client: TestClient, benchmark: pytest.BenchmarkFixture) -> None:
    """Benchmark N+1: 1 + N queries (slower than eager)."""
    _seed(client, n_categories=20, items_per_cat=10)

    def run():
        r = client.get("/api/v1/items/categories-with-items/nplus1")
        assert r.status_code == 200
        return len(r.json())

    result = benchmark(run)
    assert result >= 20
