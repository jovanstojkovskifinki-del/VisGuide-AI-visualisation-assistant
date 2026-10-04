import pandas as pd


class QualityReportService:
    """Computes missing-value and duplicate-row statistics for a DataFrame."""

    def missing_values_report(self, df: pd.DataFrame) -> dict[str, float]:
        if df.shape[0] == 0:
            return {str(col): 0.0 for col in df.columns}
        missing_pct = (df.isna().sum() / df.shape[0]) * 100
        return {str(col): round(float(pct), 2) for col, pct in missing_pct.items()}

    def duplicate_row_count(self, df: pd.DataFrame) -> int:
        return int(df.duplicated().sum())

    def constant_columns(self, df: pd.DataFrame) -> list[str]:
        """Columns with a single distinct non-null value — a quality flag."""
        constant = []
        for column in df.columns:
            non_null = df[column].dropna()
            if not non_null.empty and non_null.nunique() == 1:
                constant.append(str(column))
        return constant
