"""The application-level conftest."""
import asyncio
import contextlib
from collections.abc import AsyncGenerator, Generator
from typing import Literal

import pytest
import stamina
from dirty_equals import IsList
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database import Dependency, Repo
from app.factories import DependencyCreateDataFactory
from app.source_graph.factories import SourceGraphRepoDataFactory
from app.source_graph.models import SourceGraphRepoData


@pytest.fixture(autouse=True, scope="session")
def anyio_backend() -> Literal["asyncio"]:
    """Use asyncio as the async backend."""
    return "asyncio"


@pytest.fixture(autouse=True, scope="session")
def _deactivate_retries() -> None:
    """Deactivate stamina retries."""
    stamina.set_active(False)


@pytest.fixture(scope="session")
def db_path() -> str:
    """Use the in-memory database for tests."""
    return ""  # ":memory:"


@pytest.fixture(scope="session")
def db_connection_string(
    db_path: str,
) -> str:
    """Provide the connection string for the in-memory database."""
    return f"sqlite+aiosqlite:///{db_path}"


@pytest.fixture(scope="session", params=[{"echo": False}], ids=["echo=False"])
async def db_engine(
    db_connection_string: str,
    request: pytest.FixtureRequest,
) -> AsyncGenerator[AsyncEngine, None, None]:
    """Create the database engine."""
    # echo=True enables logging of all SQL statements
    # https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine.params.echo
    engine = create_async_engine(
        db_connection_string,
        **request.param,  # type: ignore
    )
    try:
        yield engine
    finally:
        # for AsyncEngine created in function scope, close and
        # clean-up pooled connections
        await engine.dispose()


@pytest.fixture(scope="session")
def event_loop(
    request: pytest.FixtureRequest,
) -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Create an instance of the default event loop for a session.

    An event loop is destroyed at the end of the test session.
    https://docs.pytest.org/en/6.2.x/fixture.html#fixture-scopes
    """
    with contextlib.closing(loop := asyncio.get_event_loop_policy().get_event_loop()):
        yield loop


@pytest.fixture(scope="session")
async def _database_objects(
    db_engine: AsyncEngine,
) -> AsyncGenerator[None, None]:
    """Create the database objects (tables, etc.)."""
    from app.database import Base

    # Enters a transaction
    # https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.AsyncConnection.begin
    try:
        async with db_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        yield
    finally:
        # Clean up after the testing session is over
        async with db_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def db_connection(
    db_engine: AsyncEngine,
) -> AsyncGenerator[AsyncConnection, None]:
    """Create a database connection."""
    # Return connection with no transaction
    # https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.AsyncEngine.connect
    async with db_engine.connect() as conn:
        yield conn


@pytest.fixture()
async def db_session(
    db_engine: AsyncEngine,
    _database_objects: None,
) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session."""
    # The `async_sessionmaker` function is used to create a Session factory
    # https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.async_sessionmaker
    async_session_factory = async_sessionmaker(
        db_engine, expire_on_commit=False, autoflush=False, autocommit=False
    )
    async with async_session_factory() as session:
        yield session


@pytest.fixture()
async def db_uow(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional scope around a series of operations."""
    from app.uow import async_session_uow

    # This context manager will start a transaction, and roll it back at the end
    # https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.AsyncSessionTransaction
    async with async_session_uow(db_session) as session:
        yield session


@pytest.fixture()
async def some_repos(
    db_session: AsyncSession,
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
    db_session.add_all(repos)
    await db_session.flush()
    return repos
