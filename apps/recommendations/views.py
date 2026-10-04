from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analysis.services.analysis_service import AnalysisService
from apps.core.exceptions import AnalysisError
from apps.core.permissions import AllowAnyForMVP
from apps.datasets.models import Dataset
from apps.recommendations.serializers import RecommendationResultSerializer
from apps.recommendations.services import RecommendationService


class DatasetRecommendationView(APIView):
    """
    GET  /datasets/{id}/recommendation/          -> recommend (analyzing first if needed)
    POST /datasets/{id}/recommendation/refresh/   -> force a fresh recommendation + log entry
    """

    permission_classes: list[type[BasePermission]] = [AllowAnyForMVP]

    def get_recommendation_service(self) -> RecommendationService:
        return RecommendationService()

    def _get_or_build_profile(self, dataset: Dataset):
        profile = getattr(dataset, "profile", None)
        if profile is None:
            profile = AnalysisService().analyze(dataset)
        if not profile.column_profiles.exists():
            raise AnalysisError("Dataset profile has no column data to recommend from.")
        return profile

    def get(self, request, dataset_id):
        dataset = get_object_or_404(Dataset, pk=dataset_id)
        profile = self._get_or_build_profile(dataset)
        result = self.get_recommendation_service().get_recommendation(profile)
        return Response(RecommendationResultSerializer(result).data)


class DatasetRecommendationRefreshView(DatasetRecommendationView):
    def post(self, request, dataset_id):
        return self.get(request, dataset_id)
