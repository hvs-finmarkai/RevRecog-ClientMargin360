"""Contract admin configuration."""
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from .models import Contract, PerformanceObligation, ContractModification


class PerformanceObligationInline(admin.TabularInline):
    model = PerformanceObligation
    extra = 0


@admin.register(Contract)
class ContractAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ["contract_number", "title", "client", "status", "total_value", "start_date", "end_date"]
    list_filter = ["status", "contract_type", "client"]
    search_fields = ["contract_number", "title", "client__name"]
    inlines = [PerformanceObligationInline]
    date_hierarchy = "start_date"


@admin.register(PerformanceObligation)
class PerformanceObligationAdmin(admin.ModelAdmin):
    list_display = ["contract", "name", "fulfillment_type", "progress_percentage", "allocated_price"]
    list_filter = ["fulfillment_type", "is_distinct"]


@admin.register(ContractModification)
class ContractModificationAdmin(SimpleHistoryAdmin):
    list_display = ["contract", "modification_type", "effective_date", "value_change"]
    list_filter = ["modification_type"]
