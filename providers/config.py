"""Provider configuration loading and environment interpolation.

This module contains configuration policy only; it does not import vendor SDKs.
Secrets should be referenced through environment variables rather than committed
into the repository.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    type: str
    model: str
    base_url: str | None = None
    api_key: str | None = None
    timeout: float = 120.0
    options: dict[str, Any] | None = None


def _env(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    # Supports ${NAME} and ${NAME:-fallback} without requiring a templating
    # dependency. Unresolved variables are intentionally left untouched so a
    # useful configuration error can be produced by the provider layer.
    if value.startswith("${") and value.endswith("}"):
        expr = value[2:-1]
        if ":-" in expr:
            name, fallback = expr.split(":-", 1)
            return os.getenv(name, fallback)
        return os.getenv(expr, value)
    return value


def load_provider_config(path: str | Path) -> dict[str, ProviderConfig]:
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    providers: dict[str, ProviderConfig] = {}
    for name, item in (raw.get("providers") or {}).items():
        item = dict(item or {})
        api_key = item.get("api_key")
        api_key_env = item.get("api_key_env")
        if api_key_env:
            api_key = os.getenv(str(api_key_env))
        elif api_key is not None:
            api_key = _env(api_key)

        providers[name] = ProviderConfig(
            name=name,
            type=str(item.get("type", "openai-compatible")),
            model=str(_env(item.get("model", ""))),
            base_url=_env(item.get("base_url")),
            api_key=api_key,
            timeout=float(item.get("timeout", 120.0)),
            options=dict(item.get("options") or {}),
        )
    return providers


def default_provider_name(path: str | Path) -> str | None:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    value = raw.get("default_llm")
    return str(value) if value else None
