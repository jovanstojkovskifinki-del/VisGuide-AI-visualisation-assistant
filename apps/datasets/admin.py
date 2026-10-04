from django.contrib import admin

from apps.datasets.models import Dataset, DatasetColumn


class DatasetColumnInline(admin.TabularInline):
    model = DatasetColumn
    extra = 0
    readonly_fields = ["name", "raw_dtype", "position", "sample_values"]
    can_delete = False


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ["name", "file_type", "status", "row_count", "column_count", "uploaded_at"]
    list_filter = ["status", "file_type"]
    search_fields = ["name", "original_filename"]
    inlines = [DatasetColumnInline]
    readonly_fields = ["id", "uploaded_at", "updated_at"]
