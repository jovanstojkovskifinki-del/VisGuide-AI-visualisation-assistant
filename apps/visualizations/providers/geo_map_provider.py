from typing import Any

from apps.analysis.models import DatasetProfile
from apps.core.enums import VisualizationType
from apps.core.interfaces.visualization_provider import VisualizationProvider
from apps.core.interfaces.visualization_recommendation import RecommendationResult
from apps.visualizations.providers._helpers import axis_spec, base_metadata


class GeoMapProvider(VisualizationProvider):
    @property
    def visualization_type(self) -> VisualizationType:
        return VisualizationType.GEOGRAPHIC_MAP

    def build_config(self, profile: DatasetProfile, recommendation: RecommendationResult) -> dict[str, Any]:
        axes = recommendation.suggested_axes
        return {
            "visualizationType": self.visualization_type,
            "title": "Geographic Distribution",
            "xAxis": axis_spec(profile, axes["longitude"]),
            "yAxis": axis_spec(profile, axes["latitude"]),
            "filters": [],
            "metadata": base_metadata(profile, recommendation),
            "options": {"mapStyle": "light", "clustering": True},
        }
