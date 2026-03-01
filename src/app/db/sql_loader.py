"""Load SQL from files and inject variables (named params :name)."""

from pathlib import Path

import app

# app package root (where __init__.py lives)
_APP_ROOT = Path(app.__file__).parent
SQL_DIR = _APP_ROOT / "sql"


def load_sql(filename: str) -> str:
    """Load SQL from file. Returns raw SQL string with :param placeholders."""
    path = SQL_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")
    return path.read_text().strip()


def inject_params(sql: str, params: dict) -> str:
    """Replace :param placeholders with values (for logging/debug). Not for execution."""
    result = sql
    for k, v in params.items():
        result = result.replace(f":{k}", repr(v))
    return result
