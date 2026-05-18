"""The pipeline orchestrator.

Wires the seven actors together. Caller-facing API: `Pipeline.run(query)`
returns a `PipelineResult` with the final response, score, and
intermediate state for debugging / A-B analysis.
"""

from __future__ import annotations

import time
from pathlib import Path

import yaml

from m3xabr_core.actors import (
    AgentHub,
    Classifier,
    Evaluator,
    ExpertiseAssembler,
    ExpertiseRouter,
    Retriever,
    Synthesizer,
)
from m3xabr_core.backends import (
    AnthropicLLM,
    EmbeddingBackend,
    LanceDBBackend,
    LLMBackend,
    VectorDBBackend,
    VoyageEmbeddings,
)
from m3xabr_core.schemas import (
    PipelineResult,
    SynthesizerInput,
)


class Pipeline:
    """The full 7-actor query pipeline.

    Default construction uses Anthropic + Voyage + LanceDB. Inject
    custom backends or actors to swap any component.
    """

    def __init__(
        self,
        *,
        lancedb_path: str | None = None,
        llm: LLMBackend | None = None,
        embedder: EmbeddingBackend | None = None,
        vector_db: VectorDBBackend | None = None,
        classifier: Classifier | None = None,
        router: ExpertiseRouter | None = None,
        assembler: ExpertiseAssembler | None = None,
        agent_hub: AgentHub | None = None,
        retriever: Retriever | None = None,
        synthesizer: Synthesizer | None = None,
        evaluator: Evaluator | None = None,
        config_path: Path | None = None,
    ) -> None:
        # Load config
        if config_path is None:
            config_path = (
                Path(__file__).parent.parent
                / "config"
                / "retrieval_scoring.yaml"
            )
        self._config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

        # Backends — default to production stack, accept injection for tests
        self._llm = llm or AnthropicLLM()
        self._embedder = embedder or VoyageEmbeddings()

        if vector_db is None:
            if lancedb_path is None:
                raise ValueError(
                    "Either lancedb_path or vector_db must be provided"
                )
            vector_db = LanceDBBackend(lancedb_path)
        self._vector_db = vector_db

        # Actors — wire backends in
        models = self._config["models"]
        self._classifier = classifier or Classifier(
            self._llm, model=models["classifier"]
        )
        self._router = router or ExpertiseRouter(
            self._llm, model=models["router"]
        )
        self._assembler = assembler or ExpertiseAssembler()
        self._agent_hub = agent_hub or AgentHub()
        self._retriever = retriever or Retriever(
            self._embedder, self._vector_db
        )
        self._synthesizer = synthesizer or Synthesizer(
            self._llm, model=models["synthesizer"]
        )
        self._evaluator = evaluator or Evaluator(
            self._llm, model=models["evaluator"]
        )

    def run(
        self,
        query: str,
        session_history: list[dict[str, str]] | None = None,
    ) -> PipelineResult:
        """Run the full pipeline on a single query."""
        timings: dict[str, float] = {}

        # Actor 1 — Classifier
        t0 = time.perf_counter()
        classifier_output = self._classifier.classify(query)
        timings["classifier_ms"] = (time.perf_counter() - t0) * 1000

        # Actor 1.5 — Expertise Router
        t0 = time.perf_counter()
        routing_decision = self._router.route(query, classifier_output)
        timings["router_ms"] = (time.perf_counter() - t0) * 1000

        # Actor 2 — Expertise Assembler (no LLM call)
        t0 = time.perf_counter()
        system_prompt = self._assembler.assemble(
            routing_decision, classifier_output
        )
        timings["assembler_ms"] = (time.perf_counter() - t0) * 1000

        # Actor 3 — Agent Hub (parallel-able but sequential in v0)
        t0 = time.perf_counter()
        agent_context = self._agent_hub.gather(classifier_output)
        timings["agent_hub_ms"] = (time.perf_counter() - t0) * 1000

        # Actor 4 — Retriever
        t0 = time.perf_counter()
        retrieved_docs = self._retriever.retrieve(query, classifier_output)
        timings["retriever_ms"] = (time.perf_counter() - t0) * 1000

        # Build synthesizer input
        synth_input = SynthesizerInput(
            system_prompt=system_prompt,
            user_query=query,
            time_window=classifier_output.time_window,
            agent_context=agent_context,
            retrieved_docs=retrieved_docs,
            session_history=session_history or [],
        )

        # Actor 5 — Synthesizer
        t0 = time.perf_counter()
        response = self._synthesizer.synthesize(synth_input)
        timings["synthesizer_ms"] = (time.perf_counter() - t0) * 1000

        # Actor 7 — Evaluator (and conditional regen)
        t0 = time.perf_counter()
        evaluation = self._evaluator.evaluate(query, response)
        timings["evaluator_ms"] = (time.perf_counter() - t0) * 1000

        regen_triggered = False
        if 5.0 <= evaluation.score < 7.0 and evaluation.improvement_hint:
            regen_triggered = True
            regen_response = self._synthesizer.synthesize(
                synth_input, extra_hint=evaluation.improvement_hint
            )
            regen_eval = self._evaluator.evaluate(query, regen_response)
            if regen_eval.score > evaluation.score:
                # Adopt regen
                response = regen_response
                evaluation = regen_eval

        return PipelineResult(
            query=query,
            response=response,
            score=evaluation.score,
            classifier_output=classifier_output,
            routing_decision=routing_decision,
            retrieved_doc_count=len(retrieved_docs),
            agent_blocks_count=len(agent_context.blocks),
            estimated_system_tokens=len(system_prompt) // 4,
            estimated_total_input_tokens=synth_input.estimated_tokens(),
            evaluation=evaluation,
            regen_triggered=regen_triggered,
            timing_ms=timings,
        )
