"""
Plain-Python DTOs produced by StructuredDataAnalyzer, before anything is
persisted to the DatasetProfile/ColumnProfile models. Keeping analysis
output in dataclasses (rather than building Django model instances
directly inside the analyzer) is what keeps StructuredDataAnalyzer free of
any Django import — it's pure pandas in, plain dataclasses out.
"""

from dataclasses import dataclass, field
from typing import Any

from apps.core.enums import ColumnType


@dataclass
class ColumnProfileData:
    column_name: str
    detected_type: ColumnType
    missing_pct: float
    unique_count: int
    stats: dict[str, Any] = field(default_factory=dict)


@dataclass
class DatasetProfileData:
    missing_values_report: dict[str, float]
    duplicate_row_count: int
    correlation_matrix: dict[str, Any] | None
    column_profiles: list[ColumnProfileData]
