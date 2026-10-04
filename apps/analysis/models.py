from django.db import models

from apps.core.enums import ColumnType
from apps.datasets.models import Dataset


class DatasetProfile(models.Model):
    """
    Statistical/semantic profile of a Dataset — separate from Dataset
    itself because parsing (structural) and analysis (semantic) are
    different bounded contexts that evolve independently. Re-running
    analysis with a smarter ContentAnalyzer should never require
    re-parsing the source file.
    """

    id = models.BigAutoField(primary_key=True)
    dataset = models.OneToOneField(Dataset, on_delete=models.CASCADE, related_name="profile")
    missing_values_report = models.JSONField(default=dict, blank=True)
    duplicate_row_count = models.PositiveIntegerField(default=0)
    correlation_matrix = models.JSONField(null=True, blank=True)
    analyzer_version = models.CharField(max_length=50, default="structured-v1")
    generated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Profile for {self.dataset_id}"


class ColumnProfile(models.Model):
    """Per-column semantic type + stats, produced by StructuredDataAnalyzer."""

    id = models.BigAutoField(primary_key=True)
    dataset_profile = models.ForeignKey(
        DatasetProfile, on_delete=models.CASCADE, related_name="column_profiles"
    )
    column_name = models.CharField(max_length=255)
    detected_type = models.CharField(max_length=20, choices=ColumnType.choices)
    missing_pct = models.FloatField(default=0.0)
    unique_count = models.PositiveIntegerField(default=0)
    stats = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.column_name}: {self.detected_type}"
