"""Reports admin configuration."""
from django.contrib import admin
from .models import Report, ScheduledReport


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["name", "report_type", "status", "format", "generated_by", "generated_at"]
    list_filter = ["report_type", "status", "format"]
    search_fields = ["name"]


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = ["name", "report_type", "frequency", "is_active", "last_generated_at", "next_generation_at"]
    list_filter = ["report_type", "frequency", "is_active"]
