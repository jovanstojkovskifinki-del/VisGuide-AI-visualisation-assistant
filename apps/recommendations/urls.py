from django.urls import path

from apps.recommendations.views import DatasetRecommendationRefreshView, DatasetRecommendationView

urlpatterns = [
    path(
        "datasets/<uuid:dataset_id>/recommendation/",
        DatasetRecommendationView.as_view(),
        name="dataset-recommendation",
    ),
    path(
        "datasets/<uuid:dataset_id>/recommendation/refresh/",
        DatasetRecommendationRefreshView.as_view(),
        name="dataset-recommendation-refresh",
    ),
]
