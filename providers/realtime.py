"""Provider-neutral contract for low-latency bidirectional voice sessions.

A realtime provider owns its wire protocol. The JARVIS core only relies on this
small surface, allowing Gemini Live, OpenAI Realtime, or another future audio
provider to be implemented independently.
"""

from __future__ import annotations

from contextlib import AbstractAsyncContextManager
from typing import Any, AsyncIterator, Protocol


class RealtimeSession(Protocol):
    async def send_audio(self, data: bytes, mime_type: str = "audio/pcm") -> None:
        ...

    def receive(self) -> AsyncIterator[Any]:
        ...

    async def send_text(self, text: str, *, turn_complete: bool = True) -> None:
        ...

    async def send_tool_response(self, function_responses: list[Any]) -> None:
        ...


class RealtimeProvider(Protocol):
    provider_id: str
    model: str

    def connect(self, **kwargs: Any) -> AbstractAsyncContextManager[RealtimeSession]:
        ...
