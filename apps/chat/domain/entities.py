from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class CommandType(str, Enum):
    CHANGE_CHART_TYPE = "change_chart_type"
    GROUP_BY = "group_by"
    FILTER_DATA = "filter_data"
    CLEAR_FILTERS = "clear_filters"
    SET_AXES = "set_axes"


class StatType(str, Enum):
    CORRELATION = "correlation"
    MEAN = "mean"
    MEDIAN = "median"
    MODE = "mode"
    SUM = "sum"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    STD = "std"
    VARIANCE = "variance"
    UNIQUE_COUNT = "unique_count"
    MISSING_COUNT = "missing_count"
    PERCENTAGE = "percentage"


@dataclass
class VisualizationCommand:
    command_type: CommandType
    params: dict[str, Any]


@dataclass
class StatisticCommand:
    stat_type: StatType
    columns: list[str]
    value: Optional[Any] = None  # only used by 'percentage' - a specific category to isolate


@dataclass
class ChatMessage:
    role: str
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ChatTurnResult:
    reply_text: str
    commands: list[VisualizationCommand] = field(default_factory=list)
    stat_command: Optional[StatisticCommand] = None
    updated_config: Optional[dict[str, Any]] = None