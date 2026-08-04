"""Prompt Registry (EDS §8).

Versioned prompt artifacts, model compatibility checking, and the
resolution policy for selecting the correct prompt version.
"""

from docuwing_engine.prompts.registry import (
    ModelCompatibility,
    PromptArtifact,
    PromptRegistry,
    PromptTemplate,
)

__all__ = [
    "ModelCompatibility",
    "PromptArtifact",
    "PromptRegistry",
    "PromptTemplate",
]
