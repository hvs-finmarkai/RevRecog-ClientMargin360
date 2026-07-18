from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from .models import Contract, PerformanceObligation, ContractAmendment


class PerformanceObligationInline(admin.TabularInline):
    model = PerformanceObligation
    extra = 0


@admin.register(Contract)
class ContractAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    list_display = ["contract_number", "title", "client", "status", "total_value", "start_date", "end_date"]
    list_filter = ["status", "billing_model", "client"]
    search_fields = ["contract_number", "title", "client__name"]
    inlines = [PerformanceObligationInline]
    date_hierarchy = "start_date"


@admin.register(PerformanceObligation)
class PerformanceObligationAdmin(admin.ModelAdmin):
    list_display = ["contract", "description", "recognition_pattern", "allocation_amount", "status"]
    list_filter = ["recognition_pattern", "status"]


@admin.register(ContractAmendment)
class ContractAmendmentAdmin(SimpleHistoryAdmin):
    list_display = ["contract", "amendment_number", "effective_date", "value_change"]
    list_filter = ["effective_date"]
