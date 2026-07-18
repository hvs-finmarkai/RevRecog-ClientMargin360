"""
Collections Management app views - ReceivableViewSet, PaymentReceiptViewSet,
CollectionScheduleViewSet, AgingBucketViewSet with aging_report and cash_forecast actions.
"""

from django.db.models import Avg, Count, Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    AgingBucket,
    CashForecast,
    CollectionSchedule,
    DunningRule,
    PaymentReceipt,
    Receivable,
)
from .serializers import (
    AgingBucketSerializer,
    CashForecastSerializer,
    CollectionScheduleSerializer,
    DunningRuleSerializer,
    PaymentReceiptSerializer,
    ReceivableSerializer,
)


class ReceivableViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing accounts receivable.
    """

    serializer_class = ReceivableSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["client", "status", "invoice"]
    search_fields = [
        "invoice__invoice_number", "client__name", "notes", "dispute_reason",
    ]
    ordering_fields = ["due_date", "amount", "aging_days", "status"]
    ordering = ["-due_date"]

    def get_queryset(self):
        return Receivable.objects.filter(
            invoice__organization=self.request.user.organization,
            is_deleted=False,
        ).select_related("invoice", "client")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=["post"])
    def send_reminder(self, request, pk=None):
        """Send a payment reminder for this receivable."""
        receivable = self.get_object()
        receivable.last_reminder_date = timezone.now().date()
        receivable.reminder_count += 1
        receivable.save(update_fields=["last_reminder_date", "reminder_count", "updated_at"])

        return Response({
            "detail": "Payment reminder sent.",
            "reminder_count": receivable.reminder_count,
        })


class PaymentReceiptViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payment receipts.
    """

    serializer_class = PaymentReceiptSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["receivable", "payment_mode", "reconciled"]
    search_fields = ["reference_number", "bank_reference", "notes"]
    ordering_fields = ["payment_date", "amount", "created_at"]
    ordering = ["-payment_date"]

    def get_queryset(self):
        return PaymentReceipt.objects.filter(
            receivable__invoice__organization=self.request.user.organization,
            is_deleted=False,
        ).select_related("receivable", "receivable__invoice")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=["post"])
    def reconcile(self, request, pk=None):
        """Reconcile a payment receipt."""
        receipt = self.get_object()
        if receipt.reconciled:
            return Response(
                {"detail": "Payment already reconciled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        receipt.reconciled = True
        receipt.reconciled_at = timezone.now()
        receipt.reconciled_by = request.user
        receipt.save(update_fields=[
            "reconciled", "reconciled_at", "reconciled_by", "updated_at",
        ])

        # Update receivable collected amount
        receivable = receipt.receivable
        receivable.amount_collected += receipt.amount
        if receivable.amount_collected >= receivable.amount:
            receivable.status = Receivable.StatusChoices.COLLECTED
        receivable.save(update_fields=["amount_collected", "status", "updated_at"])

        return Response({"detail": "Payment reconciled successfully."})


class CollectionScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing collection follow-up schedules.
    """

    serializer_class = CollectionScheduleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["client", "frequency", "escalation_level", "assigned_to"]
    search_fields = ["client__name", "notes", "last_contact_outcome"]
    ordering_fields = ["next_followup_date", "total_outstanding", "escalation_level"]
    ordering = ["next_followup_date"]

    def get_queryset(self):
        return CollectionSchedule.objects.filter(
            client__organization=self.request.user.organization,
            is_deleted=False,
        ).select_related("client", "assigned_to")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=False, methods=["get"])
    def overdue_followups(self, request):
        """List overdue follow-up schedules."""
        today = timezone.now().date()
        overdue = self.get_queryset().filter(next_followup_date__lt=today)
        serializer = self.get_serializer(overdue, many=True)
        return Response(serializer.data)


class AgingBucketViewSet(viewsets.ModelViewSet):
    """
    ViewSet for aging bucket data with aging_report and cash_forecast actions.
    """

    serializer_class = AgingBucketSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = []
    search_fields = []
    ordering_fields = ["as_of_date", "total"]
    ordering = ["-as_of_date"]

    def get_queryset(self):
        return AgingBucket.objects.filter(
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

    @action(detail=False, methods=["get"])
    def aging_report(self, request):
        """Generate a detailed aging report for the organization."""
        org = request.user.organization

        # Get the latest aging bucket
        latest_bucket = AgingBucket.objects.filter(
            organization=org, is_deleted=False,
        ).order_by("-as_of_date").first()

        # Client-level breakdown
        receivables = Receivable.objects.filter(
            invoice__organization=org,
            is_deleted=False,
        ).exclude(status=Receivable.StatusChoices.COLLECTED)

        client_aging = receivables.values("client__name").annotate(
            total_outstanding=Sum("amount"),
            total_collected=Sum("amount_collected"),
            avg_aging_days=Avg("aging_days"),
            count=Count("id"),
        ).order_by("-total_outstanding")

        report = {
            "as_of_date": str(timezone.now().date()),
            "summary": None,
            "client_breakdown": list(client_aging[:20]),
            "total_receivables": receivables.aggregate(
                total=Sum("amount")
            )["total"] or 0,
        }

        if latest_bucket:
            report["summary"] = {
                "current": str(latest_bucket.current_amount),
                "days_1_30": str(latest_bucket.days_30),
                "days_31_60": str(latest_bucket.days_60),
                "days_61_90": str(latest_bucket.days_90),
                "days_90_plus": str(latest_bucket.days_90_plus),
                "total": str(latest_bucket.total),
                "client_count": latest_bucket.client_count,
                "invoice_count": latest_bucket.invoice_count,
            }

        return Response(report)

    @action(detail=False, methods=["get"])
    def cash_forecast(self, request):
        """Get cash flow forecast based on receivables and historical patterns."""
        org = request.user.organization
        months = int(request.query_params.get("months", 3))

        forecasts = CashForecast.objects.filter(
            organization=org,
            is_deleted=False,
        ).order_by("-forecast_date")[:months]

        forecast_data = CashForecastSerializer(forecasts, many=True).data

        # Summary stats
        total_expected = forecasts.aggregate(
            total=Sum("expected_collections")
        )["total"] or 0

        return Response({
            "forecast_months": months,
            "total_expected_collections": str(total_expected),
            "forecasts": forecast_data,
        })
