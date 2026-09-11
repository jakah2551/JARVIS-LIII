"""Dependency-light OpenAI-compatible provider.

This covers OpenAI, OpenRouter, Together, Groq, Ollama (when exposed through
its OpenAI-compatible endpoint), vLLM, LM Studio, llama.cpp servers and other
compatible gateways.  No provider SDK is required.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, AsyncIterator, Mapping, Sequence

from .base import ChatMessage, LLMProvider, ProviderCapabilities, ProviderResponse


class OpenAICompatibleProvider:
    provider_id = "openai-compatible"

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None,
        model: str,
        timeout: float = 120.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.capabilities = ProviderCapabilities(
            chat=True,
            streaming=True,
            tools=True,
        )

    def _payload(
        self,
        messages: Sequence[ChatMessage],
        *,
        tools: Sequence[Mapping[str, Any]] | None,
        temperature: float | None,
        max_tokens: int | None,
        stream: bool,
        **kwargs: Any,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": m.role, "content": m.content} for m in messages
            ],
            "stream": stream,
        }
        if tools:
            payload["tools"] = list(tools)
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        payload.update(kwargs)
        return payload

    def _request(self, payload: Mapping[str, Any]) -> bytes:
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"{self.provider_id} HTTP {exc.code}: {detail[:1000]}"
            ) from exc

    async def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        tools: Sequence[Mapping[str, Any]] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        # Keep the first implementation dependency-free.  asyncio.to_thread
        # prevents urllib from blocking the JARVIS event loop.
        import asyncio

        raw = await asyncio.to_thread(
            self._request,
            self._payload(
                messages,
                tools=tools,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                **kwargs,
            ),
        )
        data = json.loads(raw.decode("utf-8"))
        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        return ProviderResponse(
            text=message.get("content") or "",
            raw=data,
            usage=data.get("usage") or {},
            finish_reason=choice.get("finish_reason"),
        )

    async def stream(
        self,
        messages: Sequence[ChatMessage],
        *,
        tools: Sequence[Mapping[str, Any]] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Yield text deltas from an SSE-compatible endpoint.

        The transport is intentionally small; provider-specific realtime/audio
        protocols belong in separate adapters rather than in this LLM class.
        """
        import asyncio

        payload = self._payload(
            messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )

        # urllib's streaming response is consumed in a worker and forwarded
        # through an asyncio queue, preserving back-pressure for the caller.
        queue: asyncio.Queue[str | None | BaseException] = asyncio.Queue()

        def worker() -> None:
            try:
                body = json.dumps(payload).encode("utf-8")
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                req = urllib.request.Request(
                    f"{self.base_url}/chat/completions",
                    data=body,
                    headers=headers,
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    for raw_line in response:
                        line = raw_line.decode("utf-8", errors="replace").strip()
                        if not line.startswith("data:"):
                            continue
                        chunk = line[5:].strip()
                        if chunk == "[DONE]":
                            break
                        try:
                            data = json.loads(chunk)
                            delta = ((data.get("choices") or [{}])[0]
                                     .get("delta") or {}).get("content")
                            if delta:
                                asyncio.run_coroutine_threadsafe(queue.put(delta), loop)
                        except json.JSONDecodeError:
                            continue
            except BaseException as exc:
                asyncio.run_coroutine_threadsafe(queue.put(exc), loop)
            finally:
                asyncio.run_coroutine_threadsafe(queue.put(None), loop)

        loop = asyncio.get_running_loop()
        await asyncio.to_thread(worker)
        while True:
            item = await queue.get()
            if item is None:
                break
            if isinstance(item, BaseException):
                raise item
            yield item
