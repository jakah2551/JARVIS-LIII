"""Provider abstraction for JARVIS.

The provider layer deliberately lives outside the assistant core.  A provider may
implement text chat, streaming, vision, tools, or realtime audio independently.
"""

from .base import ChatMessage, LLMProvider, ProviderCapabilities, ProviderResponse
from .registry import ProviderRegistry

__all__ = [
    "ChatMessage",
    "LLMProvider",
    "ProviderCapabilities",
    "ProviderResponse",
    "ProviderRegistry",
]
