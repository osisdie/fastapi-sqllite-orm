"""Application configuration with Pydantic Settings for .env injection.

.env is gitignored; use .env.example as template. Environment variables
override .env file values.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic import field_validator


def _parse_bool(v: str | bool) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).lower() in ("true", "1", "yes")


class Settings(BaseSettings):
    """Application settings loaded from .env and environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "python-test"
    debug: bool = False

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, v: str | bool) -> bool:
        if isinstance(v, bool):
            return v
        return _parse_bool(str(v))

    environment: Literal["development", "staging", "production"] = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database (default in-memory SQLite)
    database_url: str = "sqlite+aiosqlite:///:memory:"

    # JWT
    jwt_secret_key: str = "change-me-in-production-use-env"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    @field_validator("jwt_secret_key", mode="before")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if not v or v == "change-me-in-production-use-env":
            return v
        if len(v) < 32:
            raise ValueError("JWT secret should be at least 32 characters in production")
        return v


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
