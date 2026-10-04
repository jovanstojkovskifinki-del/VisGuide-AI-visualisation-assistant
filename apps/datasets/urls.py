from rest_framework.routers import DefaultRouter

from apps.datasets.views import DatasetViewSet

router = DefaultRouter()
router.register(r"datasets", DatasetViewSet, basename="dataset")

urlpatterns = router.urls
