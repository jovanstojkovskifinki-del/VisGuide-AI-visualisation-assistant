from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.datasets.services.data_access_service import DatasetDataService

from apps.core.pagination import DefaultPagination
from apps.core.permissions import AllowAnyForMVP
from apps.datasets.models import Dataset
from apps.datasets.serializers import DatasetSerializer, DatasetUploadSerializer
from apps.datasets.services.ingestion_service import DatasetIngestionService


class DatasetViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Thin API surface for datasets. Every non-trivial line of logic lives in
    `DatasetIngestionService` — this view only translates HTTP <-> service
    calls, per the "business logic must NOT exist inside Views" requirement.
    """

    queryset = Dataset.objects.prefetch_related("columns").all()
    serializer_class = DatasetSerializer
    pagination_class = DefaultPagination
    permission_classes = [AllowAnyForMVP]

    def get_ingestion_service(self) -> DatasetIngestionService:
        return DatasetIngestionService()

    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request):
        upload_serializer = DatasetUploadSerializer(data=request.data)
        upload_serializer.is_valid(raise_exception=True)

        dataset = self.get_ingestion_service().ingest(
            uploaded_file=upload_serializer.validated_data["file"],
            name=upload_serializer.validated_data.get("name"),
        )

        return Response(
            DatasetSerializer(dataset).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="columns")
    def columns(self, request, pk=None):
        dataset = self.get_object()
        from apps.datasets.serializers import DatasetColumnSerializer

        serializer = DatasetColumnSerializer(dataset.columns.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="data")
    def data(self, request, pk=None):
        """
        Returns the dataset's actual parsed rows (capped at
        DatasetDataService.DEFAULT_ROW_LIMIT), for the frontend to plot.
        Separate from `/profile/` (which returns aggregate stats, not raw
        rows) — this is the one endpoint that hands back real data.
        """
        dataset = self.get_object()
        payload = DatasetDataService().get_rows(dataset)
        return Response(payload)
