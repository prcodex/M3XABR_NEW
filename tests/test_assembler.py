"""Tests for the ExpertiseAssembler (Actor 2).

The assembler is the most-tested actor because:
- It has no LLM call (deterministic)
- It controls token counts
- It implements the conservative fallback for low confidence

These tests verify file concatenation, frontmatter stripping, and the
keyword-matching fallback.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from m3xabr_core.actors import ExpertiseAssembler
from m3xabr_core.schemas import ClassifierOutput, RoutingDecision

EXPERTISES_DIR = Path(__file__).parent.parent / "expertises"


def test_assembler_loads_required_files() -> None:
    """Kernel + scope filter + named expertise are all in the output."""
    assembler = ExpertiseAssembler(EXPERTISES_DIR)
    routing = RoutingDecision(
        kernel="m3xabr_kernel",
        scope_filter="scope_filter_brazil",
        expertises=["monetary_analysis"],
        confidence=0.9,
        reasoning="test",
    )

    prompt = assembler.assemble(routing)

    # The kernel's identity section signal
    assert "M3xA Brasil" in prompt
    # The scope filter's mirror filter signal
    assert "Escopo Brasil" in prompt or "ESCOPO" in prompt
    # The monetary expertise signal
    assert "Selic" in prompt
    assert "Copom" in prompt


def test_assembler_strips_frontmatter() -> None:
    """YAML frontmatter must not leak into the system prompt."""
    assembler = ExpertiseAssembler(EXPERTISES_DIR)
    routing = RoutingDecision(
        kernel="m3xabr_kernel",
        scope_filter="scope_filter_brazil",
        expertises=["fiscal_analysis"],
        confidence=0.9,
        reasoning="test",
    )

    prompt = assembler.assemble(routing)

    # Frontmatter markers should not appear
    assert "trigger_keywords:" not in prompt
    assert "version:" not in prompt
    assert "applies_to: brazil" not in prompt
    # The first three dashes of YAML must not be there either
    assert not prompt.startswith("---")


def test_assembler_token_count_typical_query() -> None:
    """A typical 1-3 expertise load should be under monolithic (~6,800 tokens).

    Real measurements (v0):
    - 1 expertise: ~2,300-3,100 tokens
    - 2 expertises: ~4,000-4,700 tokens
    - 3 expertises: ~5,500-6,000 tokens
    """
    assembler = ExpertiseAssembler(EXPERTISES_DIR)
    routing = RoutingDecision(
        kernel="m3xabr_kernel",
        scope_filter="scope_filter_brazil",
        expertises=["monetary_analysis", "fiscal_analysis"],
        confidence=0.9,
        reasoning="test",
    )

    prompt = assembler.assemble(routing)
    est_tokens = len(prompt) // 4

    # 2-expertise load should be well under monolithic 6,800
    assert 3000 < est_tokens < 6000, f"Expected 3000-6000 tokens, got {est_tokens}"


def test_assembler_single_expertise_smaller() -> None:
    """Single expertise should be smaller than multi-expertise."""
    assembler = ExpertiseAssembler(EXPERTISES_DIR)

    single = assembler.assemble(
        RoutingDecision(
            expertises=["market_intelligence"],
            confidence=0.9,
            reasoning="test",
        )
    )
    triple = assembler.assemble(
        RoutingDecision(
            expertises=[
                "monetary_analysis",
                "fiscal_analysis",
                "economic_releases",
            ],
            confidence=0.9,
            reasoning="test",
        )
    )

    assert len(single) < len(triple)


def test_assembler_conservative_fallback() -> None:
    """Low confidence should pull in more expertises via keyword match."""
    assembler = ExpertiseAssembler(EXPERTISES_DIR, confidence_threshold=0.7)

    # Low confidence, plus the classifier mentions Selic (monetary)
    routing = RoutingDecision(
        expertises=["economic_releases"],  # router picked this
        confidence=0.5,  # but is uncertain
        reasoning="test",
    )
    classifier = ClassifierOutput(
        query_type="info",
        time_window="last_7d",
        entities_mentioned=["selic"],
        topics=["monetary_policy"],
    )

    prompt_with_fallback = assembler.assemble(routing, classifier)
    prompt_without_fallback = assembler.assemble(routing)

    # The fallback version should be longer (loaded extra expertises)
    assert len(prompt_with_fallback) > len(prompt_without_fallback)
    # And specifically should contain monetary content
    # (because "selic" is a trigger_keyword in monetary_analysis.md)
    assert "Selic" in prompt_with_fallback


def test_assembler_missing_file_doesnt_crash() -> None:
    """Missing expertise files should be skipped, not raise."""
    assembler = ExpertiseAssembler(EXPERTISES_DIR)
    routing = RoutingDecision(
        expertises=["monetary_analysis", "nonexistent_expertise"],
        confidence=0.9,
        reasoning="test",
    )

    # Should not raise
    prompt = assembler.assemble(routing)
    assert "Selic" in prompt  # monetary loaded
    # Nonexistent silently skipped


def test_assembler_dir_must_exist() -> None:
    """Constructor should fail if expertises directory is missing."""
    with pytest.raises(FileNotFoundError):
        ExpertiseAssembler(Path("/nonexistent/path"))
