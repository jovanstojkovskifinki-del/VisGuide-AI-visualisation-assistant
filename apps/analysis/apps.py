from django.apps import AppConfig


class AnalysisConfig(AppConfig):
    """Column typing, data quality, statistics, and correlation analysis."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.analysis"
    label = "analysis"
