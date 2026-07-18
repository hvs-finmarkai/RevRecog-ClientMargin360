"""
Billing app views - BillingModelViewSet, RateCardViewSet,
BillingPeriodViewSet, BillingScheduleViewSet, EscalationRuleViewSet.
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    BillingModel,
    BillingPeriod,
    BillingSchedule,
    EscalationRule,
    RateCard,
    RateCardItem,
)
from .serializers import (
    BillingModelSerializer,
    BillingPeriodSerializer,
    BillingScheduleSerializer,
    EscalationRuleSerializer,
    RateCardItemSerializer,
    RateCardSerializer,
)


class BillingModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing billing model configurations.
    """

    serializer_class = BillingModelSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["is_active", "organization"]
    search_fields = ["name", "code", "description"]
    ordering_fields = ["name", "code", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        user = self.request.user
        return BillingModel.objects.filter(
            is_deleted=False,
        ).filter(
            organization=user.organization,
        ) | BillingModel.objects.filter(
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


class RateCardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing rate cards with nested items.
    """

    serializer_class = RateCardSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["client", "contract", "status", "currency"]
    search_fields = ["name", "client__name"]
    ordering_fields = ["effective_from", "name", "created_at"]
    ordering = ["-effective_from"]

    def get_queryset(self):
        return RateCard.objects.filter(
            client__organization=self.request.user.organization,
            is_deleted=False,
        ).select_related("client", "contract")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=["get"])
    def items(self, request, pk=None):
        """List all items in this rate card."""
        rate_card = self.get_object()
        items = RateCardItem.objects.filter(
            rate_card=rate_card, is_deleted=False
        )
        serializer = RateCardItemSerializer(items, many=True)
        return Response(serializer.data)


class BillingPeriodViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing billing periods.
    """

    serializer_class = BillingPeriodSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["contract", "status"]
    search_fields = ["contract__contract_number", "notes"]
    ordering_fields = ["period_start", "period_end", "status"]
    ordering = ["-period_start"]

    def get_queryset(self):
        return BillingPeriod.objects.filter(
            contract__organization=self.request.user.organization,
            is_deleted=False,
        ).select_related("contract")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=["post"])
    def lock(self, request, pk=None):
        """Lock a billing period to prevent further modifications."""
        from django.utils import timezone

        period = self.get_object()
        period.status = BillingPeriod.StatusChoices.LOCKED
        period.locked_at = timezone.now()
        period.locked_by = request.user
        period.save(update_fields=["status", "locked_at", "locked_by", "updated_at"])
        return Response({"detail": "Billing period locked successfully."})


class BillingScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing billing schedules.
    """

    serializer_class = BillingScheduleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["contract", "frequency", "status"]
    search_fields = ["contract__contract_number", "milestone_description"]
    ordering_fields = ["next_billing_date", "amount", "frequency"]
    ordering = ["next_billing_date"]

    def get_queryset(self):
        return BillingSchedule.objects.filter(
            contract__organization=self.request.user.organization,
            is_deleted=False,
        ).select_related("contract")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """List billing schedules due in the next 30 days."""
        from django.utils import timezone
        from datetime import timedelta

        today = timezone.now().date()
        upcoming = self.get_queryset().filter(
            next_billing_date__gte=today,
            next_billing_date__lte=today + timedelta(days=30),
            status=BillingSchedule.StatusChoices.SCHEDULED,
        )
        serializer = self.get_serializer(upcoming, many=True)
        return Response(serializer.data)


class EscalationRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing rate escalation rules.
    """

    serializer_class = EscalationRuleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["contract", "escalation_type", "frequency", "auto_apply"]
    search_fields = ["contract__contract_number", "notes"]
    ordering_fields = ["next_escalation_date", "percentage", "created_at"]
    ordering = ["next_escalation_date"]

    def get_queryset(self):
        return EscalationRule.objects.filter(
            contract__organization=self.request.user.organization,
            is_deleted=False,
        ).select_related("contract")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=False, methods=["get"])
    def pending(self, request):
        """List escalation rules pending application."""
        from django.utils import timezone

        today = timezone.now().date()
        pending = self.get_queryset().filter(
            next_escalation_date__lte=today,
            auto_apply=False,
        )
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)
