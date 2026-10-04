from rest_framework import serializers

from apps.visualizations.models import VisualizationConfig


class VisualizationConfigSerializer(serializers.ModelSerializer):
    """
    Matches the {visualizationType, title, xAxis, yAxis, filters,
    metadata, options} contract from the architecture doc — camelCase
    field names on the wire via `source=`, snake_case in the model.
    """

    visualizationType = serializers.CharField(source="visualization_type")
    xAxis = serializers.JSONField(source="x_axis")
    yAxis = serializers.JSONField(source="y_axis")

    class Meta:
        model = VisualizationConfig
        fields = [
            "id",
            "visualizationType",
            "title",
            "xAxis",
            "yAxis",
            "filters",
            "metadata",
            "options",
            "created_at",
        ]
        read_only_fields = fields
