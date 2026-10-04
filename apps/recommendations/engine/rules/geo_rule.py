from apps.analysis.models import DatasetProfile
from apps.core.enums import ColumnType, VisualizationType
from apps.core.interfaces.visualization_recommendation import RecommendationResult
from apps.recommendations.engine.rule import Rule
from apps.recommendations.engine.rules._helpers import columns_of_type


class GeoRule(Rule):
    """
    IF latitude + longitude columns present -> Geographic Map.

    Checked before every other rule because latitude/longitude columns
    are also numeric, and would otherwise be caught by TwoNumericRule
    (scatter) or SingleNumericRule (histogram) first.
    """

    name = "geo_lat_lon"

    def matches(self, profile: DatasetProfile) -> bool:
        lat_cols = columns_of_type(profile, ColumnType.LATITUDE)
        lon_cols = columns_of_type(profile, ColumnType.LONGITUDE)
        return bool(lat_cols) and bool(lon_cols)

    def build_recommendation(self, profile: DatasetProfile) -> RecommendationResult:
        lat_col = columns_of_type(profile, ColumnType.LATITUDE)[0]
        lon_col = columns_of_type(profile, ColumnType.LONGITUDE)[0]
        return RecommendationResult(
            visualization_type=VisualizationType.GEOGRAPHIC_MAP,
            reasoning=(
                f"Detected latitude column '{lat_col.column_name}' and longitude "
                f"column '{lon_col.column_name}' — geographic coordinates are best "
                "shown on a map."
            ),
            confidence=0.95,
            matched_rule=self.name,
            suggested_axes={"latitude": lat_col.column_name, "longitude": lon_col.column_name},
        )
