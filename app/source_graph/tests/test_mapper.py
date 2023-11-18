"""The tests for the source graph mapper to the database objects."""

import pytest
import sqlalchemy
from dirty_equals import IsInstance, IsList
from sqlalchemy.ext.asyncio import AsyncSession

from app import database
from app.source_graph.factories import SourceGraphRepoDataFactory
from app.source_graph.mapper import create_or_update_repos_from_source_graph_repos_data
from app.source_graph.models import SourceGraphRepoData

pytestmark = pytest.mark.anyio


async def test_create_or_update_repos_from_source_graph_repos_data(
    db_session: AsyncSession,
    source_graph_repo_data_factory: SourceGraphRepoDataFactory,
) -> None:
    """Test creating repos from source graph repos data."""
    source_graph_repo_data: list[
        SourceGraphRepoData
    ] = source_graph_repo_data_factory.batch(5)
    repos = await create_or_update_repos_from_source_graph_repos_data(
        db_session, source_graph_repo_data
    )
    assert repos == IsList(length=5)
    assert all(repo == IsInstance[database.Repo] for repo in repos)
    assert all(repo.id is not None for repo in repos)


async def test_create_or_update_repos_from_source_graph_repos_data_update(
    some_repos: list[database.Repo],
    db_session: AsyncSession,
    source_graph_repo_data_factory: SourceGraphRepoDataFactory,
) -> None:
    """Test updating repos from source graph repos data."""
    assert (
        await db_session.execute(
            sqlalchemy.select(sqlalchemy.func.count(database.Repo.id))
        )
    ).scalar() == len(some_repos)
    source_graph_repos_data: list[
        SourceGraphRepoData
    ] = source_graph_repo_data_factory.batch(len(some_repos))
    source_graph_repos_data = [
        SourceGraphRepoData(
            **(
                repo_data.model_dump(by_alias=True)
                | {"repositoryID": repo.source_graph_repo_id}
            )
        )
        for repo, repo_data in zip(some_repos, source_graph_repos_data, strict=True)
    ]
    repos = await create_or_update_repos_from_source_graph_repos_data(
        db_session, source_graph_repos_data
    )
    assert repos == IsList(length=len(some_repos))
    assert all(repo == IsInstance[database.Repo] for repo in repos)
    assert all(repo.id is not None for repo in repos)
    assert (
        await db_session.execute(
            sqlalchemy.select(sqlalchemy.func.count(database.Repo.id))
        )
    ).scalar() == len(some_repos)
