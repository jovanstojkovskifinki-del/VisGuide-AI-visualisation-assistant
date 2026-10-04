from typing import Any, Optional

import pandas as pd

from apps.chat.domain.entities import StatType
from apps.chat.domain.interfaces import IStatisticsService
from .dataframe_loader import load_dataframe

TOP_CORRELATIONS_LIMIT = 8


def compute_top_correlations(dataset: Any, top_n: int = 5) -> list[dict[str, Any]]:
    """Real pairwise correlations across all numeric columns, strongest
    first. Gives the LLM grounded context so it can answer 'which columns
    are most correlated' without guessing or chaining many
    compute_statistic calls.
    """
    df = load_dataframe(dataset)
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.shape[1] < 2:
        return []

    corr = numeric_df.corr()
    cols = corr.columns.tolist()
    pairs = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            val = corr.iloc[i, j]
            if pd.notna(val):
                pairs.append(
                    {"columns": [cols[i], cols[j]], "correlation": round(float(val), 4)}
                )
    pairs.sort(key=lambda p: abs(p["correlation"]), reverse=True)
    return pairs[:top_n]


class PandasStatisticsService(IStatisticsService):
    def compute(
        self,
        dataset: Any,
        stat_type: StatType,
        columns: list[str],
        value: Optional[Any] = None,
    ) -> Any:
        df = load_dataframe(dataset)

        for col in columns:
            if col not in df.columns:
                raise ValueError(f"Unknown column: {col}")

        if stat_type == StatType.CORRELATION:
            if len(columns) != 2:
                raise ValueError("Correlation needs exactly 2 columns")
            series_a = self._as_numeric(df, columns[0])
            series_b = self._as_numeric(df, columns[1])
            return round(float(series_a.corr(series_b)), 4)

        if stat_type == StatType.PERCENTAGE:
            if len(columns) != 1:
                raise ValueError("percentage needs exactly 1 column")
            col = columns[0]
            total = int(df[col].notna().sum())
            if total == 0:
                raise ValueError(f"Column '{col}' has no values")
            counts = df[col].value_counts(dropna=True)

            if value is not None:
                matched = int(counts.get(value, 0))
                pct = round(matched / total * 100, 2)
                return f"{pct}% ({matched} of {total} rows)"

            breakdown = (counts / total * 100).round(2)
            parts = [f"{k}: {v}%" for k, v in breakdown.items()]
            return ", ".join(parts)

        if len(columns) != 1:
            raise ValueError(f"{stat_type.value} needs exactly 1 column")
        col = columns[0]

        if stat_type == StatType.COUNT:
            return int(df[col].count())
        if stat_type == StatType.UNIQUE_COUNT:
            return int(df[col].nunique(dropna=True))
        if stat_type == StatType.MISSING_COUNT:
            return int(df[col].isna().sum())
        if stat_type == StatType.MODE:
            modes = df[col].mode(dropna=True)
            if modes.empty:
                raise ValueError(f"Column '{col}' has no values to find a mode from")
            mode_value = modes.iloc[0]
            return f"{mode_value}" + (" (tied with others)" if len(modes) > 1 else "")

        series = self._as_numeric(df, col)
        if stat_type == StatType.MEAN:
            return round(float(series.mean()), 4)
        if stat_type == StatType.MEDIAN:
            return round(float(series.median()), 4)
        if stat_type == StatType.SUM:
            return round(float(series.sum()), 4)
        if stat_type == StatType.MIN:
            return round(float(series.min()), 4)
        if stat_type == StatType.MAX:
            return round(float(series.max()), 4)
        if stat_type == StatType.STD:
            return round(float(series.std()), 4)
        if stat_type == StatType.VARIANCE:
            return round(float(series.var()), 4)

        raise ValueError(f"Unsupported stat type: {stat_type}")

    def _as_numeric(self, df: pd.DataFrame, col: str) -> pd.Series:
        series = pd.to_numeric(df[col], errors="coerce")
        if series.notna().sum() == 0:
            raise ValueError(f"Column '{col}' has no numeric values to compute on")
        return series.dropna()