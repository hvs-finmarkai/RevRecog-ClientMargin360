"""Leakage admin configuration."""
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import LeakageAlert, LeakageDetectionRun


@admin.register(LeakageAlert)
class LeakageAlertAdmin(SimpleHistoryAdmin):
    list_display = ["title", "alert_type", "severity", "status", "client", "estimated_leakage_amount", "created_at"]
    list_filter = ["alert_type", "severity", "status"]
    search_fields = ["title", "client__name", "contract__contract_number"]


@admin.register(LeakageDetectionRun)
class LeakageDetectionRunAdmin(admin.ModelAdmin):
    list_display = ["run_date", "contracts_analyzed", "alerts_generated", "total_leakage_detected", "duration_seconds"]
