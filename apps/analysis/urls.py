from django.urls import path

from apps.analysis.views import DatasetProfileView

urlpatterns = [
    path("datasets/<uuid:dataset_id>/profile/", DatasetProfileView.as_view(), name="dataset-profile"),
]
