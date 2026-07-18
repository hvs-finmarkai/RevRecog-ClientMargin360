"""
Integrations app serializers - IntegrationConfigSerializer, SyncLogSerializer,
WebhookConfigSerializer, APIKeySerializer.
"""

from django.utils import timezone
from rest_framework import serializers

from .models import APIKey, IntegrationConfig, SyncLog, WebhookConfig


# =============================================================================
# Sync Log Serializer
# =============================================================================

class SyncLogSerializer(serializers.ModelSerializer):
    """Serializer for SyncLog model."""

    integration_name = serializers.SerializerMethodField()
    sync_type_display = serializers.CharField(
        source="get_sync_type_display", read_only=True
    )
    direction_display = serializers.CharField(
        source="get_direction_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    triggered_by_name = serializers.SerializerMethodField()
    duration_seconds = serializers.FloatField(read_only=True)
    success_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = SyncLog
        fields = [
            "id", "integration", "integration_name",
            "sync_type", "sync_type_display",
            "direction", "direction_display",
            "started_at", "completed_at",
            "records_synced", "records_failed", "records_skipped",
            "errors", "status", "status_display",
            "triggered_by", "triggered_by_name",
            "summary", "duration_seconds", "success_rate",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "started_at", "completed_at",
            "records_synced", "records_failed", "records_skipped",
            "errors", "status", "triggered_by",
            "created_at", "updated_at",
        ]

    def get_integration_name(self, obj):
        return obj.integration.name or obj.integration.get_provider_display()

    def get_triggered_by_name(self, obj):
        if obj.triggered_by:
            return obj.triggered_by.get_full_name()
        return None


# =============================================================================
# Integration Config Serializer
# =============================================================================

class IntegrationConfigSerializer(serializers.ModelSerializer):
    """Serializer for IntegrationConfig model."""

    provider_display = serializers.CharField(
        source="get_provider_display", read_only=True
    )
    sync_frequency_display = serializers.CharField(
        source="get_sync_frequency_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    recent_sync_logs = serializers.SerializerMethodField()
    health_status = serializers.SerializerMethodField()

    class Meta:
        model = IntegrationConfig
        fields = [
            "id", "organization", "organization_name",
            "provider", "provider_display", "name",
            "config", "is_active", "last_sync",
            "sync_frequency", "sync_frequency_display",
            "status", "status_display",
            "error_message", "last_error_at",
            "sync_mappings", "metadata",
            "recent_sync_logs", "health_status",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "last_sync", "last_error_at",
            "error_message", "created_at", "updated_at",
        ]

    def get_recent_sync_logs(self, obj):
        recent = obj.sync_logs.order_by("-started_at")[:5]
        return SyncLogSerializer(recent, many=True).data

    def get_health_status(self, obj):
        """Determine integration health based on recent activity."""
        if not obj.is_active:
            return "inactive"
        if obj.status == "error":
            return "error"
        if obj.last_sync:
            hours_since_sync = (
                timezone.now() - obj.last_sync
            ).total_seconds() / 3600
            if hours_since_sync > 48:
                return "stale"
        return "healthy"

    def validate_config(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Config must be a JSON object.")
        return value


# =============================================================================
# Webhook Config Serializer
# =============================================================================

class WebhookConfigSerializer(serializers.ModelSerializer):
    """Serializer for WebhookConfig model."""

    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    is_healthy = serializers.SerializerMethodField()

    class Meta:
        model = WebhookConfig
        fields = [
            "id", "organization", "organization_name",
            "name", "url", "events",
            "secret", "is_active",
            "last_triggered", "last_response_code",
            "failure_count", "max_retries", "timeout_seconds",
            "headers", "status", "status_display",
            "is_healthy",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "last_triggered", "last_response_code",
            "failure_count", "status", "created_at", "updated_at",
        ]
        extra_kwargs = {
            "secret": {"write_only": True},
        }

    def get_is_healthy(self, obj):
        return obj.failure_count < obj.max_retries and obj.is_active

    def validate_url(self, value):
        if not value.startswith("https://"):
            raise serializers.ValidationError(
                "Webhook URL must use HTTPS for security."
            )
        return value

    def validate_events(self, value):
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError(
                "At least one event type must be specified."
            )
        return value


# =============================================================================
# API Key Serializer
# =============================================================================

class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for APIKey model."""

    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    created_by_name = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.SerializerMethodField()

    class Meta:
        model = APIKey
        fields = [
            "id", "organization", "organization_name",
            "name", "key_prefix", "permissions",
            "is_active", "expires_at", "last_used",
            "last_used_ip", "usage_count", "rate_limit",
            "status", "status_display",
            "created_by_user", "created_by_name",
            "is_expired", "days_until_expiry",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "key_prefix", "last_used", "last_used_ip",
            "usage_count", "status", "created_by_user",
            "created_at", "updated_at",
        ]

    def get_created_by_name(self, obj):
        if obj.created_by_user:
            return obj.created_by_user.get_full_name()
        return None

    def get_days_until_expiry(self, obj):
        if obj.expires_at:
            remaining = (obj.expires_at - timezone.now()).days
            return max(0, remaining)
        return None

    def validate_permissions(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Permissions must be a list.")
        valid_scopes = [
            "read:contracts", "write:contracts",
            "read:invoices", "write:invoices",
            "read:clients", "write:clients",
            "read:reports", "write:reports",
            "read:analytics", "admin",
        ]
        invalid = [p for p in value if p not in valid_scopes]
        if invalid:
            raise serializers.ValidationError(
                f"Invalid permission scopes: {', '.join(invalid)}"
            )
        return value
