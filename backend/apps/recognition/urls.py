"""Recognition app URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ASC606ComplianceViewSet,
    RecognitionRuleViewSet,
    RevenueEntryViewSet,
    RevenueScheduleViewSet,
)

router = DefaultRouter()
router.register(r"revenue-schedules", RevenueScheduleViewSet, basename="revenue-schedule")
router.register(r"revenue-entries", RevenueEntryViewSet, basename="revenue-entry")
router.register(r"recognition-rules", RecognitionRuleViewSet, basename="recognition-rule")
router.register(r"asc606-compliance", ASC606ComplianceViewSet, basename="asc606-compliance")

app_name = "recognition"

urlpatterns = [
    path("", include(router.urls)),
]
