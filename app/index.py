"""Create index.json file from database."""
import json
from pathlib import Path
from typing import Final

import aiofiles
import sqlalchemy.orm
import typer

from app.database import Repo
from app.models import RepoDetail
from app.uow import async_session_uow

#: The path to the index.json file.
INDEX_PATH: Final[Path] = Path(__file__).parent.parent / "index.json"


async def create_index() -> None:
    """
    Create index.json file from database.

    Creates an index which is going to be used by the frontend.
    :return: None
    """
    async with async_session_uow() as session, aiofiles.open(
        INDEX_PATH, "w"
    ) as index_file:
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


def main() -> None:
    """Create index.json file from database."""
    import asyncio

    asyncio.run(create_index())


if __name__ == "__main__":
    typer.run(main)
