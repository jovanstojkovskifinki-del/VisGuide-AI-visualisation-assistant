from rest_framework import serializers

from apps.chat.models import ChatMessageModel, ChatSession


class ChatMessageInputSerializer(serializers.Serializer):
    """Validates the incoming request body for posting a chat message."""

    message = serializers.CharField(allow_blank=False)
    current_config = serializers.DictField()
    data_schema = serializers.DictField()


class ChatMessageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessageModel
        fields = ["id", "role", "content", "created_at"]
        read_only_fields = fields


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageModelSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ["id", "dataset", "created_at", "messages"]
        read_only_fields = ["id", "created_at", "messages"]


class ChatTurnResponseSerializer(serializers.Serializer):
    """Shapes the response returned to the frontend after a chat turn."""

    reply = serializers.CharField()
    updated_config = serializers.DictField(allow_null=True, required=False)

class ChatMessageInputSerializer(serializers.Serializer):
    message = serializers.CharField(allow_blank=False)
    current_config = serializers.DictField()
    data_schema = serializers.DictField()
    preferred_model = serializers.CharField(required=False, allow_null=True, allow_blank=True)