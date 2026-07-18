from django.contrib import admin
from .models import ReportTemplate, ReportSchedule, ReportExport, Dashboard, DashboardWidget


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'created_at']
    list_filter = ['report_type']
    search_fields = ['name']


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ['template', 'frequency', 'next_run', 'is_active']
    list_filter = ['frequency', 'is_active']
    search_fields = ['template__name']


@admin.register(ReportExport)
class ReportExportAdmin(admin.ModelAdmin):
    list_display = ['template', 'format', 'status', 'created_at']
    list_filter = ['format', 'status']
    search_fields = ['template__name']


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'is_default', 'created_at']
    list_filter = ['is_default']
    search_fields = ['name', 'owner__email']


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['dashboard', 'name', 'widget_type', 'position']
    list_filter = ['widget_type']
    search_fields = ['name', 'dashboard__name']
