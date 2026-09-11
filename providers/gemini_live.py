"""Gemini Live adapter.

This is deliberately the only provider module that knows about google-genai's
Live API. The rest of JARVIS should depend on the realtime contract instead of
constructing Gemini sessions directly.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from google import genai
from google.genai import types


class GeminiLiveSession:
    def __init__(self, session: Any):
        self._session = session

    async def send_audio(self, data: bytes, mime_type: str = "audio/pcm") -> None:
        await self._session.send_realtime_input(
            audio=types.Blob(data=data, mime_type=mime_type)
        )

    def receive(self) -> AsyncIterator[Any]:
        return self._session.receive()

    async def send_text(self, text: str, *, turn_complete: bool = True) -> None:
        await self._session.send_client_content(
            turns={"role": "user", "parts": [{"text": text}]},
            turn_complete=turn_complete,
        )

    async def send_tool_response(self, function_responses: list[Any]) -> None:
        await self._session.send_tool_response(
            function_responses=function_responses
        )

    def __getattr__(self, name: str) -> Any:
        # Temporary compatibility bridge while the core is migrated. New code
        # should use the provider-neutral methods above.
        return getattr(self._session, name)


class GeminiLiveProvider:
    provider_id = "gemini-live"

    def __init__(self, *, api_key: str, model: str, api_version: str = "v1beta"):
        self.api_key = api_key
        self.model = model
        self.api_version = api_version

    @asynccontextmanager
    async def connect(self, *, config: Any):
        client = genai.Client(
            api_key=self.api_key,
            http_options={"api_version": self.api_version},
        )
        async with client.aio.live.connect(model=self.model, config=config) as session:
            yield GeminiLiveSession(session)
