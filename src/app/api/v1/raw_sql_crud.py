"""SQL non-ORM CRUD: raw SQL from files with variable injection."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from app.db.session import DbSession
from app.db.sql_loader import load_sql
from app.models.raw_sql import RawItemCreate, RawItemResponse, RawItemUpdate

router = APIRouter(prefix="/raw-items", tags=["raw-sql-crud"])


def _row_to_item(row) -> RawItemResponse:
    """Convert DB row to response model."""
    return RawItemResponse(
        id=row.id,
        name=row.name,
        description=row.description,
        category_id=row.category_id,
    )


@router.post("", response_model=RawItemResponse, status_code=status.HTTP_201_CREATED)
async def create_raw_item(body: RawItemCreate, db: DbSession) -> RawItemResponse:
    """Create item via raw SQL from file (variables injected from request)."""
    sql = load_sql("items_insert.sql")
    params = {
        "name": body.name,
        "description": body.description,
        "category_id": body.category_id,
    }
    result = await db.execute(text(sql), params)
    row = result.mappings().one()
    return _row_to_item(row)


@router.get("/{item_id}", response_model=RawItemResponse)
async def get_raw_item(item_id: int, db: DbSession) -> RawItemResponse:
    """Get item by ID via raw SQL."""
    sql = load_sql("items_select_by_id.sql")
    result = await db.execute(text(sql), {"id": item_id})
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return _row_to_item(row)


@router.get("", response_model=list[RawItemResponse])
async def list_raw_items(db: DbSession) -> list[RawItemResponse]:
    """List all items via raw SQL."""
    sql = load_sql("items_select_all.sql")
    result = await db.execute(text(sql))
    return [_row_to_item(r) for r in result.mappings().all()]


@router.patch("/{item_id}", response_model=RawItemResponse)
async def update_raw_item(item_id: int, body: RawItemUpdate, db: DbSession) -> RawItemResponse:
    """Update item via raw SQL."""
    # Fetch current
    get_sql = load_sql("items_select_by_id.sql")
    get_result = await db.execute(text(get_sql), {"id": item_id})
    row = get_result.mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    name = body.name if body.name is not None else row.name
    description = body.description if body.description is not None else row.description

    sql = load_sql("items_update.sql")
    await db.execute(text(sql), {"id": item_id, "name": name, "description": description})
    await db.flush()

    fetch_result = await db.execute(text(get_sql), {"id": item_id})
    updated = fetch_result.mappings().one()
    return _row_to_item(updated)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_raw_item(item_id: int, db: DbSession) -> None:
    """Delete item via raw SQL."""
    sql = load_sql("items_delete.sql")
    result = await db.execute(text(sql), {"id": item_id})
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
