"""Test the operations on the database models."""
import pytest
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
    await test_db_session.commit()
    await test_db_session.refresh(repo)
    assert repo.id is not None
    assert repo.url == str(repo_create_data.url)
    assert (await repo.awaitable_attrs.dependencies) == []
