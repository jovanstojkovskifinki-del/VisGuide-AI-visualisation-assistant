from abc import ABC, abstractmethod
from typing import Any, Optional

from .entities import ChatMessage, ChatTurnResult, StatType, VisualizationCommand


class ILLMChatService(ABC):
    @abstractmethod
    def get_response(
        self,
        history: list[ChatMessage],
        current_config: dict[str, Any],
        data_schema: dict[str, Any],
    ) -> ChatTurnResult:
        raise NotImplementedError


class ICommandExecutor(ABC):
    @abstractmethod
    def apply(
        self,
        command: VisualizationCommand,
        current_config: dict[str, Any],
        dataset: Any,
    ) -> dict[str, Any]:
        raise NotImplementedError


class IStatisticsService(ABC):
    @abstractmethod
    def compute(
        self,
        dataset: Any,
        stat_type: StatType,
        columns: list[str],
        value: Optional[Any] = None,
    ) -> Any:
        raise NotImplementedError