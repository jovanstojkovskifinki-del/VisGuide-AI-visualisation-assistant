import pandas as pd

from apps.analysis.dto import ColumnProfileData, DatasetProfileData
from apps.analysis.services.column_type_detector import ColumnTypeDetector
from apps.analysis.services.correlation_service import CorrelationService
from apps.analysis.services.quality_report_service import QualityReportService
from apps.analysis.services.statistics_service import StatisticsService
from apps.core.enums import ColumnType
from apps.core.exceptions import AnalysisError
from apps.core.interfaces.content_analyzer import ContentAnalyzer
from apps.datasets.parsers.base_parser import ParsedDataset


class StructuredDataAnalyzer(ContentAnalyzer[ParsedDataset, DatasetProfileData]):
    """
    Module 1's sole ContentAnalyzer implementation. Composes
    ColumnTypeDetectionService, QualityReportService, StatisticsService,
    and CorrelationService, and produces a DatasetProfileData DTO — no
    Django models are touched here; persistence is AnalysisService's job
    (see analysis/services/analysis_service.py).
    """

    def __init__(
        self,
        type_detector: ColumnTypeDetector | None = None,
        quality_service: QualityReportService | None = None,
        statistics_service: StatisticsService | None = None,
        correlation_service: CorrelationService | None = None,
    ):
        self._type_detector = type_detector or ColumnTypeDetector()
        self._quality_service = quality_service or QualityReportService()
        self._statistics_service = statistics_service or StatisticsService()
        self._correlation_service = correlation_service or CorrelationService()

    def analyze(self, parsed_content: ParsedDataset) -> DatasetProfileData:
        df = parsed_content.dataframe
        if df is None:
            raise AnalysisError("ParsedDataset is missing its DataFrame.")

        column_profiles: list[ColumnProfileData] = []
        numeric_columns: list[str] = []

        for column_name in df.columns:
            series = df[column_name]
            detected_type = self._type_detector.detect(series)
            if detected_type in (ColumnType.NUMERIC, ColumnType.LATITUDE, ColumnType.LONGITUDE):
                numeric_columns.append(str(column_name))

            non_null_count = series.notna().sum()
            missing_pct = 0.0 if len(series) == 0 else round(
                (1 - non_null_count / len(series)) * 100, 2
            )

            column_profiles.append(
                ColumnProfileData(
                    column_name=str(column_name),
                    detected_type=detected_type,
                    missing_pct=missing_pct,
                    unique_count=int(series.nunique(dropna=True)),
                    stats=self._statistics_service.compute(series, detected_type),
                )
            )

        return DatasetProfileData(
            missing_values_report=self._quality_service.missing_values_report(df),
            duplicate_row_count=self._quality_service.duplicate_row_count(df),
            correlation_matrix=self._correlation_service.compute(df, numeric_columns),
            column_profiles=column_profiles,
        )
