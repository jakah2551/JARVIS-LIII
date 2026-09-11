"""Provider contracts used by the JARVIS core.

Keep this module dependency-free.  Concrete providers can depend on their own
SDKs without forcing those SDKs onto every JARVIS installation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Mapping, Protocol, Sequence


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


@dataclass(frozen=True)
class ProviderCapabilities:
    chat: bool = True
    streaming: bool = False
    tools: bool = False
    vision: bool = False
    audio_input: bool = False
    audio_output: bool = False
    realtime: bool = False


@dataclass
class ProviderResponse:
    text: str = ""
    raw: Any = None
    usage: Mapping[str, Any] = field(default_factory=dict)
    finish_reason: str | None = None


class LLMProvider(Protocol):
    """Minimal contract every text provider must satisfy."""

    provider_id: str
    model: str
    capabilities: ProviderCapabilities

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        tools: Sequence[Mapping[str, Any]] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        ...

    async def stream(
        self,
        messages: Sequence[ChatMessage],
        *,
        tools: Sequence[Mapping[str, Any]] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        ...
