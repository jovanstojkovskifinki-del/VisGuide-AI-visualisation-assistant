from django.db import models

from apps.core.enums import RecommendationEngineType, VisualizationType
from apps.datasets.models import Dataset


class RecommendationLog(models.Model):
    """
    Audit trail of which engine/rule produced which recommendation for a
    dataset. Optional for Module 1's own functioning, but valuable from
    day one: once an AI engine exists, these rows become training/eval
    data for comparing rule-based vs AI recommendations on the same
    datasets.
    """

    id = models.BigAutoField(primary_key=True)
    dataset = models.ForeignKey(
        Dataset, on_delete=models.CASCADE, related_name="recommendation_logs"
    )
    engine_used = models.CharField(max_length=20, choices=RecommendationEngineType.choices)
    matched_rule = models.CharField(max_length=100, null=True, blank=True)
    recommended_type = models.CharField(max_length=20, choices=VisualizationType.choices)
    confidence = models.FloatField(null=True, blank=True)
    reasoning = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.dataset_id} -> {self.recommended_type} ({self.engine_used})"
