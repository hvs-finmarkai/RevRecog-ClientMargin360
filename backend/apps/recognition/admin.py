"""Revenue recognition admin configuration."""
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import RevenueRecognitionEvent, DeferredRevenue, RecognitionRule


@admin.register(RevenueRecognitionEvent)
class RevenueRecognitionEventAdmin(SimpleHistoryAdmin):
    list_display = ["contract", "obligation", "period", "amount", "method", "status", "recognition_date"]
    list_filter = ["status", "method", "period"]
    search_fields = ["contract__contract_number"]
    date_hierarchy = "recognition_date"


@admin.register(DeferredRevenue)
class DeferredRevenueAdmin(admin.ModelAdmin):
    list_display = ["contract", "obligation", "period", "opening_balance", "recognized", "closing_balance"]
    list_filter = ["period"]


@admin.register(RecognitionRule)
class RecognitionRuleAdmin(admin.ModelAdmin):
    list_display = ["name", "trigger_type", "is_active", "requires_approval", "auto_recognize_threshold"]
    list_filter = ["trigger_type", "is_active"]
