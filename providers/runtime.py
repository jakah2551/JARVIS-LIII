"""Build providers from the provider configuration file."""

from __future__ import annotations

from pathlib import Path

from .config import ProviderConfig, default_provider_name, load_provider_config
from .openai_compatible import OpenAICompatibleProvider
from .registry import ProviderRegistry


def build_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register("openai-compatible", OpenAICompatibleProvider)
    return registry


def build_provider(config_path: str | Path, name: str | None = None):
    configs = load_provider_config(config_path)
    selected = name or default_provider_name(config_path)
    if not selected:
        raise ValueError("No default_llm is configured")
    try:
        cfg: ProviderConfig = configs[selected]
    except KeyError as exc:
        available = ", ".join(sorted(configs)) or "none"
        raise ValueError(f"Unknown configured provider '{selected}'. Available: {available}") from exc

    registry = build_registry()
    if cfg.type != "openai-compatible":
        raise ValueError(
            f"Provider type '{cfg.type}' is not wired yet. "
            "Use 'openai-compatible' for OpenAI/OpenRouter/Ollama/custom endpoints."
        )
    if not cfg.base_url:
        raise ValueError(f"Provider '{selected}' is missing base_url")
    if not cfg.model:
        raise ValueError(f"Provider '{selected}' is missing model")

    return registry.create(
        cfg.type,
        base_url=cfg.base_url,
        api_key=cfg.api_key,
        model=cfg.model,
        timeout=cfg.timeout,
        **(cfg.options or {}),
    )
