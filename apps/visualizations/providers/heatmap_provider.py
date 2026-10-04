from typing import Any

from apps.analysis.models import DatasetProfile
from apps.core.enums import VisualizationType
from apps.core.interfaces.visualization_provider import VisualizationProvider
from apps.core.interfaces.visualization_recommendation import RecommendationResult
from apps.visualizations.providers._helpers import base_metadata


class HeatmapProvider(VisualizationProvider):
    @property
    def visualization_type(self) -> VisualizationType:
        return VisualizationType.HEATMAP

    def build_config(self, profile: DatasetProfile, recommendation: RecommendationResult) -> dict[str, Any]:
        columns = recommendation.suggested_axes.get("columns", [])
        return {
            "visualizationType": self.visualization_type,
            "title": "Correlation Heatmap",
            "xAxis": {"column": None, "label": "Columns", "type": None, "categories": columns},
            "yAxis": {"column": None, "label": "Columns", "type": None, "categories": columns},
            "filters": [],
            "metadata": {
                **base_metadata(profile, recommendation),
                "correlationMatrix": profile.correlation_matrix,
            },
            "options": {"colorScale": "RdBu", "showValues": True},
        }
