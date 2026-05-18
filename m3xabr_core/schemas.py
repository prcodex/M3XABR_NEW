"""Pydantic schemas defining the contracts between actors.

Each actor in the pipeline has a typed input and a typed output. The
schemas here are the load-bearing contracts; if you fork m3xabr-core
and swap an actor implementation, conform to these and the pipeline
will keep working.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Actor 1 — Classifier
# ---------------------------------------------------------------------------

QueryType = Literal[
    "info",
    "analysis",
    "comparison",
    "release",
    "forecast",
    "drift",
    "off_scope",
]

TimeWindow = Literal["last_24h", "last_7d", "last_30d", "last_90d"]


class ClassifierOutput(BaseModel):
    """Structured metadata extracted from the user query.

    Produced by Actor 1. Consumed by Actor 1.5 (router) and Actor 4
    (retriever, for time-window filtering and top-K selection).
    """

    domain: str = Field(default="brazil")
    query_type: QueryType
    time_window: TimeWindow = "last_7d"
    entities_mentioned: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    language: Literal["pt-BR", "en", "mixed"] = "pt-BR"


# ---------------------------------------------------------------------------
# Actor 1.5 — Expertise Router
# ---------------------------------------------------------------------------


class RoutingDecision(BaseModel):
    """The router's decision on which expertise files to load.

    Produced by Actor 1.5. Consumed by Actor 2 (assembler) which reads
    the files and concatenates them.
    """

    kernel: str = "m3xabr_kernel"
    scope_filter: str = "scope_filter_brazil"
    expertises: list[str] = Field(min_length=1, max_length=3)
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = ""

    def all_files(self) -> list[str]:
        """Return all files to load, in dependency order."""
        return [self.kernel, self.scope_filter, *self.expertises]


# ---------------------------------------------------------------------------
# Actor 3 — Agent Hub
# ---------------------------------------------------------------------------


class AgentBlock(BaseModel):
    """A labeled context block from one of the data agents."""

    name: str  # e.g. "MARKET SNAPSHOT", "POLYMARKET", "CALENDAR"
    content: str
    timestamp: datetime | None = None


class AgentContext(BaseModel):
    """Combined output from all agents that fired for this query.

    Produced by Actor 3. Consumed by Actor 5 (synthesizer) as part of
    the user-turn payload.
    """

    blocks: list[AgentBlock] = Field(default_factory=list)

    def to_prompt_section(self) -> str:
        """Format as a single block of text for the synthesizer."""
        if not self.blocks:
            return ""
        parts = []
        for block in self.blocks:
            parts.append(f"=== {block.name} ===")
            parts.append(block.content)
            parts.append(f"=== END {block.name} ===")
        return "\n".join(parts)


# ---------------------------------------------------------------------------
# Actor 4 — Retriever
# ---------------------------------------------------------------------------


class RetrievedDoc(BaseModel):
    """A single document retrieved from the corpus."""

    id: str
    text: str
    source: str  # e.g. "valor", "itau_brazil", "twitter_handle"
    published_at: datetime | None = None
    score: float = 0.0
    domain: str = "brazil"
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Actor 5 — Synthesizer
# ---------------------------------------------------------------------------


class SynthesizerInput(BaseModel):
    """The full payload Actor 5 receives.

    `system_prompt` is the assembled soul from Actor 2.
    The rest is the dynamic context layered around the user's query.
    """

    system_prompt: str
    user_query: str
    time_window: TimeWindow
    agent_context: AgentContext
    retrieved_docs: list[RetrievedDoc]
    session_history: list[dict[str, str]] = Field(default_factory=list)
    health_caveats: str = ""

    def estimated_tokens(self) -> int:
        """Rough estimate of total input tokens."""
        total = len(self.system_prompt) // 4  # rough chars→tokens
        total += len(self.user_query) // 4
        total += len(self.agent_context.to_prompt_section()) // 4
        for doc in self.retrieved_docs:
            total += len(doc.text) // 4
        for turn in self.session_history:
            total += sum(len(v) // 4 for v in turn.values())
        total += len(self.health_caveats) // 4
        return total


# ---------------------------------------------------------------------------
# Actor 7 — Evaluator
# ---------------------------------------------------------------------------


class RubricScores(BaseModel):
    grounding: float = Field(ge=0.0, le=10.0)
    citation: float = Field(ge=0.0, le=10.0)
    clarity: float = Field(ge=0.0, le=10.0)
    completeness: float = Field(ge=0.0, le=10.0)
    no_fabrication: float = Field(ge=0.0, le=10.0)
    format_compliance: float = Field(ge=0.0, le=10.0)


class EvaluationResult(BaseModel):
    """The evaluator's verdict on a synthesized response."""

    score: float = Field(ge=0.0, le=10.0)
    rubric_scores: RubricScores
    improvement_hint: str | None = None
    regen_recommended: bool = False


# ---------------------------------------------------------------------------
# Full pipeline result
# ---------------------------------------------------------------------------


class PipelineResult(BaseModel):
    """The complete output of one pipeline run.

    Surfaced to the caller — contains the final response plus all
    intermediate state for debugging / logging / A-B analysis.
    """

    query: str
    response: str
    score: float
    classifier_output: ClassifierOutput
    routing_decision: RoutingDecision
    retrieved_doc_count: int
    agent_blocks_count: int
    estimated_system_tokens: int
    estimated_total_input_tokens: int
    evaluation: EvaluationResult
    regen_triggered: bool = False
    timing_ms: dict[str, float] = Field(default_factory=dict)
