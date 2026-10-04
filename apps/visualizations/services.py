from apps.analysis.models import DatasetProfile
from apps.core.interfaces.visualization_recommendation import RecommendationResult
from apps.visualizations.models import VisualizationConfig
from apps.visualizations.providers.registry import ProviderRegistry


class VisualizationConfigService:
    """
    Looks up the right provider via ProviderRegistry, builds the
    standardized config dict, and persists it. This is the only class
    views call for config generation — provider selection logic lives
    entirely in ProviderRegistry, never here or in a view.
    """

    def __init__(self, registry: ProviderRegistry | None = None):
        self._registry = registry or ProviderRegistry()

    def generate(
        self, profile: DatasetProfile, recommendation: RecommendationResult
    ) -> VisualizationConfig:
        provider = self._registry.get(recommendation.visualization_type)
        config_dict = provider.build_config(profile, recommendation)

        return VisualizationConfig.objects.create(
            dataset_id=profile.dataset_id,
            visualization_type=config_dict["visualizationType"],
            title=config_dict["title"],
            x_axis=config_dict.get("xAxis"),
            y_axis=config_dict.get("yAxis"),
            filters=config_dict.get("filters", []),
            metadata=config_dict.get("metadata", {}),
            options=config_dict.get("options", {}),
        )
