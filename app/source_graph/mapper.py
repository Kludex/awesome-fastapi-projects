"""Mapper for source graph models to the database objects."""
from collections.abc import Sequence

import sqlalchemy.dialects.sqlite
from sqlalchemy.ext.asyncio import AsyncSession

from app import database
from app.source_graph.models import SourceGraphRepoData


async def create_or_update_repos_from_source_graph_repos_data(
    session: AsyncSession, source_graph_repos_data: Sequence[SourceGraphRepoData]
) -> Sequence[database.Repo]:
    """
    Create repos from source graph repos data.

    If any repos already exist, update them.

    :param session: The database session.
    :param source_graph_repos_data: The source graph repos data.
    """
    insert_statement = sqlalchemy.dialects.sqlite.insert(database.Repo)
    update_statement = insert_statement.on_conflict_do_update(
        index_elements=[database.Repo.source_graph_repo_id],
        set_={
            "url": insert_statement.excluded.url,
            "description": insert_statement.excluded.description,
            "stars": insert_statement.excluded.stars,
            "source_graph_repo_id": insert_statement.excluded.source_graph_repo_id,
        },
    )

    return (
        await session.scalars(
            update_statement.returning(database.Repo),
            [
                {
                    "url": str(repo_data.repo_url),
                    "description": repo_data.description,
                    "stars": repo_data.stars,
                    "source_graph_repo_id": repo_data.repo_id,
                }
                for repo_data in source_graph_repos_data
            ],
        )
    ).all()
