from apps.analysis.models import ColumnProfile, DatasetProfile
from apps.core.enums import ColumnType, VisualizationType
from apps.core.interfaces.visualization_recommendation import RecommendationResult
from apps.recommendations.engine.rule import Rule
from apps.recommendations.engine.rules._helpers import columns_of_type


class CategoricalNumericRule(Rule):
    """
    IF categorical + numerical columns present -> Bar Chart.

    When multiple categorical columns are available, prefers the one with
    the *lowest* cardinality (fewest distinct values) as the grouping
    axis. A column like `student_name` is technically CATEGORICAL (it's
    text, not numeric) but is usually near-unique per row — grouping a
    bar chart by it produces one bar per row, which isn't a useful
    aggregation. A column like `subject` with a handful of repeated
    values is what a bar chart is actually good at summarizing.
    """

    name = "categorical_numeric"

    def matches(self, profile: DatasetProfile) -> bool:
        categorical_cols = columns_of_type(profile, ColumnType.CATEGORICAL)
        numeric_cols = columns_of_type(profile, ColumnType.NUMERIC)
        return bool(categorical_cols) and bool(numeric_cols)

    def build_recommendation(self, profile: DatasetProfile) -> RecommendationResult:
        categorical_col = self._best_grouping_column(profile)
        numeric_col = columns_of_type(profile, ColumnType.NUMERIC)[0]
        return RecommendationResult(
            visualization_type=VisualizationType.BAR_CHART,
            reasoning=(
                f"Detected categorical column '{categorical_col.column_name}' "
                f"alongside numeric column '{numeric_col.column_name}' — a bar "
                "chart best compares values across categories."
            ),
            confidence=0.85,
            matched_rule=self.name,
            suggested_axes={"x": categorical_col.column_name, "y": numeric_col.column_name},
        )

    @staticmethod
    def _best_grouping_column(profile: DatasetProfile) -> ColumnProfile:
        categorical_cols = columns_of_type(profile, ColumnType.CATEGORICAL)
        return min(categorical_cols, key=lambda cp: cp.unique_count)