"""The client for the SourceGraph API."""
from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Any, AnyStr, Final, Self
from urllib.parse import quote

import httpx
import stamina
from httpx_sse import EventSource, ServerSentEvent, aconnect_sse
from pydantic import HttpUrl

#: The URL of the SourceGraph SSE API.
SOURCE_GRAPH_STREAM_API_URL: Final[
    HttpUrl
] = "https://sourcegraph.com/.api/search/stream"


class AsyncSourceGraphSSEClient:
    """A client for the SourceGraph SSE API."""

    def __init__(self: Self) -> None:
        """Initialize the client."""
        self._last_event_id: str | None = None
        self._reconnection_delay: float = 0.0
        self._aclient: httpx.AsyncClient = httpx.AsyncClient()

    @asynccontextmanager
    async def _aconnect_sse(
        self: Self, **kwargs: Mapping[AnyStr, Any]
    ) -> AsyncGenerator[EventSource, None]:
        """Connect to the SourceGraph SSE API."""
        headers = kwargs.pop("headers", {})
        if self._last_event_id is not None:
            headers["Last-Event-ID"] = self._last_event_id
        async with aconnect_sse(
            client=self._aclient,
            url=SOURCE_GRAPH_STREAM_API_URL,
            method="GET",
            headers=headers,
            **kwargs,
        ) as event_source:
            yield event_source

    async def _aiter_sse(
        self: Self, **kwargs: Mapping[AnyStr, Any]
    ) -> AsyncGenerator[ServerSentEvent, None]:
        """Iterate over the SourceGraph SSE API."""
        async with self._aconnect_sse(**kwargs) as event_source:
            async for event in event_source.aiter_sse():
                yield event

    async def _aiter_sse_with_retries(
        self: Self, **kwargs: Mapping[AnyStr, Any]
    ) -> AsyncGenerator[ServerSentEvent, None]:
        """Iterate over the SourceGraph SSE API with retries."""
        async for attempt in stamina.retry_context(
            on=httpx.ReadError, wait_initial=max(self._reconnection_delay, 0.1)
        ):
            with attempt:
                async for event in self._aiter_sse(**kwargs):
                    self._last_event_id = event.id
                    if event.retry is not None:
                        self._reconnection_delay = timedelta(
                            milliseconds=event.retry
                        ).total_seconds()
                    yield event

    async def aiter_fastapi_repos(self: Self) -> AsyncGenerator[ServerSentEvent, None]:
        """Iterate over the SourceGraph SSE API with retries."""
        params = {
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
        async for event in self._aiter_sse_with_retries(params=params):
            yield event
