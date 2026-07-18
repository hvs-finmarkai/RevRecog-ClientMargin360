"""Invoice admin configuration."""
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from .models import Invoice, InvoiceLineItem, Payment


class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ["invoice_number", "client", "status", "total_amount", "amount_paid", "issue_date", "due_date"]
    list_filter = ["status", "client", "currency"]
    search_fields = ["invoice_number", "client__name"]
    inlines = [InvoiceLineItemInline, PaymentInline]
    date_hierarchy = "issue_date"


@admin.register(Payment)
class PaymentAdmin(SimpleHistoryAdmin):
    list_display = ["invoice", "amount", "payment_date", "payment_method", "reference_number"]
    list_filter = ["payment_method"]
