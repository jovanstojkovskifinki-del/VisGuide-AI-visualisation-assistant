from django.apps import AppConfig


class DatasetsConfig(AppConfig):
    """Upload, storage, and parsing of structured datasets (CSV/Excel)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.datasets"
    label = "datasets"
