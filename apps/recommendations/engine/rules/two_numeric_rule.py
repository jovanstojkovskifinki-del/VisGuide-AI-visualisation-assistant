from apps.analysis.models import DatasetProfile
from apps.core.enums import ColumnType, VisualizationType
from apps.core.interfaces.visualization_recommendation import RecommendationResult
from apps.recommendations.engine.rule import Rule
from apps.recommendations.engine.rules._helpers import columns_of_type


class TwoNumericRule(Rule):
    """IF exactly (or at least) two numerical columns, no stronger signal -> Scatter Plot."""

    name = "two_numeric"

    MIN_NUMERIC_COLUMNS = 2

    def matches(self, profile: DatasetProfile) -> bool:
        numeric_cols = columns_of_type(profile, ColumnType.NUMERIC)
        return len(numeric_cols) >= self.MIN_NUMERIC_COLUMNS

    def build_recommendation(self, profile: DatasetProfile) -> RecommendationResult:
        numeric_cols = columns_of_type(profile, ColumnType.NUMERIC)
        x_col, y_col = numeric_cols[0], numeric_cols[1]
        return RecommendationResult(
            visualization_type=VisualizationType.SCATTER_PLOT,
            reasoning=(
                f"Detected multiple numeric columns ('{x_col.column_name}', "
                f"'{y_col.column_name}') — a scatter plot best shows the "
                "relationship between two numeric variables."
            ),
            confidence=0.7,
            matched_rule=self.name,
            suggested_axes={"x": x_col.column_name, "y": y_col.column_name},
        )
