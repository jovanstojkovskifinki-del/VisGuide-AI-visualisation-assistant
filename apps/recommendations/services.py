from apps.analysis.models import DatasetProfile
from apps.core.enums import RecommendationEngineType
from apps.core.interfaces.visualization_recommendation import (
    RecommendationResult,
    VisualizationRecommendation,
)
from apps.recommendations.engine.ai_engine import AIRecommendationEngine
from apps.recommendations.engine.factory import get_default_engine
from apps.recommendations.models import RecommendationLog


class RecommendationService:
    """
    The one place the rest of the system asks "what visualization fits
    this dataset?". Takes a `VisualizationRecommendation` implementation
    as a constructor dependency, defaulting to whichever engine
    `get_default_engine()` resolves to based on the RECOMMENDATION_ENGINE
    setting (rule-based or Ollama-backed AI).
    """

    def __init__(self, engine: VisualizationRecommendation | None = None):
        self._engine = engine or get_default_engine()
        self._engine_type = (
            RecommendationEngineType.AI
            if isinstance(self._engine, AIRecommendationEngine)
            else RecommendationEngineType.RULE_BASED
        )

    def get_recommendation(self, profile: DatasetProfile) -> RecommendationResult:
        result = self._engine.recommend(profile)
        RecommendationLog.objects.create(
            dataset_id=profile.dataset_id,
            engine_used=self._engine_type,
            matched_rule=result.matched_rule,
            recommended_type=result.visualization_type,
            confidence=result.confidence,
            reasoning=result.reasoning,
        )
        return result