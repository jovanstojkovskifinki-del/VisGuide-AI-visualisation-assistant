from typing import Any

import pandas as pd


class CorrelationService:
    """
    Computes a Pearson correlation matrix across numeric columns.
    Returns None when fewer than two numeric columns exist, since a
    correlation matrix isn't meaningful (and this None is what lets the
    recommendation engine's "matrix -> heatmap" rule short-circuit
    cleanly).
    """

    MIN_NUMERIC_COLUMNS = 2

    def compute(self, df: pd.DataFrame, numeric_columns: list[str]) -> dict[str, Any] | None:
        if len(numeric_columns) < self.MIN_NUMERIC_COLUMNS:
            return None

        numeric_df = df[numeric_columns].apply(pd.to_numeric, errors="coerce")
        corr = numeric_df.corr(method="pearson")
        corr = corr.round(4)

        return {
            "columns": list(corr.columns),
            "matrix": [
                [None if pd.isna(v) else float(v) for v in row]
                for row in corr.to_numpy().tolist()
            ],
        }
