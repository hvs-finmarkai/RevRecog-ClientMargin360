"""Notifications admin configuration."""
from django.contrib import admin
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "recipient", "notification_type", "channel", "is_read", "created_at"]
    list_filter = ["notification_type", "channel", "is_read"]
    search_fields = ["title", "recipient__email"]


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ["user", "email_enabled", "digest_frequency"]
