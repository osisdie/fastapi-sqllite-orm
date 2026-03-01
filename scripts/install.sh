# ================================
# install dependencies
# ================================
uv sync --extra dev

# ================================
# run uvicorn
# ================================
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# ================================
# run tests
# ================================
uv run pytest tests/ -v

# ================================
# pre-commit
# ================================
# pre-commit
pre-commit install
pre-commit run --all-files
