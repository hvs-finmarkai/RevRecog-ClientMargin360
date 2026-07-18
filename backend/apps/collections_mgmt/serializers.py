"""
Collections Management app serializers - ReceivableSerializer, PaymentReceiptSerializer,
CollectionScheduleSerializer, AgingBucketSerializer, DunningRuleSerializer,
CashForecastSerializer.
"""

from django.utils import timezone
from rest_framework import serializers

from .models import (
    AgingBucket,
    CashForecast,
    CollectionSchedule,
    DunningRule,
    PaymentReceipt,
    Receivable,
)


# =============================================================================
# Payment Receipt Serializer
# =============================================================================

class PaymentReceiptSerializer(serializers.ModelSerializer):
    """Serializer for PaymentReceipt model."""

    payment_mode_display = serializers.CharField(
        source="get_payment_mode_display", read_only=True
    )
    reconciled_by_name = serializers.SerializerMethodField()
    invoice_number = serializers.CharField(
        source="receivable.invoice.invoice_number", read_only=True
    )

    class Meta:
        model = PaymentReceipt
        fields = [
            "id", "receivable", "invoice_number",
            "amount", "payment_date",
            "payment_mode", "payment_mode_display",
            "reference_number", "bank_reference",
            "reconciled", "reconciled_at",
            "reconciled_by", "reconciled_by_name",
            "tds_deducted", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "reconciled_at", "reconciled_by",
            "created_at", "updated_at",
        ]

    def get_reconciled_by_name(self, obj):
        if obj.reconciled_by:
            return obj.reconciled_by.get_full_name()
        return None

    def validate(self, attrs):
        amount = attrs.get("amount", 0)
        receivable = attrs.get("receivable") or (self.instance.receivable if self.instance else None)

        if receivable:
            balance = receivable.amount - receivable.amount_collected
            if self.instance:
                balance += self.instance.amount
            if amount > balance:
                raise serializers.ValidationError(
                    {"amount": f"Payment amount exceeds outstanding balance ({balance})."}
                )

        tds_deducted = attrs.get("tds_deducted", 0)
        if tds_deducted > amount:
            raise serializers.ValidationError(
                {"tds_deducted": "TDS deducted cannot exceed payment amount."}
            )

        return attrs


# =============================================================================
# Receivable Serializer
# =============================================================================

class ReceivableSerializer(serializers.ModelSerializer):
    """Serializer for Receivable model with nested payments."""

    client_name = serializers.CharField(source="client.name", read_only=True)
    invoice_number = serializers.CharField(
        source="invoice.invoice_number", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    balance = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    is_overdue = serializers.BooleanField(read_only=True)
    payment_receipts = PaymentReceiptSerializer(many=True, read_only=True)
    days_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Receivable
        fields = [
            "id", "invoice", "invoice_number",
            "client", "client_name",
            "amount", "amount_collected", "due_date",
            "status", "status_display",
            "aging_days", "last_reminder_date",
            "next_action_date", "reminder_count",
            "notes", "dispute_reason",
            "balance", "is_overdue", "days_overdue",
            "payment_receipts",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "amount_collected", "aging_days",
            "created_at", "updated_at",
        ]

    def get_days_overdue(self, obj):
        if obj.status == "collected":
            return 0
        today = timezone.now().date()
        days = (today - obj.due_date).days
        return max(0, days)


# =============================================================================
# Collection Schedule Serializer
# =============================================================================

class CollectionScheduleSerializer(serializers.ModelSerializer):
    """Serializer for CollectionSchedule model."""

    client_name = serializers.CharField(source="client.name", read_only=True)
    frequency_display = serializers.CharField(
        source="get_frequency_display", read_only=True
    )
    escalation_level_display = serializers.CharField(
        source="get_escalation_level_display", read_only=True
    )
    assigned_to_name = serializers.SerializerMethodField()
    is_followup_due = serializers.SerializerMethodField()

    class Meta:
        model = CollectionSchedule
        fields = [
            "id", "client", "client_name",
            "frequency", "frequency_display",
            "next_followup_date", "assigned_to", "assigned_to_name",
            "escalation_level", "escalation_level_display",
            "notes", "total_outstanding",
            "last_contact_date", "last_contact_outcome",
            "is_followup_due",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name()
        return None

    def get_is_followup_due(self, obj):
        return obj.next_followup_date <= timezone.now().date()


# =============================================================================
# Aging Bucket Serializer
# =============================================================================

class AgingBucketSerializer(serializers.ModelSerializer):
    """Serializer for AgingBucket model."""

    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    overdue_percentage = serializers.SerializerMethodField()

    class Meta:
        model = AgingBucket
        fields = [
            "id", "organization", "organization_name",
            "as_of_date", "current_amount",
            "days_30", "days_60", "days_90", "days_90_plus",
            "total", "client_count", "invoice_count",
            "overdue_percentage",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "total", "created_at", "updated_at"]

    def get_overdue_percentage(self, obj):
        if obj.total > 0:
            overdue = obj.days_30 + obj.days_60 + obj.days_90 + obj.days_90_plus
            return round((overdue / obj.total) * 100, 2)
        return 0


# =============================================================================
# Dunning Rule Serializer
# =============================================================================

class DunningRuleSerializer(serializers.ModelSerializer):
    """Serializer for DunningRule model."""

    action_display = serializers.CharField(
        source="get_action_display", read_only=True
    )
    template_name = serializers.CharField(
        source="template.name", read_only=True, default=None
    )

    class Meta:
        model = DunningRule
        fields = [
            "id", "name", "organization",
            "days_overdue", "action", "action_display",
            "template", "template_name",
            "auto_execute", "is_active", "priority",
            "description",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        days_overdue = attrs.get("days_overdue", 0)
        if days_overdue < 0:
            raise serializers.ValidationError(
                {"days_overdue": "Days overdue cannot be negative."}
            )
        return attrs


# =============================================================================
# Cash Forecast Serializer
# =============================================================================

class CashForecastSerializer(serializers.ModelSerializer):
    """Serializer for CashForecast model."""

    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    methodology_display = serializers.CharField(
        source="get_methodology_display", read_only=True
    )
    accuracy = serializers.SerializerMethodField()
    variance_pct = serializers.SerializerMethodField()

    class Meta:
        model = CashForecast
        fields = [
            "id", "organization", "organization_name",
            "forecast_date", "period_start", "period_end",
            "expected_collections", "actual_collections",
            "confidence", "methodology", "methodology_display",
            "breakdown", "variance",
            "accuracy", "variance_pct",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "variance", "created_at", "updated_at",
        ]

    def get_accuracy(self, obj):
        return obj.accuracy

    def get_variance_pct(self, obj):
        if obj.expected_collections and obj.actual_collections:
            return round(
                ((obj.actual_collections - obj.expected_collections)
                 / obj.expected_collections) * 100,
                2
            )
        return None

    def validate(self, attrs):
        period_start = attrs.get("period_start")
        period_end = attrs.get("period_end")

        if period_start and period_end and period_end <= period_start:
            raise serializers.ValidationError(
                {"period_end": "Period end must be after period start."}
            )

        confidence = attrs.get("confidence", 0)
        if confidence < 0 or confidence > 100:
            raise serializers.ValidationError(
                {"confidence": "Confidence must be between 0 and 100."}
            )

        return attrs
