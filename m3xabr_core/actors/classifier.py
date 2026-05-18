"""Actor 1 — Classifier.

Reads the raw user query and extracts structured metadata: query type,
time window, entities mentioned, topics, language. Cheap (Haiku) call
that downstream actors depend on.
"""

from __future__ import annotations

import json
from pathlib import Path

from m3xabr_core.backends.llm import LLMBackend
from m3xabr_core.schemas import ClassifierOutput


class Classifier:
    """Actor 1 — extracts query metadata via Haiku."""

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
                / "classifier_prompt.md"
            )
        self._prompt = prompt_path.read_text(encoding="utf-8")

    def classify(self, query: str) -> ClassifierOutput:
        """Extract metadata from a query."""
        response = self._llm.complete(
            model=self._model,
            system=self._prompt,
            user=query,
            max_tokens=512,
            temperature=0.0,
        )

        parsed = self._parse_json(response)
        return ClassifierOutput.model_validate(parsed)

    @staticmethod
    def _parse_json(text: str) -> dict:
        """Tolerant JSON extraction — strips ```json fences and stray prose."""
        cleaned = text.strip()
        if cleaned.startswith("```"):
            # remove first fence line + closing fence
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1] if len(lines) > 2 else lines)
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        # If there's prose before/after, find the JSON braces
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            cleaned = cleaned[start : end + 1]

        return json.loads(cleaned)
