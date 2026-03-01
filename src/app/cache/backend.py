"""Cache backend interface and implementations (in-memory for DI, Redis-ready)."""

from abc import ABC, abstractmethod
from typing import Any

from cachetools import TTLCache


class CacheBackend(ABC):
    """Abstract cache backend for DI injection."""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Get value by key."""
        ...

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Set key-value with optional TTL."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete key. Returns True if key existed."""
        ...


class InMemoryCacheBackend(CacheBackend):
    """In-memory cache using TTLCache (5s default TTL for demo)."""

    def __init__(self, maxsize: int = 1000, ttl: int = 5) -> None:
        self._cache: TTLCache[str, Any] = TTLCache(maxsize=maxsize, ttl=ttl)

    async def get(self, key: str) -> Any | None:
        return self._cache.get(key)

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        self._cache[key] = value

    async def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False
