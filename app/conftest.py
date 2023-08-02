"""The application-level conftest."""
import asyncio
from collections.abc import AsyncGenerator
from typing import Literal

import pytest
from dirty_equals import IsList
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from app.database import Dependency, Repo, async_session_maker
from app.factories import DependencyCreateDataFactory
from app.scraper.factories import SourceGraphRepoDataFactory
from app.scraper.models import SourceGraphRepoData


@pytest.fixture(autouse=True, scope="session")
def anyio_backend() -> Literal["asyncio"]:
    """Use asyncio as the async backend."""
    return "asyncio"


@pytest.fixture(autouse=True)
def _test_db(mocker: MockerFixture) -> None:
    """Use the in-memory database for tests."""
    mocker.patch("app.database.DB_PATH", "")


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


@pytest.fixture()
async def test_db_session(
    test_db_connection: AsyncConnection,
) -> AsyncGenerator[AsyncSession, None]:
    """Use the in-memory database for tests."""
    async with async_session_maker() as session:
        async with session.begin():
            try:
                yield session
            finally:
                await session.flush()
                await session.rollback()


@pytest.fixture()
async def some_repos(
    test_db_session: AsyncSession,
    source_graph_repo_data_factory: SourceGraphRepoDataFactory,
    dependency_create_data_factory: DependencyCreateDataFactory,
) -> list[Repo]:
    """Create some repos."""
    source_graph_repos_data: list[
        SourceGraphRepoData
    ] = source_graph_repo_data_factory.batch(10)
    assert source_graph_repos_data == IsList(length=10)
    repos = [
        Repo(
            url=str(source_graph_repo_data.repo_url),
            description=source_graph_repo_data.description,
            stars=source_graph_repo_data.stars,
            source_graph_repo_id=source_graph_repo_data.repo_id,
            dependencies=[
                Dependency(**dependency_create_data.model_dump())
                for dependency_create_data in dependency_create_data_factory.batch(5)
            ],
        )
        for source_graph_repo_data in source_graph_repos_data
    ]
    test_db_session.add_all(repos)
    await test_db_session.flush()
    await asyncio.gather(*[test_db_session.refresh(repo) for repo in repos])
    return repos
