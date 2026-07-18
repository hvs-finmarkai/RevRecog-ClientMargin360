"""Billing app URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BillingModelViewSet,
    BillingPeriodViewSet,
    BillingScheduleViewSet,
    EscalationRuleViewSet,
    RateCardViewSet,
)

router = DefaultRouter()
router.register(r"billing-models", BillingModelViewSet, basename="billing-model")
router.register(r"rate-cards", RateCardViewSet, basename="rate-card")
router.register(r"billing-periods", BillingPeriodViewSet, basename="billing-period")
router.register(r"billing-schedules", BillingScheduleViewSet, basename="billing-schedule")
router.register(r"escalation-rules", EscalationRuleViewSet, basename="escalation-rule")

app_name = "billing"

urlpatterns = [
    path("", include(router.urls)),
]
