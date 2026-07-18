from django.contrib import admin
from .models import AnalyticsEvent, MetricSnapshot


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'user', 'created_at']
    list_filter = ['event_type']
    search_fields = ['event_type', 'user__email']


@admin.register(MetricSnapshot)
class MetricSnapshotAdmin(admin.ModelAdmin):
    list_display = ['metric_name', 'value', 'period', 'created_at']
    list_filter = ['metric_name', 'period']
    search_fields = ['metric_name']
