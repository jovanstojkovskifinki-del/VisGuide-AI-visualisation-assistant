from django.urls import path

from apps.visualizations.views import DatasetVisualizationConfigView

urlpatterns = [
    path(
        "datasets/<uuid:dataset_id>/visualization-config/",
        DatasetVisualizationConfigView.as_view(),
        name="dataset-visualization-config",
    ),
]
