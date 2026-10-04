from django.apps import AppConfig


class RecommendationsConfig(AppConfig):
    """Rule-based (and eventually AI-based) visualization type recommendation."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.recommendations"
    label = "recommendations"
