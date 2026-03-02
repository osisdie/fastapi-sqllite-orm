"""SQLModel async session."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import _async_session_factory


async def get_db_sm() -> AsyncGenerator[AsyncSession, None]:
    """Yield session for SQLModel (reuses shared engine)."""
    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


DbSessionSM = Annotated[AsyncSession, Depends(get_db_sm)]
