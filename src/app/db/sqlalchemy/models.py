"""SQLAlchemy ORM models."""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ItemSA(Base):
    """SQLAlchemy Item model."""

    __tablename__ = "sqlalchemy_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("sqlalchemy_categories.id"), nullable=True)
    category: Mapped["CategorySA | None"] = relationship("CategorySA", back_populates="items")


class CategorySA(Base):
    """SQLAlchemy Category model (N+1 demo). Uses default lazy='select' - access triggers query."""

    __tablename__ = "sqlalchemy_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    items: Mapped[list["ItemSA"]] = relationship("ItemSA", back_populates="category")

    @property
    def item_count(self) -> int:
        """Triggers lazy load when accessed: SELECT * FROM sqlalchemy_items WHERE category_id=?."""
        return len(self.items)
