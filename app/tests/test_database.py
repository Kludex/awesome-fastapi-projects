"""Test the operations on the database models."""
import pytest
import sqlalchemy as sa
import sqlalchemy.orm
from dirty_equals import IsList
from sqlalchemy.ext.asyncio import AsyncSession

from app import database
from app.factories import DependencyCreateDataFactory
from app.models import DependencyCreateData
from app.source_graph.factories import SourceGraphRepoDataFactory
from app.source_graph.models import SourceGraphRepoData

pytestmark = pytest.mark.anyio


def _assert_repo_properties(
    repo: database.Repo, source_graph_repo_data: SourceGraphRepoData
) -> bool:
    """Assert that the repo has the expected properties."""
    assert repo.id is not None
    assert repo.url == str(source_graph_repo_data.repo_url)
    assert repo.description == source_graph_repo_data.description
    assert repo.stars == source_graph_repo_data.stars
    assert repo.source_graph_repo_id == source_graph_repo_data.repo_id
    return True


async def test_create_repo_no_dependencies(
    test_db_session: AsyncSession,
    source_graph_repo_data_factory: SourceGraphRepoDataFactory,
) -> None:
    """Test creating a repo."""
    source_graph_repo_data: SourceGraphRepoData = source_graph_repo_data_factory.build()
    repo = database.Repo(
        url=str(source_graph_repo_data.repo_url),
        description=source_graph_repo_data.description,
        stars=source_graph_repo_data.stars,
        source_graph_repo_id=source_graph_repo_data.repo_id,
    )
    test_db_session.add(repo)
    await test_db_session.flush()
    await test_db_session.refresh(repo)
    _assert_repo_properties(repo, source_graph_repo_data)
    assert (await repo.awaitable_attrs.dependencies) == IsList(length=0)


async def test_create_repo_with_dependencies(
    test_db_session: AsyncSession,
    source_graph_repo_data_factory: SourceGraphRepoDataFactory,
    dependency_create_data_factory: DependencyCreateDataFactory,
) -> None:
    """Test creating a repo with dependencies."""
    source_graph_repo_data: SourceGraphRepoData = source_graph_repo_data_factory.build()
    dependencies_create_data: list[
        DependencyCreateData
    ] = dependency_create_data_factory.batch(5)
    repo = database.Repo(
        url=str(source_graph_repo_data.repo_url),
        description=source_graph_repo_data.description,
        stars=source_graph_repo_data.stars,
        source_graph_repo_id=source_graph_repo_data.repo_id,
        dependencies=[
            database.Dependency(**dependency_create_data.model_dump())
            for dependency_create_data in dependencies_create_data
        ],
    )
    test_db_session.add(repo)
    await test_db_session.flush()
    await test_db_session.refresh(repo)
    _assert_repo_properties(repo, source_graph_repo_data)
    repo_dependencies = await repo.awaitable_attrs.dependencies
    assert repo_dependencies == IsList(length=5)
    assert all(
        repo_dependency.name == dependency.name
        for repo_dependency, dependency in zip(
            repo_dependencies, dependencies_create_data, strict=True
        )
    )


async def test_list_repositories(
    test_db_session: AsyncSession,
    some_repos: list[database.Repo],
) -> None:
    """Test listing repositories."""
    repos_from_db_result = await test_db_session.execute(
        sa.select(database.Repo).options(
            sqlalchemy.orm.joinedload(database.Repo.dependencies)
        )
    )
    repos_from_db = repos_from_db_result.scalars().unique().all()
    assert repos_from_db == IsList(length=10)
    assert all(
        repo.id == repo_data.id
        and all(
            repo_dependency.name == dependency.name
            for repo_dependency, dependency in zip(
                repo.dependencies, repo_data.dependencies, strict=True
            )
        )
        for repo, repo_data in zip(repos_from_db, some_repos, strict=True)
    )
