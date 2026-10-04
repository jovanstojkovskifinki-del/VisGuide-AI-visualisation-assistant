from django.contrib import admin

from apps.recommendations.models import RecommendationLog


@admin.register(RecommendationLog)
class RecommendationLogAdmin(admin.ModelAdmin):
    list_display = ["dataset", "engine_used", "matched_rule", "recommended_type", "confidence", "created_at"]
    list_filter = ["engine_used", "recommended_type"]
    readonly_fields = [f.name for f in RecommendationLog._meta.fields]
