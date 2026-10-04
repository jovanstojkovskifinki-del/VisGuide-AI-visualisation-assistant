import pandas as pd

from apps.core.exceptions import DatasetParsingError
from apps.datasets.parsers.base_parser import DatasetParser, ParsedDataset


class ExcelParser(DatasetParser):
    """
    Parses .xlsx files using pandas + openpyxl.

    Reads only the first sheet for Module 1. Multi-sheet support is a
    natural, non-breaking extension (return one ParsedDataset per sheet)
    that can be added later without touching this class's public contract.
    """

    def parse(self, file_path: str) -> ParsedDataset:
        try:
            df = pd.read_excel(file_path, sheet_name=0, engine="openpyxl")
        except Exception as exc:  # noqa: BLE001 - surfaced as a domain error
            raise DatasetParsingError(f"Could not parse Excel file: {exc}") from exc

        self._validate_non_empty(df)

        return ParsedDataset(
            row_count=df.shape[0],
            column_count=df.shape[1],
            columns=self._build_parsed_columns(df),
            dataframe=df,
        )
