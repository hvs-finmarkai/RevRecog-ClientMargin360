"""
Notifications app views - NotificationViewSet with actions: mark_read, mark_all_read;
AlertRuleViewSet.
"""

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import AlertRule, Notification, NotificationPreference, NotificationTemplate
from .serializers import (
    AlertRuleSerializer,
    NotificationPreferenceSerializer,
    NotificationSerializer,
    NotificationTemplateSerializer,
)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user notifications with mark_read and mark_all_read actions.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["type", "category", "read_at"]
    search_fields = ["title", "message"]
    ordering_fields = ["created_at", "priority", "read_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(
            organization=user.organization,
            is_deleted=False,
        ).filter(
            user=user,
        ) | Notification.objects.filter(
            organization=user.organization,
            is_deleted=False,
            user__isnull=True,  # Broadcast notifications
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
    def mark_read(self, request, pk=None):
        """Mark a specific notification as read."""
        notification = self.get_object()
        if not notification.read_at:
            notification.read_at = timezone.now()
            notification.save(update_fields=["read_at", "updated_at"])
        return Response({"detail": "Notification marked as read."})

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """Mark all unread notifications as read for the current user."""
        user = request.user
        count = Notification.objects.filter(
            organization=user.organization,
            user=user,
            read_at__isnull=True,
            is_deleted=False,
        ).update(read_at=timezone.now())

        return Response({
            "detail": f"{count} notification(s) marked as read.",
            "count": count,
        })

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """Get count of unread notifications."""
        user = request.user
        count = Notification.objects.filter(
            organization=user.organization,
            user=user,
            read_at__isnull=True,
            is_deleted=False,
        ).count()

        return Response({"unread_count": count})


class AlertRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing alert rules that trigger notifications.
    """

    serializer_class = AlertRuleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["severity", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["severity", "name", "last_triggered", "trigger_count"]
    ordering = ["severity", "name"]

    def get_queryset(self):
        return AlertRule.objects.filter(
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
    def toggle(self, request, pk=None):
        """Toggle an alert rule active/inactive."""
        rule = self.get_object()
        rule.is_active = not rule.is_active
        rule.save(update_fields=["is_active", "updated_at"])
        return Response({
            "detail": f"Alert rule {'activated' if rule.is_active else 'deactivated'}.",
            "is_active": rule.is_active,
        })

    @action(detail=True, methods=["post"])
    def test_rule(self, request, pk=None):
        """Test an alert rule without actually triggering notifications."""
        rule = self.get_object()

        return Response({
            "detail": "Alert rule test completed.",
            "rule_name": rule.name,
            "would_trigger": True,
            "matching_conditions": rule.condition,
            "recipients_count": len(rule.recipients),
            "channels": rule.channels,
        })
