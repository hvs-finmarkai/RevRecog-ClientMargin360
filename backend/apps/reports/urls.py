"""Reports app URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DashboardViewSet, ReportViewSet

router = DefaultRouter()
router.register(r"reports", ReportViewSet, basename="report")
router.register(r"dashboards", DashboardViewSet, basename="dashboard")

app_name = "reports"

urlpatterns = [
    path("", include(router.urls)),
]
