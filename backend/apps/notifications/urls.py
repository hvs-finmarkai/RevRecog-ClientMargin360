"""Notifications app URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AlertRuleViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"alert-rules", AlertRuleViewSet, basename="alert-rule")

app_name = "notifications"

urlpatterns = [
    path("", include(router.urls)),
]
