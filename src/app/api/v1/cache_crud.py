"""Cache CRUD API (Redis-ready, in-memory via DI)."""


from cachetools import TTLCache, cached
from fastapi import APIRouter, HTTPException, status

from app.deps import CacheDep
from app.models.cache_crud import CacheItemCreate, CacheItemResponse, CacheItemUpdate

router = APIRouter(prefix="/cache", tags=["cache-crud"])

CACHE_TTL = 5  # seconds

# 5s TTL cache for lru_cache-style endpoint
_ttl_cache = TTLCache(maxsize=100, ttl=CACHE_TTL)


def _compute_cached(key: str) -> str:
    return f"cached:{key}"


@router.post("", response_model=CacheItemResponse, status_code=status.HTTP_201_CREATED)
async def create_cache_item(
    body: CacheItemCreate,
    cache: CacheDep,
) -> CacheItemResponse:
    """Set cache key-value."""
    await cache.set(body.key, body.value, ttl_seconds=CACHE_TTL)
    return CacheItemResponse(key=body.key, value=body.value)


@router.get("/{key}", response_model=CacheItemResponse)
async def get_cache_item(key: str, cache: CacheDep) -> CacheItemResponse:
    """Get cache value by key."""
    value = await cache.get(key)
    if value is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Key not found")
    return CacheItemResponse(key=key, value=str(value))


@router.patch("/{key}", response_model=CacheItemResponse)
async def update_cache_item(
    key: str,
    body: CacheItemUpdate,
    cache: CacheDep,
) -> CacheItemResponse:
    """Update cache value."""
    existing = await cache.get(key)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Key not found")
    await cache.set(key, body.value, ttl_seconds=CACHE_TTL)
    return CacheItemResponse(key=key, value=body.value)


@router.delete("/{key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cache_item(key: str, cache: CacheDep) -> None:
    """Delete cache key."""
    await cache.delete(key)


# --- lru_cache-style endpoint (5s TTL) ---

@cached(cache=_ttl_cache)
def _get_cached_value_sync(key: str) -> str:
    """Sync compute, cached 5s via cachetools TTLCache."""
    return _compute_cached(key)


@router.get("/cached/{key}", response_model=dict)
async def get_cached_value(key: str) -> dict:
    """Get value with 5s TTL cache (lru_cache style)."""
    value = _get_cached_value_sync(key)
    return {"key": key, "value": value}
