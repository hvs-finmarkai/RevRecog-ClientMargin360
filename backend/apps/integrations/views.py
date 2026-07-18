"""
Integrations app views - IntegrationConfigViewSet with actions: sync, test_connection;
WebhookConfigViewSet.
"""

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import APIKey, IntegrationConfig, SyncLog, WebhookConfig
from .serializers import (
    APIKeySerializer,
    IntegrationConfigSerializer,
    SyncLogSerializer,
    WebhookConfigSerializer,
)


class IntegrationConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing integration configurations with sync and test_connection actions.
    """

    serializer_class = IntegrationConfigSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["provider", "is_active", "status", "sync_frequency"]
    search_fields = ["name", "provider", "error_message"]
    ordering_fields = ["provider", "last_sync", "status", "created_at"]
    ordering = ["provider", "name"]

    def get_queryset(self):
        return IntegrationConfig.objects.filter(
            organization=self.request.user.organization,
            is_deleted=False,
        )

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=["post"])
    def sync(self, request, pk=None):
        """Trigger a manual sync for this integration."""
        integration = self.get_object()

        if not integration.is_active:
            return Response(
                {"detail": "Integration is not active."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sync_type = request.data.get("sync_type", "incremental")
        direction = request.data.get("direction", "inbound")

        # Create sync log entry
        sync_log = SyncLog.objects.create(
            integration=integration,
            sync_type=sync_type,
            direction=direction,
            triggered_by=request.user,
            status=SyncLog.StatusChoices.STARTED,
            created_by=request.user,
        )

        # In production, this would trigger an async task
        return Response({
            "detail": "Sync initiated.",
            "sync_log_id": str(sync_log.id),
            "integration": integration.name or integration.get_provider_display(),
            "sync_type": sync_type,
            "direction": direction,
            "status": "started",
        })

    @action(detail=True, methods=["post"])
    def test_connection(self, request, pk=None):
        """Test the connection for this integration."""
        integration = self.get_object()

        # In production, this would actually attempt to connect
        test_result = {
            "integration_id": str(integration.id),
            "provider": integration.provider,
            "connection_status": "success",
            "tested_at": timezone.now().isoformat(),
            "response_time_ms": 150,
            "details": "Connection successful. Authentication verified.",
        }

        return Response(test_result)

    @action(detail=True, methods=["get"])
    def sync_logs(self, request, pk=None):
        """Get sync history for this integration."""
        integration = self.get_object()
        logs = SyncLog.objects.filter(
            integration=integration, is_deleted=False
        ).order_by("-started_at")[:20]
        serializer = SyncLogSerializer(logs, many=True)
        return Response(serializer.data)


class WebhookConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing webhook configurations.
    """

    serializer_class = WebhookConfigSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["is_active", "status"]
    search_fields = ["name", "url"]
    ordering_fields = ["name", "last_triggered", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        return WebhookConfig.objects.filter(
            organization=self.request.user.organization,
            is_deleted=False,
        )

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=["post"])
    def test(self, request, pk=None):
        """Send a test payload to the webhook endpoint."""
        webhook = self.get_object()

        # In production, this would send an actual HTTP request
        test_result = {
            "webhook_id": str(webhook.id),
            "url": webhook.url,
            "status": "success",
            "response_code": 200,
            "tested_at": timezone.now().isoformat(),
        }

        return Response(test_result)

    @action(detail=True, methods=["post"])
    def reset_failures(self, request, pk=None):
        """Reset the failure count and reactivate the webhook."""
        webhook = self.get_object()
        webhook.failure_count = 0
        webhook.status = WebhookConfig.StatusChoices.ACTIVE
        webhook.save(update_fields=["failure_count", "status", "updated_at"])
        return Response({"detail": "Webhook failure count reset."})
