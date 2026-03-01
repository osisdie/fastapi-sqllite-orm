.PHONY: install test lint run pre-commit

install:
	uv sync --extra dev

test:
	uv run pytest tests/ -v --tb=short

lint:
	uv run ruff check src tests

run:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pre-commit:
	pre-commit run --all-files
