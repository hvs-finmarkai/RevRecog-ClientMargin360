from django.contrib import admin

from .models import LeakageDetection, LeakageRule, LeakageAlert, LeakageResolution


@admin.register(LeakageDetection)
class LeakageDetectionAdmin(admin.ModelAdmin):
    list_display = ["id", "client", "detection_type", "amount", "severity", "status"]
    list_filter = ["detection_type", "severity", "status"]
    search_fields = ["client__name", "description"]


@admin.register(LeakageRule)
class LeakageRuleAdmin(admin.ModelAdmin):
    list_display = ["name", "detection_type", "severity", "is_active"]
    list_filter = ["detection_type", "severity", "is_active"]
    search_fields = ["name"]


@admin.register(LeakageAlert)
class LeakageAlertAdmin(admin.ModelAdmin):
    list_display = ["id", "detection", "alert_type", "sent_at"]
    list_filter = ["alert_type"]


@admin.register(LeakageResolution)
class LeakageResolutionAdmin(admin.ModelAdmin):
    list_display = ["id", "detection", "action_taken", "amount_recovered"]
    search_fields = ["action_taken"]
