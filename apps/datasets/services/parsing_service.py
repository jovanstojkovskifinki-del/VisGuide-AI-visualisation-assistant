from apps.core.enums import FileType
from apps.datasets.parsers.base_parser import ParsedDataset
from apps.datasets.parsers.factory import get_parser_for


class DatasetParsingService:
    """
    Thin orchestration wrapper around the parser factory. Kept as its own
    service (rather than inlined into IngestionService) so parsing can be
    unit-tested or re-invoked independently of the upload/persistence flow
    (e.g. a future "re-parse this dataset" admin action).
    """

    def parse(self, file_path: str, file_type: FileType) -> ParsedDataset:
        parser = get_parser_for(file_type)
        return parser.parse(file_path)
