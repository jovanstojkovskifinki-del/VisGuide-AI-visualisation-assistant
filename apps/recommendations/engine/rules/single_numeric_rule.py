from apps.analysis.models import DatasetProfile
from apps.core.enums import ColumnType, VisualizationType
from apps.core.interfaces.visualization_recommendation import RecommendationResult
from apps.recommendations.engine.rule import Rule
from apps.recommendations.engine.rules._helpers import columns_of_type


class SingleNumericRule(Rule):
    """IF exactly one numerical column and nothing stronger matched -> Histogram."""

    name = "single_numeric"

    def matches(self, profile: DatasetProfile) -> bool:
        numeric_cols = columns_of_type(profile, ColumnType.NUMERIC)
        return len(numeric_cols) >= 1

    def build_recommendation(self, profile: DatasetProfile) -> RecommendationResult:
        numeric_col = columns_of_type(profile, ColumnType.NUMERIC)[0]
        return RecommendationResult(
            visualization_type=VisualizationType.HISTOGRAM,
            reasoning=(
                f"Detected numeric column '{numeric_col.column_name}' with no "
                "stronger pairing signal — a histogram best shows its "
                "distribution."
            ),
            confidence=0.6,
            matched_rule=self.name,
            suggested_axes={"x": numeric_col.column_name},
        )
