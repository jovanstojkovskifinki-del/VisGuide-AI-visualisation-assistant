from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analysis.services.analysis_service import AnalysisService
from apps.core.exceptions import AnalysisError
from apps.core.permissions import AllowAnyForMVP
from apps.datasets.models import Dataset
from apps.recommendations.services import RecommendationService
from apps.visualizations.serializers import VisualizationConfigSerializer
from apps.visualizations.services import VisualizationConfigService


class DatasetVisualizationConfigView(APIView):
    """
    GET  -> return the most recent config, generating the full
           analyze -> recommend -> configure pipeline on first request.
    POST -> force regeneration (e.g. after a user overrides axis choices
           in a future iteration, or after the recommendation engine changes).
    """

    permission_classes: list[type[BasePermission]] = [AllowAnyForMVP]

    def _get_or_build_profile(self, dataset: Dataset):
        profile = getattr(dataset, "profile", None)
        if profile is None:
            profile = AnalysisService().analyze(dataset)
        if not profile.column_profiles.exists():
            raise AnalysisError("Dataset profile has no column data to visualize.")
        return profile

    def get(self, request, dataset_id):
        dataset = get_object_or_404(Dataset, pk=dataset_id)
        existing = dataset.visualization_configs.first()
        if existing is not None:
            return Response(VisualizationConfigSerializer(existing).data)
        return self._generate(dataset)

    def post(self, request, dataset_id):
        dataset = get_object_or_404(Dataset, pk=dataset_id)
        return self._generate(dataset)

    def _generate(self, dataset: Dataset) -> Response:
        profile = self._get_or_build_profile(dataset)
        recommendation = RecommendationService().get_recommendation(profile)
        config = VisualizationConfigService().generate(profile, recommendation)
        return Response(VisualizationConfigSerializer(config).data)
