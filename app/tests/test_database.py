"""Test the operations on the database models."""
import pytest
from dirty_equals import IsList
from sqlalchemy.ext.asyncio import AsyncSession

from app import database
from app.factories import RepoCreateDataFactory

pytestmark = pytest.mark.anyio


async def test_create_repo_no_dependencies(
    test_db_session: AsyncSession, repo_create_data_factory: RepoCreateDataFactory
) -> None:
    """Test creating a repo."""
    repo_create_data = repo_create_data_factory.build()
    repo = database.Repo(url=str(repo_create_data.url))
    test_db_session.add(repo)
    await test_db_session.flush()
    await test_db_session.refresh(repo)
    assert repo.id is not None
    assert repo.url == str(repo_create_data.url)
    assert (await repo.awaitable_attrs.dependencies) == []


async def test_create_repo_with_dependencies(
    test_db_session: AsyncSession, repo_create_data_factory: RepoCreateDataFactory
) -> None:
    """Test creating a repo with dependencies."""
    repo_create_data = repo_create_data_factory.build()
    repo = database.Repo(
        url=str(repo_create_data.url),
        dependencies=[
            database.Dependency(name=dependency.name)
            for dependency in repo_create_data.dependencies
        ],
    )
    test_db_session.add(repo)
    await test_db_session.flush()
    await test_db_session.refresh(repo)
    assert repo.id is not None
    assert repo.url == str(repo_create_data.url)
    repo_dependencies = await repo.awaitable_attrs.dependencies
    assert 2 <= len(repo_dependencies) <= 5
    assert repo_dependencies == IsList(length=len(repo_create_data.dependencies))
    assert all(
        repo_dependency.name == dependency.name
        for repo_dependency, dependency in zip(
            repo_dependencies, repo_create_data.dependencies, strict=True
        )
    )
