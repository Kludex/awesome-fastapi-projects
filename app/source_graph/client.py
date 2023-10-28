"""The client for the SourceGraph API."""
import asyncio
from collections.abc import AsyncGenerator, Mapping, MutableMapping
from contextlib import asynccontextmanager
from datetime import timedelta
from types import TracebackType
from typing import Any, Final, Self
from urllib.parse import quote

import httpx
import stamina
from httpx_sse import EventSource, ServerSentEvent, aconnect_sse
from loguru import logger

from app.source_graph.models import SourceGraphRepoData, SourceGraphRepoDataListAdapter

#: The URL of the SourceGraph SSE API.
SOURCE_GRAPH_STREAM_API_URL: Final[str] = "https://sourcegraph.com/.api/search/stream"


#: The query parameters for the SourceGraph SSE API.
FASTAPI_REPOS_QUERY_PARAMS: Final[Mapping[str, str]] = {
    "q": quote(
        " ".join(
            [
                "repo:has.content(from fastapi import FastApi)",
                "type:repo",
                "visibility:public",
                "archived:no",
                "fork:no",
            ]
        )
    ),
}


class AsyncSourceGraphSSEClient:
    """
    A client for the SourceGraph SSE API.

    To learn more about the underlying API, see the ``SourceGraph SSE API``
    https://docs.sourcegraph.com/api/stream_api#sourcegraph-stream-api
    """

    def __init__(self: Self) -> None:
        """Initialize the client."""
        self._last_event_id: str | None = None
        self._reconnection_delay: float = 0.0
        self._aclient: httpx.AsyncClient = httpx.AsyncClient()

    async def __aenter__(self: Self) -> Self:
        """Enter the async context manager."""
        await self._aclient.__aenter__()
        return self

    async def __aexit__(
        self: Self,
        exc_type: type[BaseException] | None = None,
        exc_val: BaseException | None = None,
        exc_tb: TracebackType | None = None,
    ) -> None:
        """Exit the async context manager."""
        return await self._aclient.__aexit__(exc_type, exc_val, exc_tb)

    @asynccontextmanager
    async def _aconnect_sse(
        self: Self, **kwargs: MutableMapping[str, Any]
    ) -> AsyncGenerator[EventSource, None]:
        """Connect to the SourceGraph SSE API."""
        headers = kwargs.pop("headers", {})
        if self._last_event_id is not None:
            headers["Last-Event-ID"] = self._last_event_id
        async with aconnect_sse(
            client=self._aclient,
            url=str(SOURCE_GRAPH_STREAM_API_URL),
            method="GET",
            headers=headers,
            **kwargs,
        ) as event_source:
            yield event_source

    async def _aiter_sse(
        self: Self, **kwargs: MutableMapping[str, Any]
    ) -> AsyncGenerator[ServerSentEvent, None]:
        """Iterate over the SourceGraph SSE API."""
        async with self._aconnect_sse(**kwargs) as event_source:
            async for event in event_source.aiter_sse():
                yield event

    async def _aiter_sse_with_retries(
        self: Self, **kwargs: MutableMapping[str, Any]
    ) -> AsyncGenerator[ServerSentEvent, None]:
        """Iterate over the SourceGraph SSE API with retries."""
        async for attempt in stamina.retry_context(
            on=(httpx.ReadError, httpx.ReadTimeout)
        ):
            with attempt:
                await asyncio.sleep(self._reconnection_delay)
                async for event in self._aiter_sse(**kwargs):
                    self._last_event_id = event.id
                    if event.retry is not None:
                        logger.error(
                            "Received a retry event from the SourceGraph SSE API. "
                            "Schedule a reconnection in {retry} milliseconds.",
                            retry=event.retry,
                            enqueue=True,
                        )
                        self._reconnection_delay = timedelta(
                            milliseconds=event.retry
                        ).total_seconds()
                    else:
                        self._reconnection_delay = 0.0
                    yield event

    async def aiter_fastapi_repos(
        self: Self,
    ) -> AsyncGenerator[list[SourceGraphRepoData], None]:
        """Iterate over the SourceGraph SSE API with retries."""
        async for event in self._aiter_sse_with_retries(
            params=dict(FASTAPI_REPOS_QUERY_PARAMS)
        ):
            if event.event == "matches":
                yield SourceGraphRepoDataListAdapter.validate_python(event.json())
