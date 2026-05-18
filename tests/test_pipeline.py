"""End-to-end pipeline smoke test with all stubs.

Verifies the pipeline wires actors correctly and that data flows from
query → response without crashing. Uses StubLLM, StubEmbeddings,
StubVectorDB so no API calls are made.

For real quality testing, you need a live LLM and a real corpus —
those are integration tests, not unit tests.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from m3xabr_core import Pipeline
from m3xabr_core.actors import (
    AgentHub,
    Classifier,
    Evaluator,
    ExpertiseAssembler,
    ExpertiseRouter,
    Retriever,
    Synthesizer,
)
from m3xabr_core.backends.embeddings import StubEmbeddings
from m3xabr_core.backends.llm import StubLLM
from m3xabr_core.backends.vector_db import StubVectorDB
from m3xabr_core.schemas import RetrievedDoc


@pytest.fixture
def stub_corpus() -> StubVectorDB:
    """Tiny in-memory corpus for smoke tests."""
    db = StubVectorDB()
    db.add(
        RetrievedDoc(
            id="1",
            text=(
                "O Itaú Macro Research projetou em relatório de março "
                "que a Selic terminal deve ficar em 9,75% a.a., revisando "
                "a projeção anterior de 9,50%."
            ),
            source="itau_brazil",
            published_at=datetime(2026, 3, 15, tzinfo=timezone.utc),
            domain="brazil",
        )
    )
    db.add(
        RetrievedDoc(
            id="2",
            text=(
                "A XP Macro Strategy mantém Selic terminal em 10,00%, "
                "mais hawkish que o consenso Focus que está em 9,75%."
            ),
            source="xp_brazil",
            published_at=datetime(2026, 3, 12, tzinfo=timezone.utc),
            domain="brazil",
        )
    )
    db.add(
        RetrievedDoc(
            id="3",
            text=(
                "IPCA de fevereiro veio em 0,42% m/m, acumulado em 12 "
                "meses ficou em 4,12%, dentro do intervalo de meta."
            ),
            source="ibge",
            published_at=datetime(2026, 3, 10, tzinfo=timezone.utc),
            domain="brazil",
        )
    )
    return db


def test_pipeline_runs_end_to_end(stub_corpus: StubVectorDB) -> None:
    """Full pipeline from query to response with all stubs."""
    classifier_response = json.dumps(
        {
            "domain": "brazil",
            "query_type": "forecast",
            "time_window": "last_7d",
            "entities_mentioned": ["itau", "selic"],
            "topics": ["monetary_policy"],
            "language": "pt-BR",
        }
    )
    router_response = json.dumps(
        {
            "kernel": "m3xabr_kernel",
            "scope_filter": "scope_filter_brazil",
            "expertises": ["monetary_analysis"],
            "confidence": 0.9,
            "reasoning": "Selic forecast from Itaú",
        }
    )
    synth_response = (
        "Nos últimos 7 dias, o Itaú projetou Selic terminal em 9,75% a.a. "
        "(relatório macro de março). A XP, em contraste, mantém 10,00%, "
        "mais hawkish que o consenso Focus."
    )
    eval_response = json.dumps(
        {
            "score": 8.5,
            "rubric_scores": {
                "grounding": 9.0,
                "citation": 8.5,
                "clarity": 9.0,
                "completeness": 8.0,
                "no_fabrication": 9.0,
                "format_compliance": 8.0,
            },
            "improvement_hint": None,
            "regen_recommended": False,
        }
    )

    # Custom multi-response stub LLM
    class SequenceStubLLM:
        def __init__(self, responses: list[str]) -> None:
            self._responses = list(responses)
            self.calls = 0

        def complete(self, *, model, system, user, max_tokens=4096, temperature=0.0):
            response = self._responses[min(self.calls, len(self._responses) - 1)]
            self.calls += 1
            return response

    llm = SequenceStubLLM(
        [classifier_response, router_response, synth_response, eval_response]
    )

    pipeline = Pipeline(
        llm=llm,  # type: ignore[arg-type]
        embedder=StubEmbeddings(),
        vector_db=stub_corpus,
        agent_hub=AgentHub(agents=[]),  # no agents for smoke test
    )

    result = pipeline.run("O que o Itaú projeta para Selic?")

    assert result.response.startswith("Nos últimos 7 dias")
    assert result.score == 8.5
    assert result.classifier_output.query_type == "forecast"
    assert result.routing_decision.expertises == ["monetary_analysis"]
    assert result.retrieved_doc_count > 0
    assert not result.regen_triggered
    assert result.estimated_system_tokens > 0


def test_pipeline_token_estimates(stub_corpus: StubVectorDB) -> None:
    """The system prompt should be < 4000 tokens for any single query."""
    classifier_response = json.dumps(
        {
            "domain": "brazil",
            "query_type": "info",
            "time_window": "last_7d",
            "entities_mentioned": [],
            "topics": [],
            "language": "pt-BR",
        }
    )
    router_response = json.dumps(
        {
            "kernel": "m3xabr_kernel",
            "scope_filter": "scope_filter_brazil",
            "expertises": ["market_intelligence"],
            "confidence": 0.9,
            "reasoning": "test",
        }
    )

    class SequenceStubLLM:
        def __init__(self, responses: list[str]) -> None:
            self._responses = list(responses)
            self.calls = 0

        def complete(self, *, model, system, user, max_tokens=4096, temperature=0.0):
            response = self._responses[min(self.calls, len(self._responses) - 1)]
            self.calls += 1
            return response

    llm = SequenceStubLLM(
        [
            classifier_response,
            router_response,
            "stub response",
            json.dumps(
                {
                    "score": 8.0,
                    "rubric_scores": {
                        "grounding": 8.0,
                        "citation": 8.0,
                        "clarity": 8.0,
                        "completeness": 8.0,
                        "no_fabrication": 8.0,
                        "format_compliance": 8.0,
                    },
                    "improvement_hint": None,
                    "regen_recommended": False,
                }
            ),
        ]
    )

    pipeline = Pipeline(
        llm=llm,  # type: ignore[arg-type]
        embedder=StubEmbeddings(),
        vector_db=stub_corpus,
        agent_hub=AgentHub(agents=[]),
    )

    result = pipeline.run("test query")

    # System prompt should be under 4500 tokens for single-expertise load
    assert result.estimated_system_tokens < 4500
    # And substantially less than the ~6,800 of a monolithic soul
    assert result.estimated_system_tokens < 5000
