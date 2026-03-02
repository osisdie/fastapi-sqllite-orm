"""SQLModel ORM CRUD API."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.sqlmodel.models import CategorySM, ItemSM
from app.db.sqlmodel.session import DbSessionSM
from app.models.sql_crud import (
    CategoryCreate,
    CategoryWithCountResponse,
    CategoryWithItemsResponse,
    ItemCreate,
    ItemResponse,
    ItemUpdate,
)

router = APIRouter(prefix="/sqlmodel/items", tags=["sqlmodel-crud"])


@router.post("/categories", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_category_sm(body: CategoryCreate, db: DbSessionSM) -> dict:
    """Create category (SQLModel)."""
    cat = CategorySM(name=body.name)
    db.add(cat)
    await db.flush()
    await db.refresh(cat)
    return {"id": cat.id, "name": cat.name}


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item_sm(body: ItemCreate, db: DbSessionSM) -> ItemSM:
    """Create item (SQLModel)."""
    item = ItemSM(
        name=body.name,
        description=body.description,
        category_id=body.category_id,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item_sm(item_id: int, db: DbSessionSM) -> ItemSM:
    """Get item by ID (SQLModel)."""
    result = await db.execute(select(ItemSM).where(ItemSM.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.get("", response_model=list[ItemResponse])
async def list_items_sm(db: DbSessionSM) -> list[ItemSM]:
    """List all items (SQLModel)."""
    result = await db.execute(select(ItemSM).order_by(ItemSM.id))
    return list(result.scalars().all())


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item_sm(item_id: int, body: ItemUpdate, db: DbSessionSM) -> ItemSM:
    """Update item (SQLModel)."""
    result = await db.execute(select(ItemSM).where(ItemSM.id == item_id))
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
async def delete_item_sm(item_id: int, db: DbSessionSM) -> None:
    """Delete item (SQLModel)."""
    result = await db.execute(select(ItemSM).where(ItemSM.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    await db.delete(item)


@router.get("/categories-with-items/eager", response_model=list[CategoryWithItemsResponse])
async def list_categories_eager_sm(db: DbSessionSM) -> list[CategorySM]:
    """Eager load (SQLModel, no N+1)."""
    result = await db.execute(
        select(CategorySM).options(selectinload(CategorySM.items)).order_by(CategorySM.id)
    )
    return list(result.scalars().unique().all())


# --- Implicit N+1 (SQLModel): lazy load triggers elsewhere ---


@router.get("/categories-with-items/implicit-pydantic", response_model=list[CategoryWithItemsResponse])
async def list_categories_implicit_pydantic_sm(db: DbSessionSM) -> list[CategorySM]:
    """IMPLICIT N+1: Pydantic serialization accesses category.items → lazy load per category."""
    result = await db.execute(select(CategorySM).order_by(CategorySM.id))
    return list(result.scalars().all())


@router.get("/categories-with-items/implicit-property", response_model=list[CategoryWithCountResponse])
async def list_categories_implicit_property_sm(db: DbSessionSM) -> list[CategorySM]:
    """IMPLICIT N+1: Property item_count accesses len(self.items) → lazy load per category."""
    result = await db.execute(select(CategorySM).order_by(CategorySM.id))
    return list(result.scalars().all())


@router.get("/categories-with-items/implicit-listcomp", response_model=list[CategoryWithItemsResponse])
async def list_categories_implicit_listcomp_sm(db: DbSessionSM) -> list[dict]:
    """IMPLICIT N+1: List comprehension [i for i in c.items] triggers lazy load per category."""
    result = await db.execute(select(CategorySM).order_by(CategorySM.id))
    categories = list(result.scalars().all())
    return [
        {
            "id": c.id,
            "name": c.name,
            "items": [{"id": i.id, "name": i.name, "description": i.description} for i in c.items],
        }
        for c in categories
    ]
