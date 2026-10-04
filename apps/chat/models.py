from django.db import models


class ChatSession(models.Model):
    dataset = models.ForeignKey("datasets.Dataset", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class ChatMessageModel(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10, choices=[("user", "user"), ("assistant", "assistant")])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
