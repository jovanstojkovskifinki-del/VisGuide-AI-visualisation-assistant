import pandas as pd

from apps.core.exceptions import DatasetParsingError
from apps.datasets.parsers.base_parser import DatasetParser, ParsedDataset


class CSVParser(DatasetParser):
    """Parses .csv files using pandas, with a couple of encoding fallbacks."""

    _ENCODINGS_TO_TRY = ("utf-8", "utf-8-sig", "latin-1")

    def parse(self, file_path: str) -> ParsedDataset:
        df: pd.DataFrame | None = None
        last_error: Exception | None = None

        for encoding in self._ENCODINGS_TO_TRY:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                break
            except (UnicodeDecodeError, pd.errors.ParserError) as exc:
                last_error = exc
                continue

        if df is None:
            raise DatasetParsingError(
                f"Could not parse CSV file with any of the supported encodings: {last_error}"
            )

        self._validate_non_empty(df)

        return ParsedDataset(
            row_count=df.shape[0],
            column_count=df.shape[1],
            columns=self._build_parsed_columns(df),
            dataframe=df,
        )
