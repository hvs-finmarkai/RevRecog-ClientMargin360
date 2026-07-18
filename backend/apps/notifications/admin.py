from django.contrib import admin

from .models import NotificationTemplate, Notification, NotificationPreference, AlertRule


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "channel", "category", "is_active"]
    list_filter = ["channel", "is_active", "category"]
    search_fields = ["name", "subject"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "type", "category", "read_at"]
    list_filter = ["type", "category"]
    search_fields = ["title", "message"]


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ["user", "channel", "is_enabled"]
    list_filter = ["channel", "is_enabled"]


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ["name", "severity", "is_active", "last_triggered", "trigger_count"]
    list_filter = ["severity", "is_active"]
    search_fields = ["name"]
