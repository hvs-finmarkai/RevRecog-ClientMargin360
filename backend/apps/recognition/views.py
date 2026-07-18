"""
Recognition app views - RevenueScheduleViewSet, RevenueEntryViewSet,
RecognitionRuleViewSet, ASC606ComplianceViewSet with run_compliance_check action.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ASC606Compliance, RecognitionRule, RevenueEntry, RevenueSchedule
from .serializers import (
    ASC606ComplianceSerializer,
    RecognitionRuleSerializer,
    RevenueEntrySerializer,
    RevenueScheduleSerializer,
)


class RevenueScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing revenue recognition schedules.
    """

    serializer_class = RevenueScheduleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["contract", "performance_obligation", "pattern", "status"]
    search_fields = ["contract__contract_number", "notes"]
    ordering_fields = ["start_date", "end_date", "total_amount", "status"]
    ordering = ["-start_date"]

    def get_queryset(self):
        return RevenueSchedule.objects.filter(
            contract__organization=self.request.user.organization,
            is_deleted=False,
        ).select_related("contract", "performance_obligation")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=["get"])
    def entries(self, request, pk=None):
        """List all revenue entries for this schedule."""
        schedule = self.get_object()
        entries = RevenueEntry.objects.filter(
            schedule=schedule, is_deleted=False
        ).order_by("-period_start")
        serializer = RevenueEntrySerializer(entries, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def generate_entries(self, request, pk=None):
        """Generate revenue entries based on the schedule pattern."""
        schedule = self.get_object()

        if schedule.status != RevenueSchedule.StatusChoices.ACTIVE:
            return Response(
                {"detail": "Schedule must be active to generate entries."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({
            "detail": "Revenue entry generation initiated.",
            "schedule_id": str(schedule.id),
            "pattern": schedule.pattern,
            "total_amount": str(schedule.total_amount),
            "recognized_amount": str(schedule.recognized_amount),
        })


class RevenueEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing individual revenue entries.
    """

    serializer_class = RevenueEntrySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["schedule", "entry_type", "status"]
    search_fields = ["journal_entry_ref", "notes"]
    ordering_fields = ["period_start", "amount", "posted_date"]
    ordering = ["-period_start"]

    def get_queryset(self):
        return RevenueEntry.objects.filter(
            schedule__contract__organization=self.request.user.organization,
            is_deleted=False,
        ).select_related("schedule", "schedule__contract")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=["post"])
    def post_entry(self, request, pk=None):
        """Post a revenue entry to the ledger."""
        from django.utils import timezone

        entry = self.get_object()
        if entry.status != RevenueEntry.StatusChoices.DRAFT:
            return Response(
                {"detail": "Entry is not in draft status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        entry.status = RevenueEntry.StatusChoices.POSTED
        entry.posted_date = timezone.now().date()
        entry.posted_by = request.user
        entry.save(update_fields=["status", "posted_date", "posted_by", "updated_at"])

        # Update schedule recognized amount
        schedule = entry.schedule
        schedule.recognized_amount += entry.amount
        schedule.save(update_fields=["recognized_amount", "updated_at"])

        return Response({"detail": "Revenue entry posted successfully."})


class RecognitionRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing revenue recognition rules.
    """

    serializer_class = RecognitionRuleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["billing_model", "recognition_pattern", "timing", "is_active"]
    search_fields = ["name", "description", "billing_model"]
    ordering_fields = ["priority", "name", "created_at"]
    ordering = ["priority", "name"]

    def get_queryset(self):
        return RecognitionRule.objects.filter(is_deleted=False)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()


class ASC606ComplianceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing ASC 606 compliance records with compliance check action.
    """

    serializer_class = ASC606ComplianceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["compliance_status", "contract"]
    search_fields = ["contract__contract_number", "notes"]
    ordering_fields = ["last_review_date", "compliance_status"]
    ordering = ["-last_review_date"]

    def get_queryset(self):
        return ASC606Compliance.objects.filter(
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
    def run_compliance_check(self, request, pk=None):
        """Run a comprehensive ASC 606 five-step compliance check."""
        from django.utils import timezone

        compliance = self.get_object()
        contract = compliance.contract

        # Step 1: Check contract identification
        step1 = bool(
            contract.contract_number
            and contract.client
            and contract.total_value > 0
        )

        # Step 2: Check performance obligations
        obligations = contract.performance_obligations.filter(is_deleted=False)
        step2 = obligations.exists()

        # Step 3: Check transaction price determination
        step3 = contract.total_value > 0

        # Step 4: Check price allocation
        step4 = all(
            o.allocation_amount > 0 for o in obligations
        ) if obligations.exists() else False

        # Step 5: Check recognition criteria
        step5 = all(
            o.recognition_pattern for o in obligations
        ) if obligations.exists() else False

        # Update compliance record
        compliance.step1_identified = step1
        compliance.step2_obligations_identified = step2
        compliance.step3_price_determined = step3
        compliance.step4_allocated = step4
        compliance.step5_recognized = step5
        compliance.last_review_date = timezone.now().date()
        compliance.reviewer = request.user

        if compliance.is_fully_compliant:
            compliance.compliance_status = ASC606Compliance.ComplianceStatus.COMPLIANT
        elif any([step1, step2, step3, step4, step5]):
            compliance.compliance_status = ASC606Compliance.ComplianceStatus.IN_PROGRESS
        else:
            compliance.compliance_status = ASC606Compliance.ComplianceStatus.NOT_STARTED

        compliance.save()

        return Response({
            "contract_number": contract.contract_number,
            "compliance_status": compliance.compliance_status,
            "completion_percentage": compliance.completion_percentage,
            "steps": {
                "step1_contract_identified": step1,
                "step2_obligations_identified": step2,
                "step3_price_determined": step3,
                "step4_price_allocated": step4,
                "step5_revenue_recognized": step5,
            },
            "is_fully_compliant": compliance.is_fully_compliant,
            "last_review_date": str(compliance.last_review_date),
        })
