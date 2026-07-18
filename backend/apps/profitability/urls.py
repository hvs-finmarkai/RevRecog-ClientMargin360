"""Profitability app URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CostAllocationViewSet,
    MarginCalculationViewSet,
    ProfitabilitySnapshotViewSet,
)

router = DefaultRouter()
router.register(r"margin-calculations", MarginCalculationViewSet, basename="margin-calculation")
router.register(r"cost-allocations", CostAllocationViewSet, basename="cost-allocation")
router.register(r"profitability-snapshots", ProfitabilitySnapshotViewSet, basename="profitability-snapshot")

app_name = "profitability"

urlpatterns = [
    path("", include(router.urls)),
]
