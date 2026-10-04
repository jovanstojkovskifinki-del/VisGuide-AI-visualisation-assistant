from django.db import models

from apps.core.enums import VisualizationType
from apps.datasets.models import Dataset


class VisualizationConfig(models.Model):
    """
    Persisted standardized config object the frontend renders directly
    (e.g. with Plotly). Stored mostly as JSON fields because the shape of
    xAxis/yAxis/options genuinely differs per chart type — a heatmap has
    no single x/y pair, a histogram has no yAxis at all, a future 3D scene
    would use `options` for camera/scene data entirely. Forcing a rigid
    relational schema here would fight the domain rather than model it.
    """

    id = models.BigAutoField(primary_key=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="visualization_configs")
    visualization_type = models.CharField(max_length=20, choices=VisualizationType.choices)
    title = models.CharField(max_length=255)
    x_axis = models.JSONField(null=True, blank=True)
    y_axis = models.JSONField(null=True, blank=True)
    filters = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    options = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.dataset_id}: {self.visualization_type}"
