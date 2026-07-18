"""Analytics admin configuration."""
from django.contrib import admin
from .models import DashboardWidget, MetricSnapshot


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ["title", "widget_type", "metric_key", "is_active", "sort_order"]
    list_filter = ["widget_type", "is_active"]


@admin.register(MetricSnapshot)
class MetricSnapshotAdmin(admin.ModelAdmin):
    list_display = ["metric_name", "metric_value", "period", "computed_at"]
    list_filter = ["metric_name", "period"]
