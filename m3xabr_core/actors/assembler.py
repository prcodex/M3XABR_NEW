"""Actor 2 — Expertise Assembler.

Replaces the monolithic `_load_soul()` of the previous architecture.
No LLM call — pure file ops. Reads the expertise files specified by
the routing decision and concatenates them into a single system prompt.

Conservative fallback: when the router's confidence is below threshold,
the assembler loads additional expertises matching trigger keywords
from the classifier output.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from m3xabr_core.schemas import ClassifierOutput, RoutingDecision


class ExpertiseAssembler:
    """Actor 2 — composes the system prompt from expertise files."""

    def __init__(
        self,
        expertises_dir: Path | None = None,
        confidence_threshold: float = 0.7,
    ) -> None:
        if expertises_dir is None:
            expertises_dir = (
                Path(__file__).parent.parent.parent / "expertises"
            )
        self._dir = Path(expertises_dir)
        self.confidence_threshold = confidence_threshold

        if not self._dir.exists():
            raise FileNotFoundError(f"Expertises directory not found: {self._dir}")

    def assemble(
        self,
        routing: RoutingDecision,
        classifier_output: ClassifierOutput | None = None,
    ) -> str:
        """Concatenate the expertise files in dependency order.

        Order: kernel → scope_filter → expertises (in routing order).
        Files are separated by section headers for synthesizer
        legibility.
        """
        files_to_load = routing.all_files()

        # Conservative fallback — if low confidence, load extra expertises
        # matching trigger keywords from classifier output
        if (
            routing.confidence < self.confidence_threshold
            and classifier_output is not None
        ):
            extra = self._find_keyword_matches(
                classifier_output,
                already_loaded=set(routing.expertises),
            )
            files_to_load.extend(extra)

        parts = []
        for filename in files_to_load:
            path = self._dir / f"{filename}.md"
            if not path.exists():
                # Skip missing files rather than crash — production
                # systems should log this
                continue
            body = self._strip_frontmatter(path.read_text(encoding="utf-8"))
            parts.append(body)
            parts.append("")  # blank line between sections

        return "\n".join(parts).strip()

    @staticmethod
    def _strip_frontmatter(content: str) -> str:
        """Remove YAML frontmatter from an expertise file."""
        if not content.startswith("---"):
            return content
        # Find the closing ---
        rest = content[3:]
        end = rest.find("---")
        if end == -1:
            return content
        return rest[end + 3 :].lstrip()

    def _find_keyword_matches(
        self,
        classifier_output: ClassifierOutput,
        already_loaded: set[str],
    ) -> list[str]:
        """Find expertises whose trigger_keywords or trigger_entities match.

        Used as conservative fallback when router confidence is low.
        """
        matches = []
        query_terms = set(
            t.lower()
            for t in classifier_output.entities_mentioned
            + classifier_output.topics
        )

        for path in sorted(self._dir.glob("*.md")):
            name = path.stem
            if name in already_loaded or name in {
                "m3xabr_kernel",
                "scope_filter_brazil",
            }:
                continue

            frontmatter = self._parse_frontmatter(path)
            triggers = set()
            triggers.update(
                str(t).lower() for t in frontmatter.get("trigger_keywords", [])
            )
            triggers.update(
                str(t).lower() for t in frontmatter.get("trigger_entities", [])
            )

            if query_terms & triggers:
                matches.append(name)

        # Cap at 3 additional expertises (~2400 extra tokens max)
        return matches[:3]

    @staticmethod
    def _parse_frontmatter(path: Path) -> dict:
        """Extract YAML frontmatter from an expertise file."""
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return {}
        rest = content[3:]
        end = rest.find("---")
        if end == -1:
            return {}
        try:
            return yaml.safe_load(rest[:end]) or {}
        except yaml.YAMLError:
            return {}
