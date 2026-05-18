"""Actor 7 — Evaluator.

Scores the synthesized response against a Portuguese rubric. Triggers
auto-regen at 5.0 ≤ score < 7.0 with an improvement hint.

Live regen gate logic:
- score >= 7.0 → deliver
- 5.0 <= score < 7.0 → regen with hint; adopt regen only if score improves
- score < 5.0 → deliver anyway, log loudly
"""

from __future__ import annotations

import json
from pathlib import Path

from m3xabr_core.backends.llm import LLMBackend
from m3xabr_core.schemas import EvaluationResult


class Evaluator:
    """Actor 7 — scores responses via Haiku with PT rubric."""

    def __init__(
        self,
        llm: LLMBackend,
        model: str = "claude-haiku-4-5",
        prompt_path: Path | None = None,
    ) -> None:
        self._llm = llm
        self._model = model
        if prompt_path is None:
            prompt_path = (
                Path(__file__).parent.parent.parent
                / "config"
                / "evaluator_prompt.md"
            )
        self._prompt = prompt_path.read_text(encoding="utf-8")

    def evaluate(self, query: str, response: str) -> EvaluationResult:
        """Score a query/response pair."""
        user_message = (
            f"=== QUERY ===\n{query}\n\n"
            f"=== RESPONSE ===\n{response}\n\n"
            f"=== EVALUATE ==="
        )

        eval_response = self._llm.complete(
            model=self._model,
            system=self._prompt,
            user=user_message,
            max_tokens=1024,
            temperature=0.0,
        )

        parsed = self._parse_json(eval_response)
        return EvaluationResult.model_validate(parsed)

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
