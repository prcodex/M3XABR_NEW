"""Actor 1.5 — Expertise Router.

The architectural centerpiece. Reads the query and classifier output
and decides which expertise files to load. Picks 1-3 expertises plus
the always-loaded kernel and scope filter.

Conservative fallback: if confidence is below threshold, the assembler
will load additional expertises matching trigger keywords.
"""

from __future__ import annotations

import json
from pathlib import Path

from m3xabr_core.backends.llm import LLMBackend
from m3xabr_core.schemas import ClassifierOutput, RoutingDecision


class ExpertiseRouter:
    """Actor 1.5 — picks expertises based on query semantics."""

    def __init__(
        self,
        llm: LLMBackend,
        model: str = "claude-haiku-4-5",
        prompt_path: Path | None = None,
        confidence_threshold: float = 0.7,
    ) -> None:
        self._llm = llm
        self._model = model
        if prompt_path is None:
            prompt_path = (
                Path(__file__).parent.parent.parent
                / "config"
                / "router_prompt.md"
            )
        self._prompt = prompt_path.read_text(encoding="utf-8")
        self.confidence_threshold = confidence_threshold

    def route(
        self,
        query: str,
        classifier_output: ClassifierOutput,
    ) -> RoutingDecision:
        """Decide which expertises to load.

        The router prompt is concatenated with the user query and the
        classifier output as context.
        """
        user_message = self._build_user_message(query, classifier_output)

        response = self._llm.complete(
            model=self._model,
            system=self._prompt,
            user=user_message,
            max_tokens=512,
            temperature=0.0,
        )

        parsed = self._parse_json(response)
        decision = RoutingDecision.model_validate(parsed)
        return decision

    @staticmethod
    def _build_user_message(
        query: str, classifier_output: ClassifierOutput
    ) -> str:
        return (
            f"Query: {query}\n\n"
            f"Classifier output:\n"
            f"  query_type: {classifier_output.query_type}\n"
            f"  time_window: {classifier_output.time_window}\n"
            f"  entities_mentioned: {classifier_output.entities_mentioned}\n"
            f"  topics: {classifier_output.topics}\n"
            f"  language: {classifier_output.language}"
        )

    @staticmethod
    def _parse_json(text: str) -> dict:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1] if len(lines) > 2 else lines)
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            cleaned = cleaned[start : end + 1]
        return json.loads(cleaned)
