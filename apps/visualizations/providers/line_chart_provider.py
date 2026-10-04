from typing import Any

from apps.analysis.models import DatasetProfile
from apps.core.enums import VisualizationType
from apps.core.interfaces.visualization_provider import VisualizationProvider
from apps.core.interfaces.visualization_recommendation import RecommendationResult
from apps.visualizations.providers._helpers import axis_spec, base_metadata


class LineChartProvider(VisualizationProvider):
    @property
    def visualization_type(self) -> VisualizationType:
        return VisualizationType.LINE_CHART

    def build_config(self, profile: DatasetProfile, recommendation: RecommendationResult) -> dict[str, Any]:
        axes = recommendation.suggested_axes
        return {
            "visualizationType": self.visualization_type,
            "title": f"{axes.get('y', 'Value')} over {axes.get('x', 'Time')}",
            "xAxis": axis_spec(profile, axes["x"]),
            "yAxis": axis_spec(profile, axes["y"]),
            "filters": [],
            "metadata": base_metadata(profile, recommendation),
            "options": {"smoothing": False, "showMarkers": False},
        }
