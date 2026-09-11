"""Runtime provider registry.

The registry intentionally knows nothing about vendor SDKs.  Concrete providers
are registered by the application, making it possible to add providers without
coupling the JARVIS core to one vendor.
"""

from __future__ import annotations

from typing import Callable

from .base import LLMProvider


ProviderFactory = Callable[..., LLMProvider]


class ProviderRegistry:
    def __init__(self) -> None:
        self._factories: dict[str, ProviderFactory] = {}

    def register(self, name: str, factory: ProviderFactory) -> None:
        key = name.strip().lower()
        if not key:
            raise ValueError("Provider name cannot be empty")
        self._factories[key] = factory

    def create(self, name: str, **config):
        key = name.strip().lower()
        try:
            factory = self._factories[key]
        except KeyError as exc:
            available = ", ".join(sorted(self._factories)) or "none"
            raise ValueError(f"Unknown provider '{name}'. Available: {available}") from exc
        return factory(**config)

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._factories))


registry = ProviderRegistry()
