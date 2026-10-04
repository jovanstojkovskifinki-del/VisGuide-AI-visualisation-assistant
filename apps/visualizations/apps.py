from django.apps import AppConfig


class VisualizationsConfig(AppConfig):
    """Standardized visualization configuration generation, via a provider registry."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.visualizations"
    label = "visualizations"
