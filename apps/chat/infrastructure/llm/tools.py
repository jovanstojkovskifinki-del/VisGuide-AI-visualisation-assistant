VISUALIZATION_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "change_chart_type",
            "description": "Switch the current visualization to a different chart type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chart_type": {
                        "type": "string",
                        "enum": ["bar", "line", "scatter", "histogram", "heatmap", "map"],
                    },
                    "columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Only used when chart_type='heatmap' - which "
                            "numeric columns to include in the real "
                            "correlation matrix. Omit to include all "
                            "numeric columns in the dataset."
                        ),
                    },
                    "reason": {"type": "string"},
                },
                "required": ["chart_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "group_by",
            "description": (
                "Group rows by a column and aggregate a numeric column "
                "(real server-side computation). If no value_column is "
                "given, counts rows per group instead."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "The column to group by (first item used).",
                    },
                    "value_column": {
                        "type": "string",
                        "description": "Numeric column to aggregate. Omit to just count rows per group.",
                    },
                    "aggregation": {
                        "type": "string",
                        "enum": ["sum", "mean", "count", "min", "max"],
                    },
                },
                "required": ["columns", "aggregation"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "filter_data",
            "description": (
                "Filter rows based on a column condition (real server-side "
                "computation). Calling this multiple times ANDs the "
                "filters together."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {"type": "string"},
                    "operator": {
                        "type": "string",
                        "enum": ["eq", "neq", "gt", "lt", "gte", "lte", "contains", "between"],
                    },
                    "value": {
                        "type": "string",
                        "description": (
                            "Required for every operator except 'between'. "
                            "Always pass as a string, even for numbers or "
                            "dates - e.g. '42' or '2021-08-11'."
                        ),
                    },
                    "value_min": {
                        "type": "string",
                        "description": "Only for operator='between' - the lower bound, as a string (e.g. an ISO date).",
                    },
                    "value_max": {
                        "type": "string",
                        "description": "Only for operator='between' - the upper bound, as a string (e.g. an ISO date).",
                    },
                },
                "required": ["column", "operator"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "clear_filters",
            "description": "Remove all active filters and show the full dataset again.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_axes",
            "description": "Set which columns map to the x and y axes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "string"},
                    "y": {"type": "string"},
                },
                "required": ["x"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compute_statistic",
            "description": "Compute a REAL statistic from the dataset's actual values.",
            "parameters": {
                "type": "object",
                "properties": {
                    "stat_type": {
                        "type": "string",
                        "enum": [
                            "correlation", "mean", "median", "mode", "sum",
                            "count", "min", "max", "std", "variance",
                            "unique_count", "missing_count", "percentage",
                        ],
                    },
                    "columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "2 columns for correlation; 1 column otherwise.",
                    },
                    "value": {
                        "type": "string",
                        "description": (
                            "Only used with stat_type='percentage' - a "
                            "specific category to get the percentage of "
                            "(e.g. value='High'). Omit to get the full "
                            "percentage breakdown of every value in the "
                            "column."
                        ),
                    },
                },
                "required": ["stat_type", "columns"],
            },
        },
    },
]