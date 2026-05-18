"""Actors — the seven components of the m3xabr-core query pipeline.

Each actor has a single responsibility and conforms to the schemas in
m3xabr_core.schemas. Swap individual actor implementations to customize.
"""

from m3xabr_core.actors.agent_hub import AgentHub
from m3xabr_core.actors.assembler import ExpertiseAssembler
from m3xabr_core.actors.classifier import Classifier
from m3xabr_core.actors.evaluator import Evaluator
from m3xabr_core.actors.retriever import Retriever
from m3xabr_core.actors.router import ExpertiseRouter
from m3xabr_core.actors.synthesizer import Synthesizer

__all__ = [
    "Classifier",
    "ExpertiseRouter",
    "ExpertiseAssembler",
    "AgentHub",
    "Retriever",
    "Synthesizer",
    "Evaluator",
]
