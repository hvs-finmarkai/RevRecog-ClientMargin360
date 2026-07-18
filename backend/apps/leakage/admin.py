from django.contrib import admin
from .models import LeakageDetection, LeakageRule, LeakageAlert, LeakageResolution


@admin.register(LeakageDetection)
class LeakageDetectionAdmin(admin.ModelAdmin):
    list_display = ['contract', 'detection_type', 'amount', 'detected_at']
    list_filter = ['detection_type']
    search_fields = ['contract__name']


@admin.register(LeakageRule)
class LeakageRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'rule_type', 'is_active']
    list_filter = ['rule_type', 'is_active']
    search_fields = ['name']


@admin.register(LeakageAlert)
class LeakageAlertAdmin(admin.ModelAdmin):
    list_display = ['detection', 'severity', 'status', 'created_at']
    list_filter = ['severity', 'status']
    search_fields = ['detection__contract__name']


@admin.register(LeakageResolution)
class LeakageResolutionAdmin(admin.ModelAdmin):
    list_display = ['alert', 'resolved_by', 'resolution_type', 'resolved_at']
    list_filter = ['resolution_type']
    search_fields = ['alert__detection__contract__name']
