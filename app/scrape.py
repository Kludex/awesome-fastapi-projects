"""The logic for scraping the source graph data processing it."""
import asyncio

import sqlalchemy.dialects.sqlite
import typer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Dependency, Repo, RepoDependency
from app.dependencies import acquire_dependencies_data_for_repository
from app.source_graph.client import AsyncSourceGraphSSEClient
from app.source_graph.mapper import create_or_update_repos_from_source_graph_repos_data
from app.uow import async_session_uow


async def _create_dependencies_for_repo(session: AsyncSession, repo: Repo) -> None:
    """
    Create dependencies for a repo.

    For each dependency, create a dependency object and add it to the repo.
    """
    try:
        dependencies_create_data = await acquire_dependencies_data_for_repository(repo)
    except RuntimeError:
        return
    # Create dependencies - on conflict do nothing.
    insert_statement = sqlalchemy.dialects.sqlite.insert(
        Dependency
    ).on_conflict_do_nothing(index_elements=[Dependency.name])
    await session.execute(
        insert_statement.returning(Dependency),
        [
            {
                "name": dependency_data.name,
            }
            for dependency_data in dependencies_create_data
        ],
    )
    # Re-fetch the dependencies from the database
    dependencies = (
        await session.scalars(
            sqlalchemy.select(Dependency).where(
                Dependency.name.in_(
                    [
                        dependency_data.name
                        for dependency_data in dependencies_create_data
                    ]
                )
            )
        )
    ).all()
    # Add the dependencies to the repo
    repo_dependencies_insert_statement = sqlalchemy.dialects.sqlite.insert(
        RepoDependency
    ).on_conflict_do_nothing([RepoDependency.repo_id, RepoDependency.dependency_id])
    await session.execute(
        repo_dependencies_insert_statement,
        [
            {
                "repo_id": repo.id,
                "dependency_id": dependency.id,
            }
            for dependency in dependencies
        ],
    )


async def scrape_source_graph_repos_data() -> None:
    """Scrape source graph repos data."""
    async with AsyncSourceGraphSSEClient() as source_graph_client:
        async for source_graph_repos_data in source_graph_client.aiter_fastapi_repos():
            async with async_session_uow() as session:
                repos = await create_or_update_repos_from_source_graph_repos_data(
                    session=session,
                    source_graph_repos_data=source_graph_repos_data,
                )
                async with asyncio.TaskGroup() as tg:
                    for repo in repos:
                        tg.create_task(
                            _create_dependencies_for_repo(session=session, repo=repo)
                        )
                await session.commit()


def main() -> None:
    """Scrape the FastAPI-related repositories utilizing the source graph API."""
    asyncio.run(scrape_source_graph_repos_data())


if __name__ == "__main__":
    """Run the scraping."""
    typer.run(main)
