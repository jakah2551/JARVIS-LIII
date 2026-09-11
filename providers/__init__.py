"""Provider abstraction for JARVIS.

The provider layer deliberately lives outside the assistant core. A provider may
implement text chat, streaming, vision, tools, or realtime audio independently.
"""

from .base import ChatMessage, LLMProvider, ProviderCapabilities, ProviderResponse, ToolCall
from .registry import ProviderRegistry
from .realtime import RealtimeProvider, RealtimeSession

__all__ = [
    "ChatMessage",
    "LLMProvider",
    "ProviderCapabilities",
    "ProviderResponse",
    "ToolCall",
    "ProviderRegistry",
    "RealtimeProvider",
    "RealtimeSession",
]
