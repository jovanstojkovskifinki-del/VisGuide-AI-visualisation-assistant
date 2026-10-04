from typing import Any

from apps.analysis.models import DatasetProfile
from apps.core.enums import VisualizationType
from apps.core.interfaces.visualization_provider import VisualizationProvider
from apps.core.interfaces.visualization_recommendation import RecommendationResult
from apps.visualizations.providers._helpers import base_metadata


class TableProvider(VisualizationProvider):
    """
    Fallback provider for when no chart-specific rule matched
    (RuleBasedRecommendationEngine's default). Ensures the config
    generation step never fails outright — the frontend can always at
    least render a data table.
    """

    @property
    def visualization_type(self) -> VisualizationType:
        return VisualizationType.TABLE

    def build_config(self, profile: DatasetProfile, recommendation: RecommendationResult) -> dict[str, Any]:
        columns = [cp.column_name for cp in profile.column_profiles.all()]
        return {
            "visualizationType": self.visualization_type,
            "title": "Data Table",
            "xAxis": None,
            "yAxis": None,
            "filters": [],
            "metadata": base_metadata(profile, recommendation),
            "options": {"columns": columns, "pageSize": 25},
        }
