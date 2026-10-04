"""
Rule is the Strategy-pattern building block RuleBasedRecommendationEngine
composes. One rule per bullet in the architecture's "Recommendation
Engine" spec (datetime+numeric -> line, categorical+numeric -> bar, etc).

Each rule operates on an `analysis.models.DatasetProfile` instance
(with `column_profiles` already prefetched by the caller) and is
self-contained: it decides on its own whether it applies and, if so,
builds the full RecommendationResult — the engine itself contains no
chart-selection logic, only rule ordering and iteration.
"""

from abc import ABC, abstractmethod

from apps.analysis.models import DatasetProfile
from apps.core.interfaces.visualization_recommendation import RecommendationResult


class Rule(ABC):
    #: Used as `matched_rule` in the result and in RecommendationLog —
    #: keep it short and stable, since it's effectively a public identifier.
    name: str = "unnamed_rule"

    @abstractmethod
    def matches(self, profile: DatasetProfile) -> bool:
        raise NotImplementedError

    @abstractmethod
    def build_recommendation(self, profile: DatasetProfile) -> RecommendationResult:
        raise NotImplementedError
