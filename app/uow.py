"""
The Unit of Work pattern implementation.

To learn more about the UoW, see:
https://www.cosmicpython.com/book/chapter_06_uow.html
"""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker


@asynccontextmanager
async def async_session_uow() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a transactional scope around a series of operations.

    :return: a UoW instance
    """
    async with async_session_maker() as session:
        async with session.begin():
            try:
                yield session
            finally:
                await session.rollback()
