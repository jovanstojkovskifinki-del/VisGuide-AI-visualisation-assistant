"""
DatasetParser is the interface both CSV and Excel parsers implement.
Adding a new structured format (e.g. Parquet, JSON-lines) later means
adding one new class here and one new entry in the parser factory —
IngestionService and everything above it is untouched.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from apps.core.exceptions import EmptyDatasetError


@dataclass
class ParsedColumn:
    name: str
    raw_dtype: str
    position: int
    sample_values: list[Any] = field(default_factory=list)


@dataclass
class ParsedDataset:
    """
    Normalized output of any DatasetParser. This — not the raw pandas
    DataFrame — is what crosses the parser -> service boundary in typed
    form; the DataFrame itself is attached for the analysis layer to
    consume directly without re-parsing the file.
    """

    row_count: int
    column_count: int
    columns: list[ParsedColumn]
    dataframe: pd.DataFrame


class DatasetParser(ABC):
    """Parses a raw uploaded file into a ParsedDataset."""

    @abstractmethod
    def parse(self, file_path: str) -> ParsedDataset:
        raise NotImplementedError

    @staticmethod
    def _validate_non_empty(df: pd.DataFrame) -> None:
        if df.shape[0] == 0 or df.shape[1] == 0:
            raise EmptyDatasetError()

    @staticmethod
    def _build_parsed_columns(df: pd.DataFrame) -> list[ParsedColumn]:
        from apps.core.utils.sampling import sample_column_values

        return [
            ParsedColumn(
                name=str(column_name),
                raw_dtype=str(df[column_name].dtype),
                position=position,
                sample_values=sample_column_values(df[column_name]),
            )
            for position, column_name in enumerate(df.columns)
        ]
