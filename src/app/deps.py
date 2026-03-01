"""Dependency injection for cache backend (in-memory by default, Redis via override)."""

from typing import Annotated

from fastapi import Depends

from app.cache.backend import CacheBackend, InMemoryCacheBackend

# Default: in-memory cache. Override in tests or via app state for Redis.
_cache_backend: CacheBackend | None = None


def get_cache_backend() -> CacheBackend:
    """Return cache backend (in-memory by default)."""
    global _cache_backend
    if _cache_backend is None:
        _cache_backend = InMemoryCacheBackend(maxsize=1000, ttl=5)
    return _cache_backend


def set_cache_backend(backend: CacheBackend) -> None:
    """Override cache backend (for tests or Redis)."""
    global _cache_backend
    _cache_backend = backend


CacheDep = Annotated[CacheBackend, Depends(get_cache_backend)]
