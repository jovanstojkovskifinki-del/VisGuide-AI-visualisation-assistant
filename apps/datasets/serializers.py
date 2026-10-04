from rest_framework import serializers

from apps.core.enums import FileType
from apps.core.utils.file_validation import detect_file_type
from apps.datasets.models import Dataset, DatasetColumn


class DatasetUploadSerializer(serializers.Serializer):
    """
    Validates an incoming upload before it reaches the ingestion service.
    Deliberately NOT a ModelSerializer — upload validation (extension,
    presence of a file) is a different concern from serializing a
    persisted Dataset for API responses (DatasetSerializer, below).
    """

    file = serializers.FileField()
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_file(self, value):
        # Raises UnsupportedFileTypeError (-> mapped to 415 by the domain
        # exception handler) if the extension isn't recognized.
        detect_file_type(value.name)
        return value


class DatasetColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetColumn
        fields = ["name", "raw_dtype", "position", "sample_values"]


class DatasetSerializer(serializers.ModelSerializer):
    columns = DatasetColumnSerializer(many=True, read_only=True)

    class Meta:
        model = Dataset
        fields = [
            "id",
            "name",
            "original_filename",
            "file_type",
            "row_count",
            "column_count",
            "status",
            "failure_reason",
            "uploaded_at",
            "updated_at",
            "columns",
        ]
        read_only_fields = fields
