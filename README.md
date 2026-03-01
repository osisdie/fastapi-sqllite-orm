# python-test

FastAPI project with Pydantic validation, JWT auth, Swagger, versioning, and modern tooling.

## Features

- **FastAPI** with health & hello APIs
- **SQL ORM CRUD** (SQLite, in-memory via DI)
- **Cache CRUD** (Redis-ready, in-memory via DI)
- **lru_cache** with 5s TTL (cachetools TTLCache)
- **Swagger UI** at `/docs`, ReDoc at `/redoc`
- **API versioning** (`/api/v1/...`)
- **Pydantic** models with field validation
- **Global exception handler** for validation and app errors
- **JWT** Bearer token auth + middleware (exempt: health, docs, auth/token)
- **config.py** with Pydantic Settings (`.env` injection, `.env` stays gitignored)
- **pytest** with parametrize
- **pre-commit** (ruff, hooks)
- **CI** for GitHub Actions and GitLab CI

## Quick Start

```bash
# Using uv (recommended)
uv sync --extra dev
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or pip
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Copy `.env.example` to `.env` and edit if needed (optional).

Visit: http://localhost:8000/docs

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/health` | No | Health check |
| POST | `/api/v1/auth/token` | No | Get JWT `{ "username": "..." }` |
| GET | `/api/v1/hello` | Bearer | Hello |
| POST | `/api/v1/hello` | Bearer | Hello with body |
| GET | `/api/v1/auth/me` | Bearer | Current user |
| POST | `/api/v1/items` | Bearer | Create item (ORM) |
| GET | `/api/v1/items` | Bearer | List items |
| GET | `/api/v1/items/{id}` | Bearer | Get item |
| PATCH | `/api/v1/items/{id}` | Bearer | Update item |
| DELETE | `/api/v1/items/{id}` | Bearer | Delete item |
| POST | `/api/v1/items/categories` | Bearer | Create category |
| GET | `/api/v1/items/categories-with-items/eager` | Bearer | Categories+items (no N+1) |
| GET | `/api/v1/items/categories-with-items/nplus1` | Bearer | Categories+items (N+1 demo) |
| POST | `/api/v1/raw-items` | Bearer | Create item (raw SQL from file) |
| GET | `/api/v1/raw-items` | Bearer | List items (raw SQL) |
| GET | `/api/v1/raw-items/{id}` | Bearer | Get item (raw SQL) |
| PATCH | `/api/v1/raw-items/{id}` | Bearer | Update item (raw SQL) |
| DELETE | `/api/v1/raw-items/{id}` | Bearer | Delete item (raw SQL) |
| POST | `/api/v1/cache` | Bearer | Set cache key-value |
| GET | `/api/v1/cache/{key}` | Bearer | Get cache value |
| PATCH | `/api/v1/cache/{key}` | Bearer | Update cache value |
| DELETE | `/api/v1/cache/{key}` | Bearer | Delete cache key |
| GET | `/api/v1/cache/cached/{key}` | Bearer | Cached value (5s TTL) |

## Scripts

```bash
# Backend lifecycle
./scripts/start_backend.sh
./scripts/status_backend.sh
./scripts/stop_backend.sh

# Health check (no auth)
./scripts/health_check.sh [BASE_URL]

# SQL CRUD, Cache CRUD, Raw SQL CRUD (auto-fetch JWT)
./scripts/sql_crud.sh [BASE_URL]
./scripts/cache_crud.sh [BASE_URL]
./scripts/raw_sql_crud.sh [BASE_URL]
```

## Tests

```bash
uv run pytest tests/ -v
# Benchmark N+1 vs eager: pytest tests/benchmark_nplus1.py -v --benchmark-only
```

## Pre-commit

```bash
pre-commit install
pre-commit run --all-files
```

## VS Code Debug

- **FastAPI (debug)**: Run with `--reload`
- **FastAPI (non-debug)**: Run without reload
- **Pytest (current file)** / **Pytest (all)**: Debug tests

Ensure `PYTHONPATH` includes `src` (launch.json sets it).

## Project Structure

```
src/app/
├── main.py          # FastAPI app
├── config.py        # Pydantic Settings (.env)
├── auth.py          # JWT create/verify
├── exceptions.py    # Global handlers
├── deps.py          # Cache DI (in-memory / Redis)
├── db/
│   ├── session.py   # DB session (SQLite)
│   ├── models.py    # Item, Category ORM
│   └── base.py
├── cache/
│   └── backend.py  # InMemoryCacheBackend (Redis-ready)
├── api/v1/
│   ├── health.py
│   ├── hello.py
│   ├── auth.py
│   ├── sql_crud.py
│   └── cache_crud.py
└── models/
    ├── health.py
    ├── hello.py
    ├── sql_crud.py
    └── cache_crud.py
scripts/
├── health_check.sh
├── sql_crud.sh
└── cache_crud.sh
tests/
├── conftest.py
├── test_health.py
├── test_hello.py
├── test_auth.py
├── test_sql_crud.py
├── test_cache_crud.py
├── test_nplus1.py   # Eager vs N+1 comparison
└── pydantic/question1.py
```
