"""The logic for scraping the source graph data processing it."""
import asyncio

import sqlalchemy.dialects.sqlite
import typer
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Dependency, Repo, RepoDependency
from app.dependencies import acquire_dependencies_data_for_repository
from app.source_graph.client import AsyncSourceGraphSSEClient
from app.source_graph.mapper import create_or_update_repos_from_source_graph_repos_data
from app.types import RepoId
from app.uow import async_session_uow


async def _create_dependencies_for_repo(session: AsyncSession, repo: Repo) -> None:
    """
    Create dependencies for a repo.

    For each parsed dependency, creates a new record in the database, if such a
    dependency does not exist.
    Then, assigns the dependencies to the given repo.

    :param session: An asynchronous session object
    :param repo: A repo for which to create and assign the dependencies
    """
    # Acquire the dependencies data for the repo
    logger.info(
        "Acquiring the dependencies data for the repo with id {repo_id}.",
        repo_id=repo.id,
        enqueue=True,
    )
    try:
        (
            revision,
            dependencies_create_data,
        ) = await acquire_dependencies_data_for_repository(repo)
    except RuntimeError:
        # If the parsing fails,
        # just skip creating the dependencies
        logger.error(
            "Failed to acquire the dependencies data for the repo with id {repo_id}.",
            enqueue=True,
        )
        return
    if repo.last_checked_revision == revision:
        # If the repo has already been updated,
        # just skip creating the dependencies
        logger.info(
            "The repo with id {repo_id} has fresh dependencies.",
            repo_id=repo.id,
            enqueue=True,
        )
        return
    if not dependencies_create_data:
        # If there are no dependencies,
        # just skip creating the dependencies
        logger.info(
            "The repo with id {repo_id} has no dependencies.",
            repo_id=repo.id,
            enqueue=True,
        )
        return
    # Update the repo with the revision hash
    logger.info(
        "Updating the repo with id {repo_id} with the revision hash {revision}.",
        repo_id=repo.id,
        revision=revision,
        enqueue=True,
    )
    update_repo_statement = (
        sqlalchemy.update(Repo)
        .where(Repo.id == repo.id)
        .values(last_checked_revision=revision)
    )
    await session.execute(update_repo_statement)
    # Create dependencies - on conflict do nothing.
    # This is to avoid creating duplicate dependencies.
    logger.info(
        "Creating the dependencies for the repo with id {repo_id}.",
        repo_id=repo.id,
        enqueue=True,
    )
    insert_dependencies_statement = sqlalchemy.dialects.sqlite.insert(
        Dependency
    ).on_conflict_do_nothing(index_elements=[Dependency.name])
    await session.execute(
        insert_dependencies_statement.returning(Dependency),
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
    insert_repo_dependencies_statement = sqlalchemy.dialects.sqlite.insert(
        RepoDependency
    ).on_conflict_do_nothing([RepoDependency.repo_id, RepoDependency.dependency_id])
    await session.execute(
        insert_repo_dependencies_statement,
        [
            {
                "repo_id": repo.id,
                "dependency_id": dependency.id,
            }
            for dependency in dependencies
        ],
    )


async def scrape_source_graph_repos() -> None:
    """
    Iterate over the source graph repos and create or update them in the database.

    :return: None
    """
    async with AsyncSourceGraphSSEClient() as sg_client:
        async with async_session_uow() as session:
            async with asyncio.TaskGroup() as tg:
                logger.info(
                    "Creating or updating repos from source graph repos data.",
                    enqueue=True,
                )
                async for sg_repos_data in sg_client.aiter_fastapi_repos():
                    logger.info(
                        "Received {count} repos.",
                        count=len(sg_repos_data),
                        enqueue=True,
                    )
                    tg.create_task(
                        create_or_update_repos_from_source_graph_repos_data(
                            session=session,
                            source_graph_repos_data=sg_repos_data,
                        )
                    )
            await session.commit()


async def parse_dependencies_for_repo(
    semaphore: asyncio.Semaphore, repo_id: RepoId
) -> None:
    """
    Parse the dependencies for a given repo and create them in the database.

    :param semaphore: A semaphore to limit the number of concurrent requests
    :param repo_id: The id of the repo for which to parse the dependencies
    :return: None
    """
    async with async_session_uow() as session, semaphore:
        # Fetch the repo from the database
        logger.info(
            "Fetching the repo with id {repo_id}.", repo_id=repo_id, enqueue=True
        )
        repo = (
            await session.scalars(sqlalchemy.select(Repo).where(Repo.id == repo_id))
        ).one()
        # Create the dependencies for the repo
        logger.info(
            "Creating the dependencies for the repo with id {repo_id}.",
            repo_id=repo_id,
            enqueue=True,
        )
        await _create_dependencies_for_repo(session=session, repo=repo)
        await session.commit()


async def parse_dependencies_for_repos() -> None:
    """
    Parse the dependencies for all the repos in the database.

    :return: None.
    """
    logger.info("Fetching the repos from the database.", enqueue=True)
    async with async_session_uow() as session:
        repo_ids = (
            await session.scalars(
                sqlalchemy.select(Repo.id).order_by(
                    Repo.last_checked_revision.is_(None).desc()
                )
            )
        ).all()
        logger.info("Fetched {count} repos.", count=len(repo_ids), enqueue=True)
    logger.info("Parsing the dependencies for the repos.", enqueue=True)
    semaphore = asyncio.Semaphore(10)
    async with asyncio.TaskGroup() as tg:
        for repo_id in repo_ids:
            logger.info(
                "Parsing the dependencies for repo {repo_id}.",
                repo_id=repo_id,
                enqueue=True,
            )
            tg.create_task(
                parse_dependencies_for_repo(
                    semaphore=semaphore, repo_id=RepoId(repo_id)
                )
            )


app = typer.Typer()


@app.command()
def scrape_repos() -> None:
    """
    Scrape the FastAPI-related repositories utilizing the source graph API.

    :return: None
    """
    logger.info("Scraping the source graph repos.", enqueue=True)
    asyncio.run(scrape_source_graph_repos())


@app.command()
def parse_dependencies() -> None:
    """
    Parse the dependencies for all the repos in the database.

    :return: None.
    """
    logger.info(
        "Parsing the dependencies for all the repos in the database.", enqueue=True
    )
    asyncio.run(parse_dependencies_for_repos())


if __name__ == "__main__":
    app()
