"""The application-level conftest."""
import asyncio
from collections.abc import AsyncGenerator
from typing import Literal

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from app.database import async_session_maker


@pytest.fixture(autouse=True, scope="session")
def anyio_backend() -> Literal["asyncio"]:
    """Use asyncio as the async backend."""
    return "asyncio"


@pytest.fixture(autouse=True)
def test_db(mocker: MockerFixture) -> None:
    """Use the in-memory database for tests."""
    mocker.patch("app.database.SQLALCHEMY_DATABASE_URL", "sqlite+aiosqlite:///")


@pytest.fixture(scope="session")
def event_loop(
    request: pytest.FixtureRequest,
) -> AsyncGenerator[asyncio.AbstractEventLoop, None]:
    """
    Create an instance of the default event loop for a session.

    An event loop is destroyed at the end of the test session.
    https://docs.pytest.org/en/6.2.x/fixture.html#fixture-scopes
    """
    loop = asyncio.get_event_loop_policy().get_event_loop()
    try:
        yield loop
    finally:
        loop.close()


@pytest.fixture(scope="session")
async def test_db_connection() -> AsyncGenerator[AsyncConnection, None]:
    """Use the in-memory database for tests."""
    from app.database import Base, engine

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            yield conn
    finally:
        # for AsyncEngine created in function scope, close and
        # clean-up pooled connections
        await engine.dispose()


@pytest.fixture
async def test_db_session(
    test_db_connection: AsyncConnection,
) -> AsyncGenerator[AsyncSession, None]:
    """Use the in-memory database for tests."""
    async with async_session_maker() as session:
        try:
            async with session.begin():
                yield session
        finally:
            await session.flush()
            await session.rollback()
            await session.close()
