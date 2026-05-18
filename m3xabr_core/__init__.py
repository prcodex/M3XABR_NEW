"""m3xabr-core: expertise-composition architecture for a Brazilian intelligence agent."""

__version__ = "0.1.0"

from m3xabr_core.pipeline import Pipeline
from m3xabr_core.schemas import (
    ClassifierOutput,
    RoutingDecision,
    AgentContext,
    RetrievedDoc,
    SynthesizerInput,
    EvaluationResult,
    PipelineResult,
)

__all__ = [
    "Pipeline",
    "ClassifierOutput",
    "RoutingDecision",
    "AgentContext",
    "RetrievedDoc",
    "SynthesizerInput",
    "EvaluationResult",
    "PipelineResult",
]
