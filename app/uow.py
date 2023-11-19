"""
The Unit of Work pattern implementation.

To learn more about the UoW, see:
https://www.cosmicpython.com/book/chapter_06_uow.html
"""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def async_session_uow(
    session: AsyncSession,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a transactional scope around a series of operations.

    :param session: The database session.
    :return: a UoW instance
    """
    async with session.begin():
        try:
            yield session
        finally:
            if session.in_transaction() and session.is_active:
                # session.is_active is True if this Session not in “partial rollback”
                # state. If this Session is within a transaction, and that transaction
                # has not been rolled back internally, the Session.is_active will also
                # be True.
                # https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.AsyncSession.is_active
                await session.rollback()
