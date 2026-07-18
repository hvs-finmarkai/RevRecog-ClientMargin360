"""
Leakage app views - LeakageDetectionViewSet with actions: detect, resolve, dashboard;
LeakageRuleViewSet, LeakageAlertViewSet.
"""

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import LeakageAlert, LeakageDetection, LeakageResolution, LeakageRule
from .serializers import (
    LeakageAlertSerializer,
    LeakageDashboardSerializer,
    LeakageDetectionSerializer,
    LeakageResolutionSerializer,
    LeakageRuleSerializer,
)


class LeakageDetectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing revenue leakage detections with detect, resolve, and dashboard actions.
    """

    serializer_class = LeakageDetectionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = [
        "detection_type", "status", "severity", "client", "contract",
    ]
    search_fields = ["description", "client__name", "contract__contract_number"]
    ordering_fields = ["detected_at", "amount", "severity", "status"]
    ordering = ["-detected_at"]

    def get_queryset(self):
        return LeakageDetection.objects.filter(
            organization=self.request.user.organization,
            is_deleted=False,
        ).select_related("client", "contract", "rule")

    def get_serializer_class(self):
        if self.action == "resolve":
            return LeakageResolutionSerializer
        if self.action == "dashboard":
            return LeakageDashboardSerializer
        return LeakageDetectionSerializer

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=False, methods=["post"])
    def detect(self, request):
        """Trigger leakage detection scan across all active contracts."""
        org = request.user.organization
        active_rules = LeakageRule.objects.filter(
            is_active=True,
            is_deleted=False,
        ).filter(
            organization=org,
        ) | LeakageRule.objects.filter(
            is_active=True,
            is_deleted=False,
            organization__isnull=True,
        )

        # In production, this would trigger async Celery tasks
        return Response({
            "detail": "Leakage detection scan initiated.",
            "rules_evaluated": active_rules.count(),
            "scan_initiated_at": timezone.now().isoformat(),
            "status": "processing",
        })

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """Resolve a leakage detection with action details."""
        detection = self.get_object()

        if detection.status == LeakageDetection.StatusChoices.RESOLVED:
            return Response(
                {"detail": "This leakage has already been resolved."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = LeakageResolutionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            detection=detection,
            created_by=request.user,
        )

        detection.status = LeakageDetection.StatusChoices.RESOLVED
        detection.resolved_at = timezone.now()
        detection.resolved_by = request.user
        detection.resolution_notes = request.data.get("description", "")
        detection.save(update_fields=[
            "status", "resolved_at", "resolved_by", "resolution_notes", "updated_at",
        ])

        return Response({"detail": "Leakage resolved successfully."})

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        """Get leakage detection dashboard summary."""
        org = request.user.organization
        detections = LeakageDetection.objects.filter(
            organization=org, is_deleted=False,
        )

        open_detections = detections.filter(
            status__in=[
                LeakageDetection.StatusChoices.OPEN,
                LeakageDetection.StatusChoices.ACKNOWLEDGED,
                LeakageDetection.StatusChoices.IN_PROGRESS,
            ]
        )

        by_severity = open_detections.values("severity").annotate(
            count=Count("id"),
            total_amount=Sum("amount"),
        )

        by_type = open_detections.values("detection_type").annotate(
            count=Count("id"),
            total_amount=Sum("amount"),
        )

        total_open_amount = open_detections.aggregate(
            total=Sum("amount")
        )["total"] or 0

        resolved_this_month = detections.filter(
            status=LeakageDetection.StatusChoices.RESOLVED,
            resolved_at__month=timezone.now().month,
            resolved_at__year=timezone.now().year,
        )

        recovered_amount = LeakageResolution.objects.filter(
            detection__organization=org,
        ).aggregate(total=Sum("amount_recovered"))["total"] or 0

        return Response({
            "total_open_detections": open_detections.count(),
            "total_open_amount": str(total_open_amount),
            "resolved_this_month": resolved_this_month.count(),
            "total_recovered_amount": str(recovered_amount),
            "by_severity": list(by_severity),
            "by_type": list(by_type),
        })


class LeakageRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leakage detection rules.
    """

    serializer_class = LeakageRuleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["detection_type", "severity", "is_active", "auto_alert"]
    search_fields = ["name", "description"]
    ordering_fields = ["severity", "name", "threshold", "created_at"]
    ordering = ["severity", "name"]

    def get_queryset(self):
        user = self.request.user
        return LeakageRule.objects.filter(
            is_deleted=False,
        ).filter(
            organization=user.organization,
        ) | LeakageRule.objects.filter(
            is_deleted=False,
            organization__isnull=True,
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


class LeakageAlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing leakage alerts.
    """

    serializer_class = LeakageAlertSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["detection", "alert_type", "delivery_status"]
    search_fields = ["message", "detection__description"]
    ordering_fields = ["sent_at", "acknowledged_at"]
    ordering = ["-sent_at"]

    def get_queryset(self):
        return LeakageAlert.objects.filter(
            detection__organization=self.request.user.organization,
            is_deleted=False,
        ).select_related("detection")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        """Acknowledge a leakage alert."""
        alert = self.get_object()
        alert.acknowledged_at = timezone.now()
        alert.acknowledged_by = request.user
        alert.save(update_fields=["acknowledged_at", "acknowledged_by", "updated_at"])
        return Response({"detail": "Alert acknowledged."})
