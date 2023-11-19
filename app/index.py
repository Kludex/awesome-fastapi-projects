"""
Create repos and dependencies indexes.

This script creates can create two indexes:

- ``repos_index.json``: Contains all the repositories and their dependencies.
- ``dependencies_index.json``: Contains all the dependencies and the
    repositories that depend on them.

The indexes are used by the frontend to display the data and perform searches.
"""
import asyncio
import json
from pathlib import Path
from typing import Final

import aiofiles
import sqlalchemy.orm
import typer

from app.database import Dependency, Repo, async_session_maker
from app.models import DependencyDetail, RepoDetail
from app.uow import async_session_uow

#: The path to the repos index file.
REPOS_INDEX_PATH: Final[Path] = Path(__file__).parent.parent / "repos_index.json"
#: The path to the dependencies index file.
DEPENDENCIES_INDEX_PATH: Final[Path] = (
    Path(__file__).parent.parent / "dependencies_index.json"
)

app = typer.Typer()


async def create_repos_index() -> None:
    """
    Create repos_index.json file from database.

    :return: None
    """
    async with async_session_maker() as session, async_session_uow(
        session
    ), aiofiles.open(REPOS_INDEX_PATH, "w") as index_file:
        await index_file.write(
            json.dumps(
                {
                    "repos": [
                        RepoDetail.model_validate(repo).model_dump()
                        async for repo in (
                            await session.stream_scalars(
                                sqlalchemy.select(Repo)
                                .order_by(Repo.id)
                                .options(sqlalchemy.orm.selectinload(Repo.dependencies))
                            )
                        )
                    ],
                },
                indent=4,
            )
        )


async def create_dependencies_index() -> None:
    """
    Create dependencies_index.json file from database.

    :return: None
    """
    async with async_session_maker() as session, async_session_uow(
        session
    ) as session, aiofiles.open(DEPENDENCIES_INDEX_PATH, "w") as index_file:
        dependencies = [
            DependencyDetail.model_validate(dependency).model_dump()
            async for dependency in (
                await session.stream_scalars(
                    sqlalchemy.select(Dependency).order_by(Dependency.id)
                )
            )
            if dependency.name
        ]
        await index_file.write(
            json.dumps(
                {
                    "dependencies": dependencies,
                },
                indent=4,
            )
        )


@app.command()
def index_repos() -> None:
    """Create ``repos_index.json``."""
    asyncio.run(create_repos_index())


@app.command()
def index_dependencies() -> None:
    """Create ``dependencies_index.json``."""
    asyncio.run(create_dependencies_index())


if __name__ == "__main__":
    app()
