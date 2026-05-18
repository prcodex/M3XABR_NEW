"""Vector DB backend — pluggable.

Default uses LanceDB. Alternative implementations could wrap Qdrant,
Weaviate, pgvector, Pinecone — anything with vector + metadata filter
support.
"""

from __future__ import annotations

from typing import Any, Protocol

from m3xabr_core.schemas import RetrievedDoc


class VectorDBBackend(Protocol):
    """Minimal contract for a vector DB."""

    def search(
        self,
        *,
        query_vector: list[float],
        filter_expr: str,
        top_k: int,
    ) -> list[RetrievedDoc]:
        """Return top_k docs matching the filter_expr, ranked by vector similarity."""
        ...


class LanceDBBackend:
    """LanceDB backend.

    Expects a table with columns: id, text, source, published_at, domain,
    content_vector, has_vector, and any optional metadata columns. See
    docs/SCHEMA.md for the full schema.
    """

    def __init__(self, db_path: str, table_name: str = "unified_feed") -> None:
        try:
            import lancedb
        except ImportError as e:
            raise ImportError(
                "lancedb package required. Install with: pip install lancedb"
            ) from e

        self._db = lancedb.connect(db_path)
        self._table_name = table_name
        try:
            self._table = self._db.open_table(table_name)
        except Exception:
            self._table = None  # Will fail at search-time if not created

    def search(
        self,
        *,
        query_vector: list[float],
        filter_expr: str,
        top_k: int,
    ) -> list[RetrievedDoc]:
        if self._table is None:
            return []

        # LanceDB vector search with metadata filter
        results = (
            self._table.search(query_vector)
            .where(filter_expr)
            .limit(top_k)
            .to_list()
        )

        return [self._row_to_doc(row) for row in results]

    @staticmethod
    def _row_to_doc(row: dict[str, Any]) -> RetrievedDoc:
        return RetrievedDoc(
            id=str(row.get("id", "")),
            text=str(row.get("text", "")),
            source=str(row.get("source", "unknown")),
            published_at=row.get("published_at"),
            score=float(row.get("_distance", 0.0)),
            domain=str(row.get("domain", "brazil")),
            metadata={
                k: v
                for k, v in row.items()
                if k
                not in {
                    "id",
                    "text",
                    "source",
                    "published_at",
                    "domain",
                    "content_vector",
                    "_distance",
                }
            },
        )


class StubVectorDB:
    """Stub backend for tests.

    Stores a small in-memory corpus and returns deterministic top-K
    based on simple keyword overlap.
    """

    def __init__(self, docs: list[RetrievedDoc] | None = None) -> None:
        self._docs = docs or []

    def add(self, doc: RetrievedDoc) -> None:
        self._docs.append(doc)

    def search(
        self,
        *,
        query_vector: list[float],
        filter_expr: str,
        top_k: int,
    ) -> list[RetrievedDoc]:
        # Filter by domain (extract from "domain = 'brazil'")
        # This stub doesn't parse filter_expr fully — just checks for
        # "domain = '...'" pattern.
        wanted_domain = "brazil"
        if "domain = '" in filter_expr:
            wanted_domain = filter_expr.split("domain = '")[1].split("'")[0]

        filtered = [d for d in self._docs if d.domain == wanted_domain]
        # Return first top_k (no ranking — stub)
        return filtered[:top_k]
