"""Leakage app URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LeakageAlertViewSet, LeakageDetectionViewSet, LeakageRuleViewSet

router = DefaultRouter()
router.register(r"leakage-detections", LeakageDetectionViewSet, basename="leakage-detection")
router.register(r"leakage-rules", LeakageRuleViewSet, basename="leakage-rule")
router.register(r"leakage-alerts", LeakageAlertViewSet, basename="leakage-alert")

app_name = "leakage"

urlpatterns = [
    path("", include(router.urls)),
]
