from django.contrib import admin

from apps.analysis.models import ColumnProfile, DatasetProfile


class ColumnProfileInline(admin.TabularInline):
    model = ColumnProfile
    extra = 0
    readonly_fields = ["column_name", "detected_type", "missing_pct", "unique_count", "stats"]
    can_delete = False


@admin.register(DatasetProfile)
class DatasetProfileAdmin(admin.ModelAdmin):
    list_display = ["dataset", "duplicate_row_count", "analyzer_version", "generated_at"]
    inlines = [ColumnProfileInline]
    readonly_fields = ["generated_at"]
