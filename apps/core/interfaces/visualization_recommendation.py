"""
VisualizationRecommendation is the single seam the rest of the system talks
to for "what chart should this data become?"

`RuleBasedRecommendationEngine` implements it today. A future
`AIRecommendationEngine` (backed by a local Ollama model through
`AIRecommendationService`) will implement the exact same interface, so
`RecommendationService` and everything above it never need to change when
the engine is swapped — only the dependency-injection wiring does.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from apps.core.enums import VisualizationType

TProfile = TypeVar("TProfile")


@dataclass(frozen=True)
class RecommendationResult:
    """
    The output of any recommendation engine, regardless of whether a rule
    or an AI model produced it.
    """

    visualization_type: VisualizationType
    reasoning: str
    confidence: float = 1.0
    matched_rule: str | None = None
    suggested_axes: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class VisualizationRecommendation(ABC, Generic[TProfile]):
    """Recommends a visualization approach given a content profile."""

    @abstractmethod
    def recommend(self, profile: TProfile) -> RecommendationResult:
        """
        Inspect `profile` (e.g. a DatasetProfile) and return the single
        best RecommendationResult. Implementations that can't produce any
        confident match should fall back to `VisualizationType.TABLE`
        rather than raising, so downstream config generation always has
        something to render.
        """
        raise NotImplementedError
