"""Actor 4 — Retriever.

Fetches relevant documents from the vector DB. Simplified scoring in
v0: vector similarity + freshness decay. The full M3xA production
scoring (entity boost, source tier, M/G scores) is documented in
ARCHITECTURE.md and implementable by extending this class.

The domain filter is applied at the vector-DB query level — Brazilian
docs only. Off-scope queries still retrieve, but the kernel + scope
filter decline gracefully.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path

import yaml

from m3xabr_core.backends.embeddings import EmbeddingBackend
from m3xabr_core.backends.vector_db import VectorDBBackend
from m3xabr_core.schemas import ClassifierOutput, RetrievedDoc


class Retriever:
    """Actor 4 — semantic retrieval against the Brazil corpus."""

    def __init__(
        self,
        embedder: EmbeddingBackend,
        vector_db: VectorDBBackend,
        config_path: Path | None = None,
    ) -> None:
        self._embedder = embedder
        self._db = vector_db
        if config_path is None:
            config_path = (
                Path(__file__).parent.parent.parent
                / "config"
                / "retrieval_scoring.yaml"
            )
        self._config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    def retrieve(
        self,
        query: str,
        classifier_output: ClassifierOutput,
    ) -> list[RetrievedDoc]:
        """Embed the query, search the corpus, rescore by freshness."""
        # 1. Embed the query
        query_vector = self._embedder.embed(query)

        # 2. Determine top-K from query type
        top_k = self._config["topk"].get(
            classifier_output.query_type,
            self._config["topk"]["info"],
        )

        # 3. Build filter expression
        filter_parts = [self._config["domain_filter"]]
        if self._config.get("has_vector_filter"):
            filter_parts.append(self._config["has_vector_filter"])
        filter_expr = " AND ".join(filter_parts)

        # 4. Query vector DB
        docs = self._db.search(
            query_vector=query_vector,
            filter_expr=filter_expr,
            top_k=top_k,
        )

        # 5. Rescore by freshness + vector
        rescored = self._rescore(docs)
        return rescored

    def _rescore(self, docs: list[RetrievedDoc]) -> list[RetrievedDoc]:
        """Apply vector + freshness weighted scoring."""
        v_weight = float(self._config["vector_weight"])
        f_weight = float(self._config["freshness"]["weight"])
        decay = float(self._config["freshness"]["decay_rate"])
        now = datetime.now(timezone.utc)

        for doc in docs:
            # Vector component: docs come back with _distance from LanceDB,
            # which we use as score (cosine distance, 0=identical).
            # Convert to similarity: higher = better.
            vec_sim = max(0.0, 1.0 - doc.score)

            # Freshness component
            if doc.published_at is not None:
                age_days = (now - doc.published_at).total_seconds() / 86400.0
                freshness = math.exp(-age_days * decay)
            else:
                freshness = 0.5  # neutral if unknown

            doc.score = v_weight * vec_sim + f_weight * freshness

        # Sort descending — best first
        return sorted(docs, key=lambda d: d.score, reverse=True)
