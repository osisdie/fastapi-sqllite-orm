"""SQLModel ORM models."""

from sqlmodel import Field, Relationship, SQLModel


class CategorySM(SQLModel, table=True):
    """SQLModel Category (N+1 demo). Uses default lazy load - access triggers query."""

    __tablename__ = "sqlmodel_categories"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    items: list["ItemSM"] = Relationship(back_populates="category")

    @property
    def item_count(self) -> int:
        """Triggers lazy load when accessed: SELECT * FROM sqlmodel_items WHERE category_id=?."""
        return len(self.items)


class ItemSM(SQLModel, table=True):
    """SQLModel Item."""

    __tablename__ = "sqlmodel_items"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    category_id: int | None = Field(default=None, foreign_key="sqlmodel_categories.id")
    category: CategorySM | None = Relationship(back_populates="items")
