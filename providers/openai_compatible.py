"""Dependency-light OpenAI-compatible provider.

Covers OpenAI, OpenRouter, Together, Groq, Ollama, vLLM, LM Studio,
llama.cpp servers and other compatible gateways. No vendor SDK is required.
"""

from __future__ import annotations

import asyncio
import json
import urllib.error
import urllib.request
from typing import Any, AsyncIterator, Mapping, Sequence

from .base import ChatMessage, ProviderCapabilities, ProviderResponse, ToolCall


class OpenAICompatibleProvider:
    provider_id = "openai-compatible"

    def __init__(self, *, base_url: str, api_key: str | None, model: str,
                 timeout: float = 120.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.capabilities = ProviderCapabilities(
            chat=True, streaming=True, tools=True, vision=True
        )

    @staticmethod
    def _normalize_tool(tool: Mapping[str, Any]) -> Mapping[str, Any]:
        """Accept either OpenAI tools or the Gemini-style declaration used by
        Mark-LIII and normalize it to the OpenAI `type=function` shape."""
        if tool.get("type") == "function":
            return tool
        if "function_declarations" in tool:
            declarations = tool.get("function_declarations") or []
            # A single declaration is the common path; callers that provide a
            # list are expanded by _payload().
            if len(declarations) == 1:
                fn = declarations[0]
                return {"type": "function", "function": {
                    "name": fn.get("name", ""),
                    "description": fn.get("description", ""),
                    "parameters": fn.get("parameters") or {"type": "object", "properties": {}},
                }}
        return tool

    def _tools(self, tools: Sequence[Mapping[str, Any]] | None) -> list[Mapping[str, Any]]:
        result: list[Mapping[str, Any]] = []
        for tool in tools or []:
            if "function_declarations" in tool:
                for fn in tool.get("function_declarations") or []:
                    result.append({"type": "function", "function": {
                        "name": fn.get("name", ""),
                        "description": fn.get("description", ""),
                        "parameters": fn.get("parameters") or {"type": "object", "properties": {}},
                    }})
            else:
                result.append(self._normalize_tool(tool))
        return result

    def _payload(self, messages: Sequence[ChatMessage], *, tools,
                 temperature, max_tokens, stream, **kwargs: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": stream,
        }
        normalized = self._tools(tools)
        if normalized:
            payload["tools"] = normalized
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        payload.update(kwargs)
        return payload

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def complete(self, messages: Sequence[ChatMessage], *, tools=None,
                       temperature=None, max_tokens=None, **kwargs: Any) -> ProviderResponse:
        payload = self._payload(messages, tools=tools, temperature=temperature,
                                max_tokens=max_tokens, stream=False, **kwargs)

        def request() -> bytes:
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers=self._headers(), method="POST")
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    return response.read()
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"{self.provider_id} HTTP {exc.code}: {detail[:1000]}") from exc

        data = json.loads((await asyncio.to_thread(request)).decode("utf-8"))
        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        calls = []
        for call in message.get("tool_calls") or []:
            fn = call.get("function") or {}
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            calls.append(ToolCall(id=str(call.get("id") or ""), name=str(fn.get("name") or ""), arguments=args))
        return ProviderResponse(
            text=message.get("content") or "", raw=data,
            usage=data.get("usage") or {}, finish_reason=choice.get("finish_reason"),
            tool_calls=calls,
        )

    async def stream(self, messages: Sequence[ChatMessage], *, tools=None,
                     temperature=None, max_tokens=None, **kwargs: Any) -> AsyncIterator[str]:
        payload = self._payload(messages, tools=tools, temperature=temperature,
                                max_tokens=max_tokens, stream=True, **kwargs)
        loop = asyncio.get_running_loop()
        queue: asyncio.Queue[str | None | BaseException] = asyncio.Queue()

        def put(item: str | None | BaseException) -> None:
            asyncio.run_coroutine_threadsafe(queue.put(item), loop)

        def worker() -> None:
            try:
                req = urllib.request.Request(
                    f"{self.base_url}/chat/completions",
                    data=json.dumps(payload).encode("utf-8"),
                    headers=self._headers(), method="POST")
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
                            delta = ((data.get("choices") or [{}])[0].get("delta") or {}).get("content")
                            if delta:
                                put(delta)
                        except json.JSONDecodeError:
                            continue
            except BaseException as exc:
                put(exc)
            finally:
                put(None)

        worker_task = asyncio.create_task(asyncio.to_thread(worker))
        try:
            while True:
                item = await queue.get()
                if item is None:
                    break
                if isinstance(item, BaseException):
                    raise item
                yield item
        finally:
            await worker_task
