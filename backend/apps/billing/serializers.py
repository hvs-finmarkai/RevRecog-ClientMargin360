"""
Billing app serializers - BillingModelSerializer, RateCardSerializer,
RateCardItemSerializer, BillingPeriodSerializer, BillingScheduleSerializer,
EscalationRuleSerializer.
"""

from django.utils import timezone
from rest_framework import serializers

from .models import (
    BillingModel,
    BillingPeriod,
    BillingSchedule,
    EscalationRule,
    RateCard,
    RateCardItem,
)


# =============================================================================
# Rate Card Item Serializer
# =============================================================================

class RateCardItemSerializer(serializers.ModelSerializer):
    """Serializer for RateCardItem model."""

    class Meta:
        model = RateCardItem
        fields = [
            "id", "rate_card", "role_name",
            "hourly_rate", "daily_rate", "monthly_rate",
            "overtime_multiplier", "minimum_hours",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        hourly_rate = attrs.get("hourly_rate", 0)
        daily_rate = attrs.get("daily_rate", 0)
        monthly_rate = attrs.get("monthly_rate", 0)

        if not any([hourly_rate, daily_rate, monthly_rate]):
            raise serializers.ValidationError(
                "At least one rate (hourly, daily, or monthly) must be specified."
            )
        return attrs


# =============================================================================
# Billing Model Serializer
# =============================================================================

class BillingModelSerializer(serializers.ModelSerializer):
    """Serializer for BillingModel model."""

    organization_name = serializers.CharField(
        source="organization.name", read_only=True, default=None
    )

    class Meta:
        model = BillingModel
        fields = [
            "id", "name", "code", "description", "rules",
            "is_active", "organization", "organization_name",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_code(self, value):
        qs = BillingModel.objects.filter(code=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A billing model with this code already exists."
            )
        return value.upper()


# =============================================================================
# Rate Card Serializer
# =============================================================================

class RateCardSerializer(serializers.ModelSerializer):
    """Serializer for RateCard model with nested items."""

    items = RateCardItemSerializer(many=True, required=False)
    client_name = serializers.CharField(source="client.name", read_only=True)
    contract_number = serializers.CharField(
        source="contract.contract_number", read_only=True, default=None
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    is_current = serializers.BooleanField(read_only=True)

    class Meta:
        model = RateCard
        fields = [
            "id", "client", "client_name",
            "contract", "contract_number",
            "name", "effective_from", "effective_to",
            "currency", "status", "status_display",
            "is_current", "notes", "items",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        effective_from = attrs.get("effective_from")
        effective_to = attrs.get("effective_to")

        if effective_from and effective_to and effective_to <= effective_from:
            raise serializers.ValidationError(
                {"effective_to": "Effective to date must be after effective from date."}
            )
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        rate_card = RateCard.objects.create(**validated_data)

        for item_data in items_data:
            item_data.pop("rate_card", None)
            RateCardItem.objects.create(rate_card=rate_card, **item_data)

        return rate_card

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                item_data.pop("rate_card", None)
                RateCardItem.objects.create(rate_card=instance, **item_data)

        return instance


# =============================================================================
# Billing Period Serializer
# =============================================================================

class BillingPeriodSerializer(serializers.ModelSerializer):
    """Serializer for BillingPeriod model."""

    contract_number = serializers.CharField(
        source="contract.contract_number", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    locked_by_name = serializers.SerializerMethodField()

    class Meta:
        model = BillingPeriod
        fields = [
            "id", "contract", "contract_number",
            "period_start", "period_end",
            "status", "status_display",
            "locked_at", "locked_by", "locked_by_name",
            "total_billable_amount", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "locked_at", "locked_by", "created_at", "updated_at",
        ]

    def get_locked_by_name(self, obj):
        if obj.locked_by:
            return obj.locked_by.get_full_name()
        return None

    def validate(self, attrs):
        period_start = attrs.get("period_start")
        period_end = attrs.get("period_end")

        if period_start and period_end and period_end <= period_start:
            raise serializers.ValidationError(
                {"period_end": "Period end must be after period start."}
            )

        # Prevent modification of locked periods
        if self.instance and self.instance.status == "locked":
            raise serializers.ValidationError(
                "Cannot modify a locked billing period."
            )

        return attrs


# =============================================================================
# Billing Schedule Serializer
# =============================================================================

class BillingScheduleSerializer(serializers.ModelSerializer):
    """Serializer for BillingSchedule model."""

    contract_number = serializers.CharField(
        source="contract.contract_number", read_only=True
    )
    frequency_display = serializers.CharField(
        source="get_frequency_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = BillingSchedule
        fields = [
            "id", "contract", "contract_number",
            "frequency", "frequency_display",
            "next_billing_date", "amount",
            "status", "status_display",
            "milestone_description", "last_generated_date",
            "is_overdue", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "last_generated_date", "created_at", "updated_at"]

    def get_is_overdue(self, obj):
        return (
            obj.status == "scheduled"
            and obj.next_billing_date < timezone.now().date()
        )


# =============================================================================
# Escalation Rule Serializer
# =============================================================================

class EscalationRuleSerializer(serializers.ModelSerializer):
    """Serializer for EscalationRule model."""

    contract_number = serializers.CharField(
        source="contract.contract_number", read_only=True
    )
    escalation_type_display = serializers.CharField(
        source="get_escalation_type_display", read_only=True
    )
    frequency_display = serializers.CharField(
        source="get_frequency_display", read_only=True
    )

    class Meta:
        model = EscalationRule
        fields = [
            "id", "contract", "contract_number",
            "escalation_type", "escalation_type_display",
            "percentage", "frequency", "frequency_display",
            "next_escalation_date", "last_applied",
            "auto_apply", "cap_percentage", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "last_applied", "created_at", "updated_at"]

    def validate(self, attrs):
        percentage = attrs.get("percentage", 0)
        cap_percentage = attrs.get("cap_percentage")

        if cap_percentage is not None and cap_percentage <= percentage:
            raise serializers.ValidationError(
                {"cap_percentage": "Cap percentage must be greater than escalation percentage."}
            )
        return attrs
