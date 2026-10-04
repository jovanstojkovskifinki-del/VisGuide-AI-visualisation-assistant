"""
Small helpers for producing JSON-safe sample values from a pandas
DataFrame, used by the datasets and analysis services. Kept here (rather
than duplicated in both apps) since both need "give me a safe preview of
this column" behavior.
"""

from typing import Any

import numpy as np
import pandas as pd


def to_json_safe(value: Any) -> Any:
    """Convert a single pandas/numpy scalar into a JSON-serializable value."""
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    return value


def sample_column_values(series: pd.Series, n: int = 5) -> list[Any]:
    """Return up to `n` non-null sample values from a column, JSON-safe."""
    non_null = series.dropna()
    sample = non_null.head(n)
    return [to_json_safe(v) for v in sample.tolist()]
