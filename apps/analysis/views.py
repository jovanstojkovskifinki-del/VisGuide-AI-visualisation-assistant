from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analysis.serializers import DatasetProfileSerializer
from apps.analysis.services.analysis_service import AnalysisService
from apps.core.permissions import AllowAnyForMVP
from apps.datasets.models import Dataset


class DatasetProfileView(APIView):
    """
    GET  -> return the existing profile (analyzing on first request if one
           doesn't exist yet, so a fresh upload doesn't need a separate
           "trigger analysis" call before profile data is available).
    POST -> force re-analysis (e.g. after the analyzer implementation
           changes).
    """

    permission_classes: list[type[BasePermission]] = [AllowAnyForMVP]

    def get_service(self) -> AnalysisService:
        return AnalysisService()

    def get(self, request, dataset_id):
        dataset = get_object_or_404(Dataset, pk=dataset_id)
        profile = getattr(dataset, "profile", None)
        if profile is None:
            profile = self.get_service().analyze(dataset)
        return Response(DatasetProfileSerializer(profile).data)

    def post(self, request, dataset_id):
        dataset = get_object_or_404(Dataset, pk=dataset_id)
        profile = self.get_service().analyze(dataset)
        return Response(DatasetProfileSerializer(profile).data, status=status.HTTP_200_OK)
