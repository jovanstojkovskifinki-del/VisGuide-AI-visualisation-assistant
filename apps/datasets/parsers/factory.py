from apps.core.enums import FileType
from apps.datasets.parsers.base_parser import DatasetParser
from apps.datasets.parsers.csv_parser import CSVParser
from apps.datasets.parsers.excel_parser import ExcelParser

_PARSERS: dict[FileType, type[DatasetParser]] = {
    FileType.CSV: CSVParser,
    FileType.XLSX: ExcelParser,
}


def get_parser_for(file_type: FileType) -> DatasetParser:
    """
    Returns a parser instance for the given FileType.

    Adding a new supported format is exactly: implement DatasetParser,
    add one line to `_PARSERS`. Nothing else in the ingestion pipeline
    changes.
    """
    parser_class = _PARSERS[file_type]
    return parser_class()
