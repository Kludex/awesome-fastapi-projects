"""Mapper for scraper."""
from collections.abc import Sequence

import sqlalchemy.sql
from sqlalchemy.ext.asyncio import AsyncSession

from app import database
from app.scraper.models import SourceGraphRepoData


async def create_repos_from_source_graph_repos_data(
    session: AsyncSession, source_graph_repo_data: Sequence[SourceGraphRepoData]
) -> Sequence[database.Repo]:
    """Create repos from source graph repos data."""
    return (
        await session.scalars(
            sqlalchemy.sql.insert(database.Repo).returning(database.Repo),
            [
                {
                    "url": str(repo_data.repo_url),
                    "description": repo_data.description,
                    "stars": repo_data.stars,
                    "source_graph_repo_id": repo_data.repo_id,
                }
                for repo_data in source_graph_repo_data
            ],
        )
    ).all()
