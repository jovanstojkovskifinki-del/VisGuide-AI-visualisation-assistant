"""
Detects the semantic ColumnType of each column in a DataFrame using a
combination of pandas dtype, column-name heuristics, and value-range
checks. This is pure logic — no Django, no I/O — so it's directly
unit-testable against plain DataFrames.
"""

import re
import warnings

import pandas as pd

from apps.core.enums import ColumnType

_LATITUDE_NAME_PATTERN = re.compile(r"^(lat|latitude|lat_?deg)$", re.IGNORECASE)
_LONGITUDE_NAME_PATTERN = re.compile(r"^(lon|lng|long|longitude|lon_?deg)$", re.IGNORECASE)
_IDENTIFIER_NAME_PATTERN = re.compile(r"^(id|.*_id|uuid|guid)$", re.IGNORECASE)


class ColumnTypeDetector:
    def detect(self, series: pd.Series) -> ColumnType:
        column_name = str(series.name or "")

        if self._looks_like_latitude(series, column_name):
            return ColumnType.LATITUDE
        if self._looks_like_longitude(series, column_name):
            return ColumnType.LONGITUDE
        if pd.api.types.is_bool_dtype(series):
            return ColumnType.BOOLEAN
        if pd.api.types.is_datetime64_any_dtype(series):
            return ColumnType.DATETIME
        if self._looks_like_datetime_string(series):
            return ColumnType.DATETIME
        if self._looks_like_identifier(series, column_name):
            return ColumnType.IDENTIFIER
        if pd.api.types.is_numeric_dtype(series):
            return ColumnType.NUMERIC
        if self._is_text_dtype(series) or isinstance(series.dtype, pd.CategoricalDtype):
            return ColumnType.CATEGORICAL
        return ColumnType.UNKNOWN

    @staticmethod
    def _is_text_dtype(series: pd.Series) -> bool:
        """
        True for columns holding text, across pandas' several string
        representations: classic `object` dtype (pandas < 3.0 default),
        and the `str`/`StringDtype` extension type that pandas >= 3.0
        uses by default when `future.infer_string` is enabled. Checking
        only `is_object_dtype` misses the latter entirely, which would
        silently misclassify every plain string column as UNKNOWN.
        """
        return bool(
            pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series)
        )

    def _looks_like_latitude(self, series: pd.Series, column_name: str) -> bool:
        if not pd.api.types.is_numeric_dtype(series):
            return False
        if _LATITUDE_NAME_PATTERN.match(column_name):
            return True
        non_null = series.dropna()
        if non_null.empty:
            return False
        return bool(non_null.between(-90, 90).all()) and "lat" in column_name.lower()

    def _looks_like_longitude(self, series: pd.Series, column_name: str) -> bool:
        if not pd.api.types.is_numeric_dtype(series):
            return False
        if _LONGITUDE_NAME_PATTERN.match(column_name):
            return True
        non_null = series.dropna()
        if non_null.empty:
            return False
        lowered = column_name.lower()
        return bool(non_null.between(-180, 180).all()) and (
            "lon" in lowered or "lng" in lowered
        )

    def _looks_like_identifier(self, series: pd.Series, column_name: str) -> bool:
        if not _IDENTIFIER_NAME_PATTERN.match(column_name):
            return False
        non_null = series.dropna()
        if non_null.empty:
            return False
        return non_null.is_unique

    def _looks_like_datetime_string(self, series: pd.Series) -> bool:
        if not self._is_text_dtype(series):
            return False
        sample = series.dropna().head(20)
        if sample.empty:
            return False
        try:
            with warnings.catch_warnings():
                # This is a speculative "does this look like dates?" probe,
                # not a real parse — the format-inference warning pandas
                # raises here is expected noise, not something callers
                # need surfaced.
                warnings.simplefilter("ignore", UserWarning)
                parsed = pd.to_datetime(sample, errors="coerce")
        except (TypeError, ValueError):
            return False
        # Require the overwhelming majority to parse as dates before
        # committing to DATETIME — otherwise free-text columns that
        # happen to contain a few date-like strings get misclassified.
        return parsed.notna().mean() >= 0.9
