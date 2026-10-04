from rest_framework import serializers

from apps.analysis.models import ColumnProfile, DatasetProfile


class ColumnProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColumnProfile
        fields = ["column_name", "detected_type", "missing_pct", "unique_count", "stats"]


class DatasetProfileSerializer(serializers.ModelSerializer):
    column_profiles = ColumnProfileSerializer(many=True, read_only=True)

    class Meta:
        model = DatasetProfile
        fields = [
            "dataset_id",
            "missing_values_report",
            "duplicate_row_count",
            "correlation_matrix",
            "analyzer_version",
            "generated_at",
            "column_profiles",
        ]
        read_only_fields = fields
