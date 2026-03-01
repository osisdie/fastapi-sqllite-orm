"""SQL CRUD API with ORM (SQLite / in-memory via DI)."""


from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import set_committed_value

from app.db.models import Category, Item
from app.db.session import DbSession
from app.models.sql_crud import (
    CategoryCreate,
    CategoryWithItemsResponse,
    ItemCreate,
    ItemResponse,
    ItemUpdate,
)

router = APIRouter(prefix="/items", tags=["sql-crud"])


@router.post("/categories", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_category(body: CategoryCreate, db: DbSession) -> dict:
    """Create category (for N+1 demo)."""
    cat = Category(name=body.name)
    db.add(cat)
    await db.flush()
    await db.refresh(cat)
    return {"id": cat.id, "name": cat.name}


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    body: ItemCreate,
    db: DbSession,
) -> Item:
    """Create item."""
    item = Item(
        name=body.name,
        description=body.description,
        category_id=body.category_id,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: DbSession) -> Item:
    """Get item by ID."""
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.get("", response_model=list[ItemResponse])
async def list_items(db: DbSession) -> list[Item]:
    """List all items."""
    result = await db.execute(select(Item).order_by(Item.id))
    return list(result.scalars().all())


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, body: ItemUpdate, db: DbSession) -> Item:
    """Update item."""
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if body.name is not None:
        item.name = body.name
    if body.description is not None:
        item.description = body.description
    await db.flush()
    await db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, db: DbSession) -> None:
    """Delete item."""
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    await db.delete(item)


# --- N+1 demo endpoints ---


@router.get("/categories-with-items/eager", response_model=list[CategoryWithItemsResponse])
async def list_categories_eager(db: DbSession) -> list[Category]:
    """List categories with items - NO N+1 (eager load via selectinload)."""
    result = await db.execute(
        select(Category).options(selectinload(Category.items)).order_by(Category.id)
    )
    return list(result.scalars().unique().all())


@router.get("/categories-with-items/nplus1", response_model=list[CategoryWithItemsResponse])
async def list_categories_nplus1(db: DbSession) -> list[Category]:
    """List categories with items - CAUSES N+1 (explicit N queries in loop)."""
    result = await db.execute(select(Category).order_by(Category.id))
    categories = list(result.scalars().all())
    # Explicit N+1: 1 query for categories + N queries for items (simulates lazy load)
    for cat in categories:
        items_result = await db.execute(select(Item).where(Item.category_id == cat.id))
        items = list(items_result.scalars().all())
        set_committed_value(cat, "items", items)
    return categories
