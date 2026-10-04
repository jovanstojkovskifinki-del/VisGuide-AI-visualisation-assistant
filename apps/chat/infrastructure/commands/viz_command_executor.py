import json
from typing import Any

import pandas as pd

from apps.chat.domain.entities import CommandType, VisualizationCommand
from apps.chat.domain.interfaces import ICommandExecutor
from apps.chat.infrastructure.analysis.dataframe_loader import load_dataframe

CHART_TYPE_MAP = {
    "bar": "BAR_CHART",
    "line": "LINE_CHART",
    "scatter": "SCATTER_PLOT",
    "histogram": "HISTOGRAM",
    "heatmap": "HEATMAP",
    "map": "GEOGRAPHIC_MAP",
}

AGGREGATIONS = {"sum", "mean", "count", "min", "max"}
RESERVED_COUNT_COLUMN = "count"
MAX_FILTERED_ROWS = 5000


def _label_for(column: str) -> str:
    return column.replace("_", " ").title()


def _coerce_for_compare(series: pd.Series, value: Any) -> tuple[pd.Series, Any]:
    """Try comparing as dates first (so 'five years ago' style filters work
    correctly), then numbers, else fall back to string comparison.

    Dates are normalized to tz-naive on both sides before comparing -
    pandas raises rather than comparing a tz-aware column against a
    tz-naive value (or vice versa), and the LLM has no way to know
    which tz-awareness a given column happens to have.
    """
    as_dates = pd.to_datetime(series, errors="coerce")
    if as_dates.notna().sum() > 0:
        try:
            value_dt = pd.to_datetime(value)
            if as_dates.dt.tz is not None:
                as_dates = as_dates.dt.tz_convert(None)
            if getattr(value_dt, "tzinfo", None) is not None:
                value_dt = value_dt.tz_localize(None)
            return as_dates, value_dt
        except (ValueError, TypeError):
            pass
    as_numeric = pd.to_numeric(series, errors="coerce")
    if as_numeric.notna().sum() > 0:
        try:
            return as_numeric, float(value)
        except (ValueError, TypeError):
            pass
    return series.astype(str), str(value)

def _apply_single_filter(df: pd.DataFrame, f: dict) -> pd.DataFrame:
    column = f["column"]
    operator = f["operator"]

    if column not in df.columns:
        raise ValueError(f"Unknown column: {column}")

    if operator == "between":
        lo_raw = f.get("value_min")
        hi_raw = f.get("value_max")
        if lo_raw is None or hi_raw is None:
            raise ValueError("'between' requires value_min and value_max")
        series, lo = _coerce_for_compare(df[column], lo_raw)
        _, hi = _coerce_for_compare(df[column], hi_raw)
        return df[(series >= lo) & (series <= hi)]

    value = f.get("value")
    if value is None:
        raise ValueError(f"filter_data operator '{operator}' needs a value")

    if operator == "contains":
        return df[df[column].astype(str).str.contains(str(value), case=False, na=False)]

    series, cmp_value = _coerce_for_compare(df[column], value)
    if operator == "eq":
        return df[series == cmp_value]
    if operator == "neq":
        return df[series != cmp_value]
    if operator == "gt":
        return df[series > cmp_value]
    if operator == "lt":
        return df[series < cmp_value]
    if operator == "gte":
        return df[series >= cmp_value]
    if operator == "lte":
        return df[series <= cmp_value]

    raise ValueError(f"Unsupported filter operator: {operator}")

