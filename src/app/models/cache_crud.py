"""Pydantic schemas for Cache CRUD API."""

from pydantic import BaseModel, Field


class CacheItemCreate(BaseModel):
    """Create cache item request."""

    key: str = Field(..., min_length=1, max_length=255)
    value: str = Field(..., max_length=10000)


class CacheItemUpdate(BaseModel):
    """Update cache item (value only)."""

    value: str = Field(..., max_length=10000)


class CacheItemResponse(BaseModel):
    """Cache item response."""

    key: str
    value: str
