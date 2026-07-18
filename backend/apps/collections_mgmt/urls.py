"""Collections Management app URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AgingBucketViewSet,
    CollectionScheduleViewSet,
    PaymentReceiptViewSet,
    ReceivableViewSet,
)

router = DefaultRouter()
router.register(r"receivables", ReceivableViewSet, basename="receivable")
router.register(r"payment-receipts", PaymentReceiptViewSet, basename="payment-receipt")
router.register(r"collection-schedules", CollectionScheduleViewSet, basename="collection-schedule")
router.register(r"aging-buckets", AgingBucketViewSet, basename="aging-bucket")

app_name = "collections_mgmt"

urlpatterns = [
    path("", include(router.urls)),
]
