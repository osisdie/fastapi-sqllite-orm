"""ORM models for SQL CRUD example."""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Item(Base):
    """Simple item for CRUD."""

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    category: Mapped["Category | None"] = relationship("Category", back_populates="items")


class Category(Base):
    """Category with items (for N+1 demo). Uses default lazy='select' - access triggers query."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    items: Mapped[list["Item"]] = relationship("Item", back_populates="category")

    @property
    def item_count(self) -> int:
        """Triggers lazy load when accessed: SELECT * FROM items WHERE category_id=?."""
        return len(self.items)
