"""
AIRecommendationService is the contract for any LLM backend used to power
`AIRecommendationEngine` (see apps/recommendations/engine/ai_engine.py).

Not implemented in Module 1. `OllamaRecommendationService` will be the
first concrete implementation, calling a locally-hosted Ollama model
(e.g. via http://localhost:11434/api/generate) with the dataset profile
serialized as structured JSON, and parsing the model's structured JSON
reply back into a RecommendationResult.

Keeping this as a narrow, separate interface from VisualizationRecommendation
matters: VisualizationRecommendation is "give me a recommendation for this
profile" (used by RecommendationService). AIRecommendationService is
"talk to a specific AI backend" (used only by AIRecommendationEngine). This
separation means swapping Ollama for another local model, or for a hosted
API, never touches VisualizationRecommendation or its consumers.
"""

from abc import ABC, abstractmethod
from typing import Any


class AIRecommendationService(ABC):
    """Thin contract for a backend capable of suggesting a visualization."""

    @abstractmethod
    def suggest(self, profile_payload: dict[str, Any]) -> dict[str, Any]:
        """
        Send a serialized profile (already converted to plain dict/JSON by
        the caller) to the AI backend and return its structured response
        as a plain dict, e.g.:

            {
                "visualization_type": "LINE_CHART",
                "reasoning": "...",
                "confidence": 0.87,
                "suggested_axes": {"x": "date", "y": "revenue"},
            }

        Implementations own model-specific prompt construction, response
        parsing, and error handling. The caller (AIRecommendationEngine) is
        responsible for converting this dict into a RecommendationResult.
        """
        raise NotImplementedError
