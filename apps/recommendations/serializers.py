from rest_framework import serializers


class RecommendationResultSerializer(serializers.Serializer):
    """
    Serializes a `RecommendationResult` dataclass (not a Django model —
    RecommendationResult is a plain domain object shared by both the
    rule-based and future AI engines).
    """

    visualization_type = serializers.CharField(source="visualization_type.value")
    reasoning = serializers.CharField()
    confidence = serializers.FloatField()
    matched_rule = serializers.CharField(allow_null=True)
    suggested_axes = serializers.DictField()
    metadata = serializers.DictField()
