from django.urls import path

from apps.chat.api.views import ChatMessageView, ModelStatusView

app_name = "chat"

urlpatterns = [
    path(
        "datasets/<uuid:dataset_id>/messages/",
        ChatMessageView.as_view(),
        name="chat-message",
    ),
    path("models/", ModelStatusView.as_view(), name="chat-models"),
]