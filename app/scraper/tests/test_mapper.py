"""The tests for the scraper mapper."""
import pytest
from dirty_equals import IsInstance, IsList
from sqlalchemy.ext.asyncio import AsyncSession

from app import database
from app.scraper.factories import SourceGraphRepoDataFactory
from app.scraper.mapper import create_repos_from_source_graph_repos_data
from app.scraper.models import SourceGraphRepoData

pytestmark = pytest.mark.anyio


async def test_create_repos_from_source_graph_repos_data(
    test_db_session: AsyncSession,
    source_graph_repo_data_factory: SourceGraphRepoDataFactory,
) -> None:
    """Test creating repos from source graph repos data."""
    source_graph_repo_data: list[
        SourceGraphRepoData
    ] = source_graph_repo_data_factory.batch(5)
    repos = await create_repos_from_source_graph_repos_data(
        test_db_session, source_graph_repo_data
    )
    assert repos == IsList(length=5)
    assert all(
        repo == IsInstance[database.Repo] for repo in repos  # type: ignore[type-var]
    )
    assert all(repo.id is not None for repo in repos)
