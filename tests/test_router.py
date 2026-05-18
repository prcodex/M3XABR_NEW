"""Tests for the ExpertiseRouter (Actor 1.5).

Uses a stub LLM to verify the router's contract — that it correctly
parses JSON responses and produces valid RoutingDecision schemas.

Real routing accuracy tests (does the router pick the right expertises
on real queries?) require a live LLM and are best done as an integration
test or via the routing audit process described in
docs/ROUTING_DECISIONS.md.
"""

from __future__ import annotations

import json

import pytest

from m3xabr_core.actors import ExpertiseRouter
from m3xabr_core.backends.llm import StubLLM
from m3xabr_core.schemas import ClassifierOutput, RoutingDecision


def make_classifier_output(
    query_type: str = "info",
    entities: list[str] | None = None,
    topics: list[str] | None = None,
) -> ClassifierOutput:
    return ClassifierOutput(
        domain="brazil",
        query_type=query_type,  # type: ignore[arg-type]
        time_window="last_7d",
        entities_mentioned=entities or [],
        topics=topics or [],
        language="pt-BR",
    )


def test_router_parses_clean_json() -> None:
    """Router should handle a clean JSON response."""
    canned = json.dumps(
        {
            "kernel": "m3xabr_kernel",
            "scope_filter": "scope_filter_brazil",
            "expertises": ["monetary_analysis"],
            "confidence": 0.92,
            "reasoning": "Pure Selic query",
        }
    )
    router = ExpertiseRouter(StubLLM(canned_response=canned))

    decision = router.route(
        "Como está a Selic?",
        make_classifier_output(entities=["selic"]),
    )

    assert isinstance(decision, RoutingDecision)
    assert decision.expertises == ["monetary_analysis"]
    assert decision.confidence == 0.92


def test_router_parses_fenced_json() -> None:
    """Router should strip ```json fences."""
    canned = (
        "```json\n"
        + json.dumps(
            {
                "kernel": "m3xabr_kernel",
                "scope_filter": "scope_filter_brazil",
                "expertises": ["fiscal_analysis", "monetary_analysis"],
                "confidence": 0.85,
                "reasoning": "Bridge fiscal-monetary",
            }
        )
        + "\n```"
    )
    router = ExpertiseRouter(StubLLM(canned_response=canned))

    decision = router.route(
        "Como o fiscal afeta a Selic?",
        make_classifier_output(entities=["selic"], topics=["fiscal"]),
    )

    assert len(decision.expertises) == 2
    assert "fiscal_analysis" in decision.expertises
    assert "monetary_analysis" in decision.expertises


def test_router_parses_json_with_preamble() -> None:
    """Router should extract JSON even with leading prose."""
    canned = (
        "Here is my routing decision:\n\n"
        + json.dumps(
            {
                "kernel": "m3xabr_kernel",
                "scope_filter": "scope_filter_brazil",
                "expertises": ["electoral_analysis"],
                "confidence": 0.95,
                "reasoning": "Pure poll query",
            }
        )
    )
    router = ExpertiseRouter(StubLLM(canned_response=canned))

    decision = router.route(
        "Quem está na frente nas pesquisas?",
        make_classifier_output(query_type="info", topics=["election_polls"]),
    )

    assert decision.expertises == ["electoral_analysis"]


def test_router_validates_expertise_count() -> None:
    """Router should reject empty expertise list."""
    canned = json.dumps(
        {
            "kernel": "m3xabr_kernel",
            "scope_filter": "scope_filter_brazil",
            "expertises": [],  # invalid — schema requires min_length=1
            "confidence": 0.5,
            "reasoning": "test",
        }
    )
    router = ExpertiseRouter(StubLLM(canned_response=canned))

    with pytest.raises(Exception):  # Pydantic ValidationError
        router.route("test", make_classifier_output())


def test_router_validates_confidence_range() -> None:
    """Confidence must be in [0.0, 1.0]."""
    canned = json.dumps(
        {
            "kernel": "m3xabr_kernel",
            "scope_filter": "scope_filter_brazil",
            "expertises": ["monetary_analysis"],
            "confidence": 1.5,  # invalid
            "reasoning": "test",
        }
    )
    router = ExpertiseRouter(StubLLM(canned_response=canned))

    with pytest.raises(Exception):
        router.route("test", make_classifier_output())


def test_router_caps_expertises_at_3() -> None:
    """The schema enforces max 3 expertises."""
    canned = json.dumps(
        {
            "kernel": "m3xabr_kernel",
            "scope_filter": "scope_filter_brazil",
            "expertises": [
                "monetary_analysis",
                "fiscal_analysis",
                "economic_releases",
                "economic_forecasts",  # 4 — too many
            ],
            "confidence": 0.5,
            "reasoning": "test",
        }
    )
    router = ExpertiseRouter(StubLLM(canned_response=canned))

    with pytest.raises(Exception):
        router.route("test", make_classifier_output())


def test_router_all_files_returns_full_load() -> None:
    """RoutingDecision.all_files() should return kernel + scope + expertises."""
    decision = RoutingDecision(
        kernel="m3xabr_kernel",
        scope_filter="scope_filter_brazil",
        expertises=["monetary_analysis", "fiscal_analysis"],
        confidence=0.9,
        reasoning="test",
    )

    files = decision.all_files()
    assert files == [
        "m3xabr_kernel",
        "scope_filter_brazil",
        "monetary_analysis",
        "fiscal_analysis",
    ]
