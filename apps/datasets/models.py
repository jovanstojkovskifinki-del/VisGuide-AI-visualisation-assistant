import uuid

from django.db import models

from apps.core.enums import DatasetStatus, FileType


class Dataset(models.Model):
    """
    Aggregate root for an uploaded structured dataset. Everything else
    (columns, profile, recommendation logs, visualization configs) hangs
    off this by foreign key, so deleting a Dataset cascades cleanly.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FileType.choices)
    file = models.FileField(upload_to="datasets/%Y/%m/%d/")
    uploaded_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="datasets",
    )
    row_count = models.PositiveIntegerField(null=True, blank=True)
    column_count = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=DatasetStatus.choices, default=DatasetStatus.UPLOADED
    )
    failure_reason = models.TextField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.status})"


class DatasetColumn(models.Model):
    """
    Raw, structural snapshot of one column as parsed — not yet semantically
    typed (that's ColumnProfile's job in the `analysis` app). Kept separate
    from analysis output so re-running analysis never requires re-parsing.
    """

    id = models.BigAutoField(primary_key=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="columns")
    name = models.CharField(max_length=255)
    raw_dtype = models.CharField(max_length=50)
    position = models.PositiveIntegerField()
    sample_values = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["position"]
        unique_together = ("dataset", "position")

    def __str__(self) -> str:
        return f"{self.dataset_id}:{self.name}"
