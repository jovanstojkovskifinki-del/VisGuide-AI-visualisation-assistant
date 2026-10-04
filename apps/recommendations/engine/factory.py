"""
Chooses the active VisualizationRecommendation implementation based on
the RECOMMENDATION_ENGINE Django setting ("rule_based" or "ai"). This is
the single wiring point RecommendationService depends on — switching
engines is a settings/env-var change, never a code change to
RecommendationService, views, or serializers.
"""

from django.conf import settings

from apps.core.interfaces.visualization_recommendation import VisualizationRecommendation
from apps.recommendations.engine.rule_based_engine import RuleBasedRecommendationEngine


def get_default_engine() -> VisualizationRecommendation:
    engine_choice = getattr(settings, "RECOMMENDATION_ENGINE", "rule_based")

    if engine_choice == "ai":
        from apps.recommendations.engine.ai_engine import AIRecommendationEngine
        from apps.recommendations.engine.ollama_service import OllamaRecommendationService

        ai_service = OllamaRecommendationService(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
        )
        return AIRecommendationEngine(ai_service)

    return RuleBasedRecommendationEngine()