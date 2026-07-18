"""
Leakage app serializers - LeakageDetectionSerializer, LeakageRuleSerializer,
LeakageAlertSerializer, LeakageResolutionSerializer, LeakageDashboardSerializer.
"""

from rest_framework import serializers

from .models import LeakageAlert, LeakageDetection, LeakageResolution, LeakageRule


# =============================================================================
# Leakage Rule Serializer
# =============================================================================

class LeakageRuleSerializer(serializers.ModelSerializer):
    """Serializer for LeakageRule model."""

    detection_type_display = serializers.CharField(
        source="get_detection_type_display", read_only=True
    )
    severity_display = serializers.CharField(
        source="get_severity_display", read_only=True
    )
    detection_count = serializers.SerializerMethodField()

    class Meta:
        model = LeakageRule
        fields = [
            "id", "name", "organization",
            "detection_type", "detection_type_display",
            "condition", "threshold",
            "severity", "severity_display",
            "is_active", "auto_alert", "cooldown_hours",
            "description", "detection_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_detection_count(self, obj):
        return obj.detections.count()

    def validate_threshold(self, value):
        if value < 0:
            raise serializers.ValidationError("Threshold cannot be negative.")
        return value


# =============================================================================
# Leakage Alert Serializer
# =============================================================================

class LeakageAlertSerializer(serializers.ModelSerializer):
    """Serializer for LeakageAlert model."""

    alert_type_display = serializers.CharField(
        source="get_alert_type_display", read_only=True
    )
    acknowledged_by_name = serializers.SerializerMethodField()

    class Meta:
        model = LeakageAlert
        fields = [
            "id", "detection", "alert_type", "alert_type_display",
            "recipients", "sent_at",
            "acknowledged_at", "acknowledged_by", "acknowledged_by_name",
            "message", "delivery_status",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "sent_at", "acknowledged_at", "acknowledged_by",
            "created_at", "updated_at",
        ]

    def get_acknowledged_by_name(self, obj):
        if obj.acknowledged_by:
            return obj.acknowledged_by.get_full_name()
        return None


# =============================================================================
# Leakage Resolution Serializer
# =============================================================================

class LeakageResolutionSerializer(serializers.ModelSerializer):
    """Serializer for LeakageResolution model."""

    action_taken_display = serializers.CharField(
        source="get_action_taken_display", read_only=True
    )
    recovery_percentage = serializers.DecimalField(
        max_digits=7, decimal_places=2, read_only=True
    )
    detection_amount = serializers.DecimalField(
        source="detection.amount", max_digits=15, decimal_places=2, read_only=True
    )

    class Meta:
        model = LeakageResolution
        fields = [
            "id", "detection", "detection_amount",
            "action_taken", "action_taken_display",
            "description", "amount_recovered", "recovery_date",
            "invoice_generated", "preventive_measures",
            "recovery_percentage",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        amount_recovered = attrs.get("amount_recovered", 0)
        detection = attrs.get("detection") or (self.instance.detection if self.instance else None)

        if detection and amount_recovered > detection.amount:
            raise serializers.ValidationError(
                {"amount_recovered": "Recovery amount cannot exceed detected leakage amount."}
            )
        return attrs


# =============================================================================
# Leakage Detection Serializer
# =============================================================================

class LeakageDetectionSerializer(serializers.ModelSerializer):
    """Serializer for LeakageDetection model with nested alerts and resolution."""

    client_name = serializers.CharField(source="client.name", read_only=True)
    contract_number = serializers.CharField(
        source="contract.contract_number", read_only=True, default=None
    )
    detection_type_display = serializers.CharField(
        source="get_detection_type_display", read_only=True
    )
    severity_display = serializers.CharField(
        source="get_severity_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    resolved_by_name = serializers.SerializerMethodField()
    rule_name = serializers.CharField(
        source="rule.name", read_only=True, default=None
    )
    alerts = LeakageAlertSerializer(many=True, read_only=True)
    resolution = LeakageResolutionSerializer(read_only=True)

    class Meta:
        model = LeakageDetection
        fields = [
            "id", "organization", "client", "client_name",
            "contract", "contract_number",
            "detection_type", "detection_type_display",
            "amount", "description",
            "severity", "severity_display",
            "detected_at", "status", "status_display",
            "resolved_at", "resolved_by", "resolved_by_name",
            "resolution_notes", "rule", "rule_name",
            "evidence_data",
            "alerts", "resolution",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "detected_at", "resolved_at", "resolved_by",
            "created_at", "updated_at",
        ]

    def get_resolved_by_name(self, obj):
        if obj.resolved_by:
            return obj.resolved_by.get_full_name()
        return None


# =============================================================================
# Leakage Dashboard Serializer (Read-only aggregate)
# =============================================================================

class LeakageDashboardSerializer(serializers.Serializer):
    """Read-only serializer for leakage dashboard summary data."""

    total_leakage_amount = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    open_detections_count = serializers.IntegerField(read_only=True)
    resolved_count = serializers.IntegerField(read_only=True)
    total_recovered = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    recovery_rate = serializers.DecimalField(
        max_digits=7, decimal_places=2, read_only=True
    )
    by_severity = serializers.DictField(read_only=True)
    by_detection_type = serializers.DictField(read_only=True)
    top_clients = serializers.ListField(read_only=True)
    trend_data = serializers.ListField(read_only=True)
    avg_resolution_days = serializers.DecimalField(
        max_digits=7, decimal_places=2, read_only=True
    )
