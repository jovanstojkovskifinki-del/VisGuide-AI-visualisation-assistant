from apps.analysis.models import DatasetProfile
from apps.core.enums import ColumnType, VisualizationType
from apps.core.interfaces.visualization_recommendation import RecommendationResult
from apps.recommendations.engine.rule import Rule
from apps.recommendations.engine.rules._helpers import columns_of_type


class DatetimeNumericRule(Rule):
    """IF datetime + numerical columns present -> Line Chart."""

    name = "datetime_numeric"

    def matches(self, profile: DatasetProfile) -> bool:
        datetime_cols = columns_of_type(profile, ColumnType.DATETIME)
        numeric_cols = columns_of_type(profile, ColumnType.NUMERIC)
        return bool(datetime_cols) and bool(numeric_cols)

    def build_recommendation(self, profile: DatasetProfile) -> RecommendationResult:
        datetime_col = columns_of_type(profile, ColumnType.DATETIME)[0]
        numeric_col = columns_of_type(profile, ColumnType.NUMERIC)[0]
        return RecommendationResult(
            visualization_type=VisualizationType.LINE_CHART,
            reasoning=(
                f"Detected datetime column '{datetime_col.column_name}' alongside "
                f"numeric column '{numeric_col.column_name}' — a line chart best "
                "shows change over time."
            ),
            confidence=0.9,
            matched_rule=self.name,
            suggested_axes={"x": datetime_col.column_name, "y": numeric_col.column_name},
        )
