from django.contrib import admin

from apps.visualizations.models import VisualizationConfig


@admin.register(VisualizationConfig)
class VisualizationConfigAdmin(admin.ModelAdmin):
    list_display = ["dataset", "visualization_type", "title", "created_at"]
    list_filter = ["visualization_type"]
    readonly_fields = ["created_at"]
