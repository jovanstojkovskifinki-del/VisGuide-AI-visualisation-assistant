from apps.analysis.models import DatasetProfile
from apps.core.enums import VisualizationType
from apps.core.interfaces.visualization_recommendation import RecommendationResult
from apps.recommendations.engine.rule import Rule


class MatrixRule(Rule):
    """
    IF a correlation matrix was computed (i.e. 3+ numeric columns, making
    a pairwise-relationship view more informative than a single scatter)
    -> Heatmap.

    Checked after GeoRule (lat/lon takes priority over a generic matrix
    view) but before the numeric-column-count rules below, since a
    correlation matrix is a stronger, more specific signal than "two
    numeric columns exist."
    """

    name = "correlation_matrix"

    #: Below this many numeric columns, a scatter plot is more useful
    #: than a heatmap of a tiny matrix.
    MIN_COLUMNS_FOR_HEATMAP = 3

    def matches(self, profile: DatasetProfile) -> bool:
        matrix = profile.correlation_matrix
        if not matrix or not matrix.get("columns"):
            return False
        return len(matrix["columns"]) >= self.MIN_COLUMNS_FOR_HEATMAP

    def build_recommendation(self, profile: DatasetProfile) -> RecommendationResult:
        columns = profile.correlation_matrix["columns"]
        return RecommendationResult(
            visualization_type=VisualizationType.HEATMAP,
            reasoning=(
                f"Found {len(columns)} numeric columns with a computed correlation "
                "matrix — a heatmap best shows pairwise relationships across many "
                "variables at once."
            ),
            confidence=0.85,
            matched_rule=self.name,
            suggested_axes={"columns": columns},
        )
