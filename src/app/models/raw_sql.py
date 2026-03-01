"""Pydantic schemas for raw SQL CRUD API."""

from pydantic import BaseModel, Field


class RawItemCreate(BaseModel):
    """Create item (raw SQL)."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    category_id: int | None = None


class RawItemUpdate(BaseModel):
    """Update item (raw SQL)."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class RawItemResponse(BaseModel):
    """Item response from raw SQL."""

    id: int
    name: str
    description: str | None
    category_id: int | None
