"""LLM backend — abstracts the model API so the rest of the code is provider-agnostic.

Default implementation uses Anthropic's Messages API. Swap by implementing
LLMBackend for your provider of choice.
"""

from __future__ import annotations

import os
from typing import Protocol


class LLMBackend(Protocol):
    """Minimal contract for an LLM provider."""

    def complete(
        self,
        *,
        model: str,
        system: str,
        user: str,
        max_tokens: int = 4096,
        temperature: float = 0.0,
    ) -> str:
        """Synchronous completion. Returns the text content."""
        ...


class AnthropicLLM:
    """Anthropic Messages API backend.

    Picks up ANTHROPIC_API_KEY from the environment by default.
    """

    def __init__(self, api_key: str | None = None) -> None:
        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise ImportError(
                "anthropic package required. Install with: pip install anthropic"
            ) from e

        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. Set the env var or pass api_key="
            )

        self._client = Anthropic(api_key=key)

    def complete(
        self,
        *,
        model: str,
        system: str,
        user: str,
        max_tokens: int = 4096,
        temperature: float = 0.0,
    ) -> str:
        """Call Messages API and return concatenated text content."""
        response = self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )

        # Concatenate text blocks (response.content is a list of blocks)
        parts = []
        for block in response.content:
            if hasattr(block, "text"):
                parts.append(block.text)
        return "\n".join(parts).strip()


class StubLLM:
    """Stub backend for tests. Returns a canned response.

    Use this in unit tests to avoid API calls. Set canned_response per
    instance for test fixtures.
    """

    def __init__(self, canned_response: str = "stub response") -> None:
        self.canned_response = canned_response
        self.calls: list[dict[str, str]] = []

    def complete(
        self,
        *,
        model: str,
        system: str,
        user: str,
        max_tokens: int = 4096,
        temperature: float = 0.0,
    ) -> str:
        self.calls.append({"model": model, "system": system, "user": user})
        return self.canned_response
