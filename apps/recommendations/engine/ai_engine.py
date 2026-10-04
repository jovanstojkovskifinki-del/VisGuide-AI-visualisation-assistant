"""
AIRecommendationEngine — LLM-backed implementation of
VisualizationRecommendation, delegating to an injected
AIRecommendationService (OllamaRecommendationService in practice).

Implements the exact same interface as RuleBasedRecommendationEngine,
so RecommendationService, views, and serializers need zero changes to
use this instead — only the dependency-injection wiring
(apps/recommendations/engine/factory.py) changes.
"""

import logging
from typing import Any

from apps.analysis.models import ColumnProfile, DatasetProfile
from apps.core.enums import VisualizationType
from apps.core.interfaces.ai_recommendation_service import AIRecommendationService
from apps.core.interfaces.visualization_recommendation import (
    RecommendationResult,
    VisualizationRecommendation,
)

logger = logging.getLogger(__name__)

_VALID_TYPES = {choice.value for choice in VisualizationType}


class AIRecommendationEngine(VisualizationRecommendation[DatasetProfile]):
    def __init__(self, ai_service: AIRecommendationService):
        self._ai_service = ai_service

    def recommend(self, profile: DatasetProfile) -> RecommendationResult:
        payload = self._profile_to_payload(profile)

        try:
            raw = self._ai_service.suggest(payload)
            return self._parse_response(raw)
        except Exception as exc:  # noqa: BLE001 - any backend/parsing failure
            # A flaky local model or an unparseable response should never
            # break the API — fall back to a safe, low-confidence TABLE
            # recommendation rather than propagating the error.
            logger.warning("AI recommendation failed, falling back to TABLE: %s", exc)
            return RecommendationResult(
                visualization_type=VisualizationType.TABLE,
                reasoning=f"AI recommendation unavailable ({exc}); falling back to a table view.",
                confidence=0.1,
                matched_rule=None,
            )

    @staticmethod
    def _profile_to_payload(profile: DatasetProfile) -> dict[str, Any]:
        columns: list[ColumnProfile] = list(profile.column_profiles.all())
        return {
            "row_count": getattr(profile.dataset, "row_count", None),
            "duplicate_row_count": profile.duplicate_row_count,
            "has_correlation_matrix": profile.correlation_matrix is not None,
            "columns": [
                {
                    "name": cp.column_name,
                    "type": cp.detected_type,
                    "missing_pct": cp.missing_pct,
                    "unique_count": cp.unique_count,
                }
                for cp in columns
            ],
        }

    @staticmethod
    def _parse_response(raw: dict[str, Any]) -> RecommendationResult:
        viz_type = raw.get("visualization_type")
        if viz_type not in _VALID_TYPES:
            raise ValueError(f"Model returned an unrecognized visualization_type: {viz_type!r}")

        return RecommendationResult(
            visualization_type=VisualizationType(viz_type),
            reasoning=raw.get("reasoning", ""),
            confidence=float(raw.get("confidence", 0.5)),
            matched_rule=None,
            suggested_axes=raw.get("suggested_axes") or {},
            metadata={"engine": "ollama"},
        )