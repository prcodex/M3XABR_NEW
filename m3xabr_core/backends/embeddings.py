"""Embedding backend — pluggable.

Default uses Voyage-3-large (2048 dim, multilingual, strong on Portuguese).
Alternative implementations: OpenAI, Cohere. Add yours by conforming to
the EmbeddingBackend protocol.
"""

from __future__ import annotations

import os
from typing import Protocol


class EmbeddingBackend(Protocol):
    """Minimal contract for an embedding provider."""

    dimension: int

    def embed(self, text: str) -> list[float]:
        """Embed a single text. Returns a vector of `dimension` floats."""
        ...

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts. Default impl loops over embed()."""
        return [self.embed(t) for t in texts]


class VoyageEmbeddings:
    """Voyage AI embedding backend.

    Picks up VOYAGE_API_KEY from the environment by default.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "voyage-3-large",
        dimension: int = 2048,
    ) -> None:
        try:
            import voyageai
        except ImportError as e:
            raise ImportError(
                "voyageai package required. Install with: pip install voyageai"
            ) from e

        key = api_key or os.environ.get("VOYAGE_API_KEY")
        if not key:
            raise RuntimeError(
                "VOYAGE_API_KEY not set. Set the env var or pass api_key="
            )

        self._client = voyageai.Client(api_key=key)
        self.model = model
        self.dimension = dimension

    def embed(self, text: str) -> list[float]:
        result = self._client.embed(
            [text],
            model=self.model,
            input_type="query",
            output_dimension=self.dimension,
        )
        return result.embeddings[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        result = self._client.embed(
            texts,
            model=self.model,
            input_type="document",
            output_dimension=self.dimension,
        )
        return result.embeddings


class OpenAIEmbeddings:
    """OpenAI embedding backend (alternative)."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "text-embedding-3-large",
        dimension: int = 3072,
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError as e:
            raise ImportError(
                "openai package required. Install with: pip install m3xabr-core[openai]"
            ) from e

        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY not set.")

        self._client = OpenAI(api_key=key)
        self.model = model
        self.dimension = dimension

    def embed(self, text: str) -> list[float]:
        response = self._client.embeddings.create(
            input=text, model=self.model, dimensions=self.dimension
        )
        return response.data[0].embedding


class StubEmbeddings:
    """Stub backend for tests. Returns deterministic vectors of zeros + a hash."""

    def __init__(self, dimension: int = 2048) -> None:
        self.dimension = dimension

    def embed(self, text: str) -> list[float]:
        # Deterministic — same text → same vector. Not semantically useful
        # but fine for plumbing tests.
        h = hash(text)
        vec = [0.0] * self.dimension
        if self.dimension > 0:
            vec[abs(h) % self.dimension] = 1.0
        return vec
