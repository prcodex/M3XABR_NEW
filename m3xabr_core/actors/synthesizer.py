"""Actor 5 — Synthesizer.

Calls Sonnet with the assembled system prompt + dynamic context to
produce the final response. The synthesizer is where the soul +
context + retrieval all come together.

Receives a fully-formed SynthesizerInput and returns the response text.
"""

from __future__ import annotations

from m3xabr_core.backends.llm import LLMBackend
from m3xabr_core.schemas import SynthesizerInput


class Synthesizer:
    """Actor 5 — produces the final response via Sonnet."""

    def __init__(
        self,
        llm: LLMBackend,
        model: str = "claude-sonnet-4-7",
        max_tokens: int = 4096,
    ) -> None:
        self._llm = llm
        self._model = model
        self._max_tokens = max_tokens

    def synthesize(
        self,
        input_data: SynthesizerInput,
        extra_hint: str | None = None,
    ) -> str:
        """Produce a response.

        `extra_hint` is used by the auto-regen path — when the
        evaluator suggests an improvement, the regen pass includes the
        hint as additional context.
        """
        user_payload = self._build_user_payload(input_data, extra_hint)

        response = self._llm.complete(
            model=self._model,
            system=input_data.system_prompt,
            user=user_payload,
            max_tokens=self._max_tokens,
            temperature=0.3,
        )
        return response

    @staticmethod
    def _build_user_payload(
        inp: SynthesizerInput,
        extra_hint: str | None,
    ) -> str:
        """Compose the user-turn payload from dynamic context.

        Layer order (matches m3xabr_core/docs/ARCHITECTURE.md):
        1. DATA WINDOW marker
        2. Agent context (MARKET SNAPSHOT, POLYMARKET, etc.)
        3. Retrieved docs
        4. Health caveats
        5. Session history (if multi-turn)
        6. User query
        7. Optional regen hint
        """
        parts = [f"DATA WINDOW: {inp.time_window}"]

        agent_section = inp.agent_context.to_prompt_section()
        if agent_section:
            parts.append("\n" + agent_section)

        if inp.retrieved_docs:
            parts.append("\n=== RETRIEVED DOCS ===")
            for i, doc in enumerate(inp.retrieved_docs, 1):
                date_str = ""
                if doc.published_at is not None:
                    date_str = f" · {doc.published_at.strftime('%Y-%m-%d')}"
                parts.append(f"\n[{i}] {doc.source}{date_str}")
                parts.append(doc.text)
            parts.append("=== END RETRIEVED DOCS ===\n")

        if inp.health_caveats:
            parts.append(f"\nHEALTH CAVEATS: {inp.health_caveats}")

        if inp.session_history:
            parts.append("\n=== SESSION HISTORY ===")
            for turn in inp.session_history[-10:]:  # last 10 turns max
                role = turn.get("role", "user")
                content = turn.get("content", "")
                parts.append(f"{role.upper()}: {content[:2000]}")
            parts.append("=== END SESSION HISTORY ===\n")

        parts.append(f"\nUSER QUERY: {inp.user_query}")

        if extra_hint:
            parts.append(f"\nIMPROVEMENT HINT FROM EVALUATOR: {extra_hint}")

        return "\n".join(parts)
