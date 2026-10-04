from apps.analysis.models import DatasetProfile
from apps.core.enums import VisualizationType
from apps.core.interfaces.visualization_recommendation import (
    RecommendationResult,
    VisualizationRecommendation,
)
from apps.recommendations.engine.rule import Rule
from apps.recommendations.engine.rules import (
    CategoricalNumericRule,
    DatetimeNumericRule,
    GeoRule,
    MatrixRule,
    SingleNumericRule,
    TwoNumericRule,
)

#: Priority order matters: earlier rules represent stronger, more specific
#: signals and are checked first. Geo and Matrix are checked before the
#: generic numeric-count rules because latitude/longitude/correlation
#: columns are *also* numeric and would otherwise be caught by
#: TwoNumericRule or SingleNumericRule first.
DEFAULT_RULE_ORDER: list[type[Rule]] = [
    GeoRule,
    MatrixRule,
    DatetimeNumericRule,
    CategoricalNumericRule,
    TwoNumericRule,
    SingleNumericRule,
]


class RuleBasedRecommendationEngine(VisualizationRecommendation[DatasetProfile]):
    """
    Evaluates an ordered list of Rule objects and returns the first match.
    Falls back to VisualizationType.TABLE if no rule matches, so callers
    always get a usable result rather than an exception.

    This class implements `VisualizationRecommendation` — the same
    interface a future `AIRecommendationEngine` will implement — so
    `RecommendationService` can be pointed at either without any change
    to its own code.
    """

    def __init__(self, rules: list[Rule] | None = None):
        self._rules = rules or [rule_cls() for rule_cls in DEFAULT_RULE_ORDER]

    def recommend(self, profile: DatasetProfile) -> RecommendationResult:
        for rule in self._rules:
            if rule.matches(profile):
                return rule.build_recommendation(profile)

        return RecommendationResult(
            visualization_type=VisualizationType.TABLE,
            reasoning="No rule matched this dataset's column profile; falling back to a table view.",
            confidence=0.3,
            matched_rule=None,
        )
