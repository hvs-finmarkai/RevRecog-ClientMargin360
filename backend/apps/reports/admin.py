from django.contrib import admin

from .models import ReportTemplate, ReportSchedule, ReportExport, Dashboard, DashboardWidget


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "report_type", "is_active"]
    list_filter = ["report_type", "is_active"]
    search_fields = ["name"]


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ["template", "frequency", "next_run", "is_active"]
    list_filter = ["frequency", "is_active"]


@admin.register(ReportExport)
class ReportExportAdmin(admin.ModelAdmin):
    list_display = ["template", "generated_at", "format", "generated_by"]
    list_filter = ["format"]


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "is_default", "created_by"]
    list_filter = ["is_default"]
    search_fields = ["name"]


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ["title", "dashboard", "widget_type", "position_x", "position_y"]
    list_filter = ["widget_type"]
    search_fields = ["title"]
