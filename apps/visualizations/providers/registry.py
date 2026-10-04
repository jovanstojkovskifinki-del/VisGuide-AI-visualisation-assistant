"""
ProviderRegistry maps VisualizationType -> VisualizationProvider instance.

This is the concrete Open/Closed seam described in the architecture:
adding a new chart type (or, later, a Scene3DProvider for the 3D module)
means writing one new VisualizationProvider class and adding one line to
DEFAULT_PROVIDERS below — no existing provider or service code changes.
"""

from apps.core.enums import VisualizationType
from apps.core.exceptions import UnsupportedVisualizationTypeError
from apps.core.interfaces.visualization_provider import VisualizationProvider
from apps.visualizations.providers.bar_chart_provider import BarChartProvider
from apps.visualizations.providers.geo_map_provider import GeoMapProvider
from apps.visualizations.providers.heatmap_provider import HeatmapProvider
from apps.visualizations.providers.histogram_provider import HistogramProvider
from apps.visualizations.providers.line_chart_provider import LineChartProvider
from apps.visualizations.providers.scatter_provider import ScatterProvider
from apps.visualizations.providers.table_provider import TableProvider

DEFAULT_PROVIDERS: list[VisualizationProvider] = [
    LineChartProvider(),
    BarChartProvider(),
    ScatterProvider(),
    HistogramProvider(),
    HeatmapProvider(),
    GeoMapProvider(),
    TableProvider(),
    # Future: Scene3DProvider() once the 3D module exists — register here,
    # nowhere else.
]


class ProviderRegistry:
    def __init__(self, providers: list[VisualizationProvider] | None = None):
        providers = providers if providers is not None else DEFAULT_PROVIDERS
        self._providers: dict[VisualizationType, VisualizationProvider] = {
            provider.visualization_type: provider for provider in providers
        }

    def get(self, visualization_type: VisualizationType) -> VisualizationProvider:
        provider = self._providers.get(visualization_type)
        if provider is None:
            raise UnsupportedVisualizationTypeError(
                f"No VisualizationProvider registered for '{visualization_type}'."
            )
        return provider

    def register(self, provider: VisualizationProvider) -> None:
        """Allows tests or future modules to register providers dynamically."""
        self._providers[provider.visualization_type] = provider
