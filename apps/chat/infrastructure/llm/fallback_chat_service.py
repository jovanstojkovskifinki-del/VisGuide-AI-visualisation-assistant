from typing import Any, Optional

import requests

from apps.chat.domain.entities import ChatMessage, ChatTurnResult
from apps.chat.domain.interfaces import ILLMChatService
from .model_registry import (
    CONNECTION_ERROR_COOLDOWN_SECONDS,
    MODEL_REGISTRY,
    is_available,
    mark_available,
    mark_exhausted,
)


class NoModelAvailableError(RuntimeError):
    pass


class FallbackChatService(ILLMChatService):
    def __init__(self, preferred_model_id: Optional[str] = None):
        self.preferred_model_id = preferred_model_id
        self.model_used: Optional[str] = None
        self.fallback_occurred = False

    def _ordered_specs(self):
        specs = list(MODEL_REGISTRY)
        if self.preferred_model_id:
            specs.sort(key=lambda s: s.id != self.preferred_model_id)
        return specs

    def get_response(
        self,
        history: list[ChatMessage],
        current_config: dict[str, Any],
        data_schema: dict[str, Any],
    ) -> ChatTurnResult:
        specs = self._ordered_specs()
        tried_any = False
        last_error: Optional[Exception] = None

        for i, spec in enumerate(specs):
            if not is_available(spec.id):
                continue
            tried_any = True
            try:
                service = spec.factory()
                result = service.get_response(history, current_config, data_schema)
                mark_available(spec.id)
                self.model_used = spec.id
                self.fallback_occurred = i > 0
                return result
            except requests.HTTPError as e:
                status = e.response.status_code if e.response is not None else None
                if status == 429:
                    mark_exhausted(spec.id)
                    last_error = e
                    continue
                raise
            except requests.ConnectionError as e:
                mark_exhausted(spec.id, cooldown_seconds=CONNECTION_ERROR_COOLDOWN_SECONDS)
                last_error = e
                continue

        if not tried_any:
            raise NoModelAvailableError(
                "Every configured model is currently cooling down from a rate "
                "limit. Try again in a moment."
            )
        raise NoModelAvailableError(
            "All available models are currently rate-limited or unreachable."
        ) from last_error