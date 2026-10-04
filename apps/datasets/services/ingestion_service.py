from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from apps.core.enums import DatasetStatus
from apps.core.exceptions import DatasetParsingError
from apps.core.utils.file_validation import detect_file_type, validate_file_size
from apps.datasets.models import Dataset, DatasetColumn
from apps.datasets.parsers.base_parser import ParsedDataset
from apps.datasets.services.parsing_service import DatasetParsingService
from apps.datasets.services.storage_service import StorageService


class DatasetIngestionService:
    """
    Orchestrates the full upload pipeline:
        validate -> store file -> create Dataset row -> parse -> persist
        DatasetColumn rows -> mark PARSED (or FAILED).

    This is the only class a view should call for dataset upload — it is
    the single entry point that composes StorageService and
    DatasetParsingService, keeping both of those independently swappable
    and independently testable.
    """

    def __init__(
        self,
        storage_service: StorageService | None = None,
        parsing_service: DatasetParsingService | None = None,
    ):
        self._storage_service = storage_service or StorageService()
        self._parsing_service = parsing_service or DatasetParsingService()

    def ingest(self, uploaded_file: UploadedFile, name: str | None = None) -> Dataset:
        validate_file_size(uploaded_file.size)
        file_type = detect_file_type(uploaded_file.name)

        dataset = Dataset.objects.create(
            name=name or uploaded_file.name,
            original_filename=uploaded_file.name,
            file_type=file_type,
            file=uploaded_file,
            status=DatasetStatus.UPLOADED,
        )

        try:
            parsed = self._parsing_service.parse(dataset.file.path, file_type)
        except DatasetParsingError as exc:
            dataset.status = DatasetStatus.FAILED
            dataset.failure_reason = exc.message
            dataset.save(update_fields=["status", "failure_reason", "updated_at"])
            raise

        self._persist_parsed_columns(dataset, parsed)
        return dataset

    @transaction.atomic
    def _persist_parsed_columns(self, dataset: Dataset, parsed: ParsedDataset) -> None:
        DatasetColumn.objects.bulk_create(
            [
                DatasetColumn(
                    dataset=dataset,
                    name=col.name,
                    raw_dtype=col.raw_dtype,
                    position=col.position,
                    sample_values=col.sample_values,
                )
                for col in parsed.columns
            ]
        )
        dataset.row_count = parsed.row_count
        dataset.column_count = parsed.column_count
        dataset.status = DatasetStatus.PARSED
        dataset.save(update_fields=["row_count", "column_count", "status", "updated_at"])
