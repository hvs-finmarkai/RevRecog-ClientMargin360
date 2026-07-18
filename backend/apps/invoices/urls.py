"""Invoices app URL configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CreditNoteViewSet, InvoiceTemplateViewSet, InvoiceViewSet

router = DefaultRouter()
router.register(r"invoices", InvoiceViewSet, basename="invoice")
router.register(r"invoice-templates", InvoiceTemplateViewSet, basename="invoice-template")
router.register(r"credit-notes", CreditNoteViewSet, basename="credit-note")

app_name = "invoices"

urlpatterns = [
    path("", include(router.urls)),
]
