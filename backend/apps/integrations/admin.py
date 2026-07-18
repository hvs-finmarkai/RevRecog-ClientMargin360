"""Integrations admin configuration."""
from django.contrib import admin
from .models import Integration, SyncLog


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ["name", "integration_type", "provider", "status", "last_sync_at"]
    list_filter = ["integration_type", "status"]


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ["integration", "status", "records_synced", "records_failed", "started_at"]
    list_filter = ["status"]
