"""
OllamaRecommendationService — concrete AIRecommendationService implementation
backed by a locally-running Ollama server.

Talks to Ollama's /api/generate endpoint with `format: "json"`, which
constrains the model's output to valid JSON, then parses that into the
plain dict AIRecommendationEngine expects. See the project README's
"Connecting to a local Ollama LLM" section for how to run the server
and pull a model.
"""

import json
import logging
from typing import Any

import requests

from apps.core.interfaces.ai_recommendation_service import AIRecommendationService

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a data visualization expert. Given a JSON description of a dataset's columns and their detected types, recommend the single best visualization type.

Respond with ONLY a JSON object in exactly this shape, no other text, no markdown code fences:
{
  "visualization_type": one of "LINE_CHART", "BAR_CHART", "SCATTER_PLOT", "HISTOGRAM", "HEATMAP", "GEOGRAPHIC_MAP", "CHOROPLETH_MAP", "TABLE",
  "reasoning": "one or two sentences explaining why",
  "confidence": a number between 0 and 1,
  "suggested_axes": an object whose keys depend on the chart type -
      LINE_CHART/BAR_CHART/SCATTER_PLOT: {"x": "<column_name>", "y": "<column_name>"}
      HISTOGRAM: {"x": "<column_name>"}
      GEOGRAPHIC_MAP: {"latitude": "<column_name>", "longitude": "<column_name>"}
      HEATMAP: {"columns": ["<column_name>", ...]}
      TABLE: {}
}
"""


class OllamaRecommendationService(AIRecommendationService):
    def __init__(self, base_url: str, model: str, timeout: float = 60.0):
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout

    def suggest(self, profile_payload: dict[str, Any]) -> dict[str, Any]:
        prompt = f"{_SYSTEM_PROMPT}\n\nDataset profile:\n{json.dumps(profile_payload, indent=2)}"

        response = requests.post(
            f"{self._base_url}/api/generate",
            json={
                "model": self._model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.1},
            },
            timeout=self._timeout,
        )
        response.raise_for_status()
        raw_text = response.json().get("response", "")

        try:
            return json.loads(raw_text)
        except json.JSONDecodeError as exc:
            logger.warning("Ollama returned non-JSON response: %s", raw_text[:500])
            raise ValueError(f"Ollama response was not valid JSON: {exc}") from exc