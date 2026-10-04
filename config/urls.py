"""
Root URL configuration. Each app's URLs are included under /api/ — thin
routing only, no view logic lives here.
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="visualizer/index.html"), name="home"),
    path("admin/", admin.site.urls),
    path("api/", include("apps.datasets.urls")),
    path("api/", include("apps.analysis.urls")),
    path("api/", include("apps.recommendations.urls")),
    path("api/", include("apps.visualizations.urls")),

    path("api/", include("apps.chat.urls")),
]