"""The logic for scraping the source graph data processing it."""
import asyncio

import sqlalchemy.dialects.sqlite
import typer
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Dependency, Repo, RepoDependency, async_session_maker
from app.dependencies import acquire_dependencies_data_for_repository
from app.source_graph.client import AsyncSourceGraphSSEClient
from app.source_graph.mapper import create_or_update_repos_from_source_graph_repos_data
from app.source_graph.models import SourceGraphRepoData
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
            repo_id=repo.id,
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


async def _save_scraped_repos_from_source_graph_repos_data(
    source_graph_repos_data: list[SourceGraphRepoData],
) -> None:
    """
    Save the scraped repos from the source graph repos data.

    .. note::
        This function is meant to be used in a task group.
        From the SQLAlchemy documentation:
        ::
            https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#using-asyncsession-with-concurrent-tasks

            The AsyncSession object is a mutable, stateful object
            which represents a single, stateful database
            transaction in progress. Using concurrent tasks with asyncio,
            with APIs such as asyncio.gather() for example, should use
            a separate AsyncSession per individual task.


    :param source_graph_repos_data: The source graph repos data.
    :return: None
    """  # noqa: E501
    async with async_session_maker() as session, async_session_uow(session):
        saved_repos = await create_or_update_repos_from_source_graph_repos_data(
            session=session,
            source_graph_repos_data=source_graph_repos_data,
        )
        logger.info(
            "Saving {count} repos.",
            count=len(saved_repos),
            enqueue=True,
        )
        await session.commit()


async def scrape_source_graph_repos() -> None:
    """
    Iterate over the source graph repos and create or update them in the database.

    :return: None
    """
    async with AsyncSourceGraphSSEClient() as sg_client, asyncio.TaskGroup() as tg:
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
                _save_scraped_repos_from_source_graph_repos_data(
                    source_graph_repos_data=sg_repos_data
                )
            )


async def parse_dependencies_for_repo(semaphore: asyncio.Semaphore, repo: Repo) -> None:
    """
    Parse the dependencies for a given repo and create them in the database.

    .. note::
        This function is meant to be used in a task group.
        From the SQLAlchemy documentation:
        ::
            https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#using-asyncsession-with-concurrent-tasks

            The AsyncSession object is a mutable, stateful object
            which represents a single, stateful database
            transaction in progress. Using concurrent tasks with asyncio,
            with APIs such as asyncio.gather() for example, should use
            a separate AsyncSession per individual task.


    :param semaphore: A semaphore to limit the number of concurrent requests
    :param repo: A repo for which to create and assign the dependencies
    :return: None
    """  # noqa: E501
    async with semaphore, async_session_maker() as session, async_session_uow(session):
        # Associate the repo object with a fresh session instance
        repo = await session.merge(repo)
        # Create the dependencies for the repo
        logger.info(
            "Creating the dependencies for the repo with id {repo_id}.",
            repo_id=repo.id,
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
    async with async_session_maker() as session:
        repos = (
            await session.scalars(
                sqlalchemy.select(Repo).order_by(
                    Repo.last_checked_revision.is_(None).desc()
                )
            )
        ).all()
    logger.info("Fetched {count} repos.", count=len(repos), enqueue=True)
    logger.info("Parsing the dependencies for the repos.", enqueue=True)
    semaphore = asyncio.Semaphore(10)
    async with asyncio.TaskGroup() as tg:
        for repo in repos:
            logger.info(
                "Parsing the dependencies for repo {repo_id}.",
                repo_id=repo.id,
                enqueue=True,
            )
            tg.create_task(parse_dependencies_for_repo(semaphore=semaphore, repo=repo))


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
