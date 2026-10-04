from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chat.api.serializers import ChatMessageInputSerializer
from apps.chat.application.process_message import ProcessChatMessageUseCase
from apps.chat.domain.entities import ChatMessage
from apps.chat.infrastructure.analysis.pandas_statistics_service import PandasStatisticsService
from apps.chat.infrastructure.commands.viz_command_executor import VisualizationCommandExecutor
from apps.chat.infrastructure.llm.fallback_chat_service import FallbackChatService, NoModelAvailableError
from apps.chat.infrastructure.llm.model_registry import MODEL_REGISTRY, get_model_status
from apps.chat.models import ChatMessageModel, ChatSession
from apps.datasets.models import Dataset

MAX_HISTORY_MESSAGES = 20


class ChatMessageView(APIView):
    def post(self, request, dataset_id):
        input_serializer = ChatMessageInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated = input_serializer.validated_data

        dataset = get_object_or_404(Dataset, id=dataset_id)
        session, _ = ChatSession.objects.get_or_create(dataset=dataset)

        ChatMessageModel.objects.create(
            session=session, role="user", content=validated["message"]
        )

        recent_messages = list(session.messages.order_by("-created_at")[:MAX_HISTORY_MESSAGES])
        recent_messages.reverse()
        history = [ChatMessage(role=m.role, content=m.content) for m in recent_messages]

        preferred_model = validated.get("preferred_model") or None
        llm_service = FallbackChatService(preferred_model_id=preferred_model)

        use_case = ProcessChatMessageUseCase(
            llm_service=llm_service,
            executor=VisualizationCommandExecutor(data_schema=validated["data_schema"]),
            statistics_service=PandasStatisticsService(),
        )

        try:
            result = use_case.execute(
                history, validated["current_config"], validated["data_schema"], dataset
            )
        except NoModelAvailableError as e:
            ChatMessageModel.objects.create(session=session, role="assistant", content=str(e))
            return Response(
                {
                    "reply": str(e),
                    "updated_config": None,
                    "model_used": None,
                    "model_status": get_model_status(),
                }
            )

        reply_text = result.reply_text
        if llm_service.fallback_occurred:
            used_name = next(
                (s.display_name for s in MODEL_REGISTRY if s.id == llm_service.model_used),
                llm_service.model_used,
            )
            reply_text = f"{reply_text}\n\n(Switched to {used_name} - the previous model hit its rate limit.)".strip()

        ChatMessageModel.objects.create(session=session, role="assistant", content=reply_text)

        return Response(
            {
                "reply": reply_text,
                "updated_config": result.updated_config,
                "model_used": llm_service.model_used,
                "model_status": get_model_status(),
            }
        )


class ModelStatusView(APIView):
    def get(self, request):
        return Response({"models": get_model_status()})