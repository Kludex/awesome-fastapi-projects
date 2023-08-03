"""The logic for scraping the source graph data processing it."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.source_graph.client import AsyncSourceGraphSSEClient


async def scrape_source_graph_repos_data(
    session: AsyncSession, source_graph_client: AsyncSourceGraphSSEClient
) -> None:
    """Scrape source graph repos data."""
    async with source_graph_client:
        pass
