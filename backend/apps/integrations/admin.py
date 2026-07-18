from django.contrib import admin
from .models import IntegrationConfig, SyncLog, WebhookConfig, APIKey


@admin.register(IntegrationConfig)
class IntegrationConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'integration_type', 'is_active', 'created_at']
    list_filter = ['integration_type', 'is_active']
    search_fields = ['name']


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ['integration', 'status', 'records_synced', 'synced_at']
    list_filter = ['status']
    search_fields = ['integration__name']


@admin.register(WebhookConfig)
class WebhookConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'event_type', 'is_active']
    list_filter = ['event_type', 'is_active']
    search_fields = ['name', 'url']


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_active', 'created_at', 'expires_at']
    list_filter = ['is_active']
    search_fields = ['name', 'user__email']
