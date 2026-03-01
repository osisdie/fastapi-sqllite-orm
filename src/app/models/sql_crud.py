"""Pydantic schemas for SQL CRUD API."""

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    """Create category request."""

    name: str = Field(..., min_length=1, max_length=255)


class ItemCreate(BaseModel):
    """Create item request."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    category_id: int | None = None


class ItemUpdate(BaseModel):
    """Update item request (partial)."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class ItemResponse(BaseModel):
    """Item response schema."""

    id: int
    name: str
    description: str | None

    model_config = {"from_attributes": True}


class CategoryWithItemsResponse(BaseModel):
    """Category with items (for N+1 demo)."""

    id: int
    name: str
    items: list[ItemResponse]

    model_config = {"from_attributes": True}


class CategoryWithCountResponse(BaseModel):
    """Category with item_count (property triggers lazy load on .items)."""

    id: int
    name: str
    item_count: int

    model_config = {"from_attributes": True}
