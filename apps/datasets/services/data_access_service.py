"""
DatasetDataService — retrieves the actual parsed rows of a dataset as
JSON-safe records, for the frontend to plot with. Distinct from
DatasetParsingService: that one produces the structural ParsedDataset
DTO (types, sample values) consumed during ingestion; this one re-reads
the stored file specifically to hand back plottable data on demand,
capped at a row limit so a very large dataset can't blow up the
response payload or the browser rendering it.
"""

import pandas as pd

from apps.core.utils.sampling import to_json_safe
from apps.datasets.models import Dataset
from apps.datasets.parsers.factory import get_parser_for

DEFAULT_ROW_LIMIT = 5000


class DatasetDataService:
    def get_rows(self, dataset: Dataset, limit: int = DEFAULT_ROW_LIMIT) -> dict:
        parser = get_parser_for(dataset.file_type)
        parsed = parser.parse(dataset.file.path)
        df: pd.DataFrame = parsed.dataframe

        truncated = df.shape[0] > limit
        if truncated:
            df = df.head(limit)

        records = [
            {str(col): to_json_safe(value) for col, value in row.items()}
            for row in df.to_dict(orient="records")
        ]

        return {
            "rows": records,
            "returned_row_count": len(records),
            "total_row_count": int(parsed.row_count),
            "truncated": truncated,
        }