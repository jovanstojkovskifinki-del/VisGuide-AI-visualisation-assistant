from django.db import transaction

from apps.analysis.models import ColumnProfile, DatasetProfile
from apps.analysis.services.structured_data_analyzer import StructuredDataAnalyzer
from apps.core.enums import DatasetStatus
from apps.core.interfaces.content_analyzer import ContentAnalyzer
from apps.datasets.models import Dataset
from apps.datasets.services.parsing_service import DatasetParsingService


class AnalysisService:
    """
    Orchestrates: re-parse the stored file (or reuse a cached DataFrame in
    a future optimization) -> run analysis -> persist DatasetProfile and
    ColumnProfile rows -> mark the Dataset ANALYZED.

    Takes a ContentAnalyzer as a constructor dependency (defaulting to
    StructuredDataAnalyzer) rather than importing it directly inline,
    consistent with the DI pattern used for the recommendation engine —
    this is the seam a future smarter analyzer would be injected through.
    """

    def __init__(
        self,
        analyzer: ContentAnalyzer | None = None,
        parsing_service: DatasetParsingService | None = None,
    ):
        self._analyzer = analyzer or StructuredDataAnalyzer()
        self._parsing_service = parsing_service or DatasetParsingService()

    def analyze(self, dataset: Dataset) -> DatasetProfile:
        parsed = self._parsing_service.parse(dataset.file.path, dataset.file_type)
        profile_data = self._analyzer.analyze(parsed)
        return self._persist(dataset, profile_data)

    @transaction.atomic
    def _persist(self, dataset: Dataset, profile_data) -> DatasetProfile:
        profile, _ = DatasetProfile.objects.update_or_create(
            dataset=dataset,
            defaults={
                "missing_values_report": profile_data.missing_values_report,
                "duplicate_row_count": profile_data.duplicate_row_count,
                "correlation_matrix": profile_data.correlation_matrix,
            },
        )
        profile.column_profiles.all().delete()
        ColumnProfile.objects.bulk_create(
            [
                ColumnProfile(
                    dataset_profile=profile,
                    column_name=cp.column_name,
                    detected_type=cp.detected_type,
                    missing_pct=cp.missing_pct,
                    unique_count=cp.unique_count,
                    stats=cp.stats,
                )
                for cp in profile_data.column_profiles
            ]
        )
        dataset.status = DatasetStatus.ANALYZED
        dataset.save(update_fields=["status", "updated_at"])
        return profile
