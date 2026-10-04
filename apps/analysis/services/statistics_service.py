from typing import Any

import pandas as pd

from apps.core.enums import ColumnType
from apps.core.utils.sampling import to_json_safe


class StatisticsService:
    """
    Computes descriptive statistics appropriate to a column's detected
    type: numeric columns get mean/median/std/min/max/percentiles;
    categorical columns get top-N category frequencies; datetime columns
    get min/max range.
    """

    def compute(self, series: pd.Series, column_type: ColumnType) -> dict[str, Any]:
        if column_type in (ColumnType.NUMERIC, ColumnType.LATITUDE, ColumnType.LONGITUDE):
            return self._numeric_stats(series)
        if column_type == ColumnType.DATETIME:
            return self._datetime_stats(series)
        if column_type == ColumnType.CATEGORICAL:
            return self._categorical_stats(series)
        if column_type == ColumnType.BOOLEAN:
            return self._boolean_stats(series)
        return {}

    def _numeric_stats(self, series: pd.Series) -> dict[str, Any]:
        non_null = series.dropna()
        if non_null.empty:
            return {}
        described = non_null.describe(percentiles=[0.25, 0.5, 0.75])
        return {
            "mean": to_json_safe(described.get("mean")),
            "std": to_json_safe(described.get("std")),
            "min": to_json_safe(described.get("min")),
            "p25": to_json_safe(described.get("25%")),
            "median": to_json_safe(described.get("50%")),
            "p75": to_json_safe(described.get("75%")),
            "max": to_json_safe(described.get("max")),
        }

    def _datetime_stats(self, series: pd.Series) -> dict[str, Any]:
        parsed = pd.to_datetime(series, errors="coerce").dropna()
        if parsed.empty:
            return {}
        return {
            "min": parsed.min().isoformat(),
            "max": parsed.max().isoformat(),
            "distinct_dates": int(parsed.dt.date.nunique()),
        }

    def _categorical_stats(self, series: pd.Series, top_n: int = 10) -> dict[str, Any]:
        non_null = series.dropna()
        if non_null.empty:
            return {}
        value_counts = non_null.value_counts().head(top_n)
        return {
            "top_categories": [
                {"value": str(value), "count": int(count)}
                for value, count in value_counts.items()
            ],
            "distinct_count": int(non_null.nunique()),
        }

    def _boolean_stats(self, series: pd.Series) -> dict[str, Any]:
        non_null = series.dropna()
        if non_null.empty:
            return {}
        return {
            "true_count": int(non_null.sum()),
            "false_count": int((~non_null.astype(bool)).sum()),
        }
