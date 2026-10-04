"""
VisualizationProvider is the contract every chart-config builder (and,
later, the 3D scene builder) implements. `ProviderRegistry`
(apps/visualizations/providers/registry.py) maps a VisualizationType to the
provider that handles it — adding a new visualization type means adding a
new provider and registering it, never editing an existing provider.
"""

from abc import ABC, abstractmethod
from typing import Any

from apps.core.enums import VisualizationType
from apps.core.interfaces.visualization_recommendation import RecommendationResult


class VisualizationProvider(ABC):
    """Builds a standardized visualization config for one visualization type."""

    @property
    @abstractmethod
    def visualization_type(self) -> VisualizationType:
        """The single VisualizationType this provider handles."""
        raise NotImplementedError

    def supports(self, visualization_type: VisualizationType) -> bool:
        return visualization_type == self.visualization_type

    @abstractmethod
    def build_config(self, profile: Any, recommendation: RecommendationResult) -> dict[str, Any]:
        """
        Build the standardized config object:

            {
                "visualizationType": ...,
                "title": ...,
                "xAxis": {...} | None,
                "yAxis": {...} | None,
                "filters": [...],
                "metadata": {...},
                "options": {...},
            }

        `profile` is typically a DatasetProfile, but the type is left as
        `Any` deliberately: a future `Scene3DProvider` will receive a
        ConceptProfile instead and return a SceneDescription-shaped dict
        through this exact same method signature.
        """
        raise NotImplementedError
