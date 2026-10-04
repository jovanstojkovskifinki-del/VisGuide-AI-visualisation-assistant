from typing import Any

from apps.chat.domain.entities import ChatMessage, ChatTurnResult, StatType
from apps.chat.domain.interfaces import ICommandExecutor, ILLMChatService, IStatisticsService
from apps.chat.infrastructure.analysis.pandas_statistics_service import compute_top_correlations

STAT_LABELS = {
    StatType.CORRELATION: "correlation",
    StatType.MEAN: "mean",
    StatType.MEDIAN: "median",
    StatType.MODE: "mode",
    StatType.SUM: "sum",
    StatType.COUNT: "count",
    StatType.MIN: "min",
    StatType.MAX: "max",
    StatType.STD: "standard deviation",
    StatType.VARIANCE: "variance",
    StatType.UNIQUE_COUNT: "number of unique values",
    StatType.MISSING_COUNT: "number of missing values",
    StatType.PERCENTAGE: "percentage breakdown",
}


class ProcessChatMessageUseCase:
    def __init__(
        self,
        llm_service: ILLMChatService,
        executor: ICommandExecutor,
        statistics_service: IStatisticsService,
    ):
        self.llm_service = llm_service
        self.executor = executor
        self.statistics_service = statistics_service

    def execute(
        self,
        history: list[ChatMessage],
        current_config: dict[str, Any],
        data_schema: dict[str, Any],
        dataset: Any,
    ) -> ChatTurnResult:
        try:
            top_correlations = compute_top_correlations(dataset)
        except Exception:
            top_correlations = []

        enriched_schema = (
            {**data_schema, "__top_correlations__": top_correlations}
            if top_correlations
            else data_schema
        )

        result = self.llm_service.get_response(history, current_config, enriched_schema)

        reply_text = result.reply_text
        updated_config = None

        if result.stat_command is not None:
            try:
                value = self.statistics_service.compute(
                    dataset,
                    result.stat_command.stat_type,
                    result.stat_command.columns,
                    result.stat_command.value,
                )
                label = STAT_LABELS.get(
                    result.stat_command.stat_type, result.stat_command.stat_type.value
                )
                cols = " and ".join(result.stat_command.columns)
                stat_line = f"The {label} of {cols} is {value}."
                reply_text = (
                    stat_line
                    if reply_text.strip() in ("", "Calculating...")
                    else f"{reply_text}\n\n{stat_line}"
                )
            except ValueError as e:
                reply_text = f"{reply_text}\n\nI couldn't compute that: {e}".strip()

        if result.commands:
            working_config = current_config
            errors = []
            for command in result.commands:
                try:
                    working_config = self.executor.apply(command, working_config, dataset)
                except ValueError as e:
                    errors.append(str(e))
            updated_config = working_config
            if errors:
                joined = "; ".join(errors)
                reply_text = f"{reply_text}\n\nSome changes couldn't be applied: {joined}".strip()

        return ChatTurnResult(
            reply_text=reply_text,
            commands=result.commands,
            stat_command=result.stat_command,
            updated_config=updated_config,
        )