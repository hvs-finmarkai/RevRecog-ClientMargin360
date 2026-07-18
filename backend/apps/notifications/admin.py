from django.contrib import admin
from .models import NotificationTemplate, Notification, NotificationPreference, AlertRule


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'channel', 'created_at']
    list_filter = ['channel']
    search_fields = ['name']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'channel', 'is_read', 'created_at']
    list_filter = ['channel', 'is_read']
    search_fields = ['user__email', 'title']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'channel', 'is_enabled']
    list_filter = ['channel', 'is_enabled']
    search_fields = ['user__email']


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'condition_type', 'severity', 'is_active']
    list_filter = ['condition_type', 'severity', 'is_active']
    search_fields = ['name']
