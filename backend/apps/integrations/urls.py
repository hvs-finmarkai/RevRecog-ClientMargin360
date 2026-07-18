"""Integrations app URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IntegrationConfigViewSet, WebhookConfigViewSet

router = DefaultRouter()
router.register(r"integrations", IntegrationConfigViewSet, basename="integration")
router.register(r"webhooks", WebhookConfigViewSet, basename="webhook")

app_name = "integrations"

urlpatterns = [
    path("", include(router.urls)),
]
