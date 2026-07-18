"""
Recognition app serializers - RevenueScheduleSerializer, RevenueEntrySerializer,
RecognitionRuleSerializer, ASC606ComplianceSerializer.
"""

from rest_framework import serializers

from .models import ASC606Compliance, RecognitionRule, RevenueEntry, RevenueSchedule


# =============================================================================
# Revenue Entry Serializer
# =============================================================================

class RevenueEntrySerializer(serializers.ModelSerializer):
    """Serializer for RevenueEntry model."""

    entry_type_display = serializers.CharField(
        source="get_entry_type_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    posted_by_name = serializers.SerializerMethodField()
    contract_number = serializers.CharField(
        source="schedule.contract.contract_number", read_only=True
    )

    class Meta:
        model = RevenueEntry
        fields = [
            "id", "schedule", "contract_number",
            "period_start", "period_end", "amount",
            "entry_type", "entry_type_display",
            "journal_entry_ref", "posted_date",
            "posted_by", "posted_by_name",
            "status", "status_display", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "posted_date", "posted_by", "created_at", "updated_at",
        ]

    def get_posted_by_name(self, obj):
        if obj.posted_by:
            return obj.posted_by.get_full_name()
        return None

    def validate(self, attrs):
        period_start = attrs.get("period_start")
        period_end = attrs.get("period_end")

        if period_start and period_end and period_end <= period_start:
            raise serializers.ValidationError(
                {"period_end": "Period end must be after period start."}
            )

        # Validate amount against schedule remaining
        schedule = attrs.get("schedule") or (self.instance.schedule if self.instance else None)
        amount = attrs.get("amount", 0)
        entry_type = attrs.get("entry_type", "recognized")

        if schedule and entry_type == "recognized" and amount > 0:
            remaining = schedule.total_amount - schedule.recognized_amount
            if self.instance:
                remaining += self.instance.amount
            if amount > remaining:
                raise serializers.ValidationError(
                    {"amount": f"Amount exceeds remaining schedule amount ({remaining})."}
                )

        return attrs


# =============================================================================
# Revenue Schedule Serializer
# =============================================================================

class RevenueScheduleSerializer(serializers.ModelSerializer):
    """Serializer for RevenueSchedule model with nested entries."""

    contract_number = serializers.CharField(
        source="contract.contract_number", read_only=True
    )
    client_name = serializers.CharField(
        source="contract.client.name", read_only=True
    )
    pattern_display = serializers.CharField(
        source="get_pattern_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    remaining_amount = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    recognition_percentage = serializers.DecimalField(
        max_digits=7, decimal_places=2, read_only=True
    )
    entries = RevenueEntrySerializer(many=True, read_only=True)

    class Meta:
        model = RevenueSchedule
        fields = [
            "id", "contract", "contract_number", "client_name",
            "performance_obligation", "total_amount",
            "recognized_amount", "deferred_amount",
            "start_date", "end_date",
            "pattern", "pattern_display",
            "status", "status_display",
            "completion_percentage", "notes",
            "remaining_amount", "recognition_percentage",
            "entries",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "recognized_amount", "deferred_amount",
            "created_at", "updated_at",
        ]

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError(
                {"end_date": "End date must be after start date."}
            )

        total_amount = attrs.get("total_amount", 0)
        if total_amount <= 0:
            raise serializers.ValidationError(
                {"total_amount": "Total amount must be greater than zero."}
            )

        return attrs


# =============================================================================
# Recognition Rule Serializer
# =============================================================================

class RecognitionRuleSerializer(serializers.ModelSerializer):
    """Serializer for RecognitionRule model."""

    recognition_pattern_display = serializers.CharField(
        source="get_recognition_pattern_display", read_only=True
    )
    timing_display = serializers.CharField(
        source="get_timing_display", read_only=True
    )

    class Meta:
        model = RecognitionRule
        fields = [
            "id", "name", "billing_model", "condition",
            "recognition_pattern", "recognition_pattern_display",
            "timing", "timing_display",
            "description", "priority", "is_active",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        qs = RecognitionRule.objects.filter(name=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A recognition rule with this name already exists."
            )
        return value


# =============================================================================
# ASC 606 Compliance Serializer
# =============================================================================

class ASC606ComplianceSerializer(serializers.ModelSerializer):
    """Serializer for ASC606Compliance model."""

    contract_number = serializers.CharField(
        source="contract.contract_number", read_only=True
    )
    client_name = serializers.CharField(
        source="contract.client.name", read_only=True
    )
    compliance_status_display = serializers.CharField(
        source="get_compliance_status_display", read_only=True
    )
    completion_percentage = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True
    )
    is_fully_compliant = serializers.BooleanField(read_only=True)
    reviewer_name = serializers.SerializerMethodField()

    class Meta:
        model = ASC606Compliance
        fields = [
            "id", "contract", "contract_number", "client_name",
            "step1_identified", "step1_notes", "step1_date",
            "step2_obligations_identified", "step2_notes", "step2_date",
            "step3_price_determined", "step3_notes", "step3_date",
            "step4_allocated", "step4_notes", "step4_date",
            "step5_recognized", "step5_notes", "step5_date",
            "compliance_status", "compliance_status_display",
            "last_review_date", "reviewer", "reviewer_name",
            "notes", "completion_percentage", "is_fully_compliant",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_reviewer_name(self, obj):
        if obj.reviewer:
            return obj.reviewer.get_full_name()
        return None

    def validate(self, attrs):
        """Auto-update compliance status based on steps."""
        steps = [
            attrs.get("step1_identified", getattr(self.instance, "step1_identified", False) if self.instance else False),
            attrs.get("step2_obligations_identified", getattr(self.instance, "step2_obligations_identified", False) if self.instance else False),
            attrs.get("step3_price_determined", getattr(self.instance, "step3_price_determined", False) if self.instance else False),
            attrs.get("step4_allocated", getattr(self.instance, "step4_allocated", False) if self.instance else False),
            attrs.get("step5_recognized", getattr(self.instance, "step5_recognized", False) if self.instance else False),
        ]

        if all(steps):
            attrs.setdefault("compliance_status", "compliant")
        elif any(steps):
            attrs.setdefault("compliance_status", "in_progress")

        return attrs