class VisualizationCommandExecutor(ICommandExecutor):
    def __init__(self, data_schema: dict[str, Any]):
        self.data_schema = data_schema

    def apply(
        self,
        command: VisualizationCommand,
        current_config: dict[str, Any],
        dataset: Any,
    ) -> dict[str, Any]:
        handler = getattr(self, f"_handle_{command.command_type.value}", None)
        if handler is None:
            raise ValueError(f"Unsupported command: {command.command_type}")
        return handler(command.params, current_config, dataset)

    def _validate_column(self, column: str) -> None:
        if column == RESERVED_COUNT_COLUMN:
            return
        if column not in self.data_schema:
            raise ValueError(f"Unknown column: {column}")

    def _handle_change_chart_type(self, params, config, dataset):
        chart_type = params.get("chart_type", "")
        mapped = CHART_TYPE_MAP.get(chart_type)
        if mapped is None:
            raise ValueError(f"Unsupported chart type: {chart_type}")

        new_config = {**config, "visualizationType": mapped}
        if mapped != "BAR_CHART":
            y_axis = new_config.get("yAxis")
            if y_axis and y_axis.get("column") == RESERVED_COUNT_COLUMN:
                new_config.pop("yAxis", None)
            new_config.pop("aggregatedData", None)

        if mapped == "HEATMAP":
            new_config["metadata"] = {
                **new_config.get("metadata", {}),
                "correlationMatrix": self._build_correlation_matrix(params, dataset),
            }
        elif "metadata" in new_config:
            new_config = {**new_config}
            new_config.pop("metadata", None)

        return new_config

    def _build_correlation_matrix(self, params, dataset) -> dict[str, Any]:
        requested_cols = params.get("columns")
        df = load_dataframe(dataset)

        if requested_cols:
            for c in requested_cols:
                self._validate_column(c)
                if c not in df.columns:
                    raise ValueError(f"Unknown column: {c}")
            numeric_df = df[requested_cols].apply(pd.to_numeric, errors="coerce")
        else:
            numeric_df = df.select_dtypes(include="number")

        numeric_df = numeric_df.dropna(axis=1, how="all")
        if numeric_df.shape[1] < 2:
            raise ValueError(
                "Need at least 2 numeric columns to build a correlation heatmap"
            )

        corr = numeric_df.corr().round(4)
        return {
            "matrix": corr.values.tolist(),
            "columns": corr.columns.tolist(),
        }

    def _handle_set_axes(self, params, config, dataset):
        x = params["x"]
        self._validate_column(x)
        new_config = {**config, "xAxis": {"column": x, "label": _label_for(x)}}
        new_config.pop("aggregatedData", None)

        y = params.get("y")
        if y:
            if y == RESERVED_COUNT_COLUMN and new_config.get("visualizationType") != "BAR_CHART":
                pass
            else:
                self._validate_column(y)
                new_config["yAxis"] = {"column": y, "label": _label_for(y)}
        return new_config

    def _handle_group_by(self, params, config, dataset):
        columns = params.get("columns") or []
        if not columns:
            raise ValueError("group_by needs at least one column")
        group_col = columns[0]
        self._validate_column(group_col)

        value_col = params.get("value_column")
        aggregation = params.get("aggregation", "sum")
        if aggregation not in AGGREGATIONS:
            raise ValueError(f"Unsupported aggregation: {aggregation}")

        new_config = {
            **config,
            "visualizationType": "BAR_CHART",
            "xAxis": {"column": group_col, "label": _label_for(group_col)},
        }

        if not value_col:
            df = load_dataframe(dataset)
            if group_col not in df.columns:
                raise ValueError(f"Unknown column: {group_col}")
            counts = df.groupby(group_col).size()
            new_config["yAxis"] = {"column": RESERVED_COUNT_COLUMN, "label": "Count"}
            new_config["aggregatedData"] = {
                "x": [str(v) for v in counts.index.tolist()],
                "y": [int(v) for v in counts.values.tolist()],
                "aggregation": "count",
            }
            return new_config

        self._validate_column(value_col)
        df = load_dataframe(dataset)
        if group_col not in df.columns or value_col not in df.columns:
            raise ValueError("Unknown column in group_by request")

        series = pd.to_numeric(df[value_col], errors="coerce") if aggregation != "count" else df[value_col]
        grouped = df.assign(**{value_col: series}).groupby(group_col)[value_col]
        result = getattr(grouped, aggregation)()

        new_config["yAxis"] = {"column": value_col, "label": _label_for(value_col)}
        new_config["aggregatedData"] = {
            "x": [str(v) for v in result.index.tolist()],
            "y": [round(float(v), 4) if aggregation != "count" else int(v) for v in result.values.tolist()],
            "aggregation": aggregation,
        }
        return new_config

    def _handle_filter_data(self, params, config, dataset):
        column = params.get("column")
        if not column:
            raise ValueError("filter_data needs a column")
        self._validate_column(column)
        if not params.get("operator"):
            raise ValueError("filter_data needs an operator")

        filters = list(config.get("filters", []))
        filters.append(params)

        df = load_dataframe(dataset)
        filtered = df
        for f in filters:
            filtered = _apply_single_filter(filtered, f)

        truncated = len(filtered) > MAX_FILTERED_ROWS
        if truncated:
            filtered = filtered.head(MAX_FILTERED_ROWS)

        rows = json.loads(filtered.to_json(orient="records", date_format="iso"))

        return {
            **config,
            "filters": filters,
            "filteredRows": rows,
            "filteredRowCount": len(rows),
            "filteredTruncated": truncated,
        }

    def _handle_clear_filters(self, params, config, dataset):
        new_config = {**config}
        new_config.pop("filters", None)
        new_config.pop("filteredRows", None)
        new_config.pop("filteredRowCount", None)
        new_config.pop("filteredTruncated", None)
        return new_config