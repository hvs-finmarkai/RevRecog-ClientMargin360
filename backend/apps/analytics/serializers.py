"""
Analytics app serializers - AnalyticsEventSerializer, MetricSnapshotSerializer.
"""

from rest_framework import serializers

from .models import AnalyticsEvent, MetricSnapshot


# =============================================================================
# Analytics Event Serializer
# =============================================================================

class AnalyticsEventSerializer(serializers.ModelSerializer):
    """Serializer for AnalyticsEvent model."""

    event_category_display = serializers.CharField(
        source="get_event_category_display", read_only=True
    )
    user_email = serializers.CharField(
        source="user.email", read_only=True, default=None
    )
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )

    class Meta:
        model = AnalyticsEvent
        fields = [
            "id", "organization", "organization_name",
            "event_type", "event_category", "event_category_display",
            "entity_type", "entity_id", "data",
            "user", "user_email", "session_id",
            "ip_address", "user_agent", "source",
            "created_at",
        ]
        read_only_fields = [
            "id", "ip_address", "user_agent", "created_at",
        ]

    def validate_event_type(self, value):
        if not value or "." not in value:
            raise serializers.ValidationError(
                "Event type must follow the format 'entity.action' (e.g., 'invoice.created')."
            )
        return value

    def validate_data(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Data must be a JSON object.")
        return value


# =============================================================================
# Metric Snapshot Serializer
# =============================================================================

class MetricSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for MetricSnapshot model."""

    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    period_type_display = serializers.CharField(
        source="get_period_type_display", read_only=True
    )
    metric_category_display = serializers.CharField(
        source="get_metric_category_display", read_only=True
    )
    trend_direction = serializers.CharField(read_only=True)

    class Meta:
        model = MetricSnapshot
        fields = [
            "id", "organization", "organization_name",
            "metric_name", "metric_value",
            "metric_category", "metric_category_display",
            "period_type", "period_type_display",
            "period_start", "period_end",
            "dimensions", "previous_value",
            "change_pct", "trend_direction", "metadata",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "change_pct", "trend_direction",
            "created_at", "updated_at",
        ]

    def validate(self, attrs):
        period_start = attrs.get("period_start")
        period_end = attrs.get("period_end")

        if period_start and period_end and period_end <= period_start:
            raise serializers.ValidationError(
                {"period_end": "Period end must be after period start."}
            )

        # Auto-calculate change percentage if previous value provided
        metric_value = attrs.get("metric_value")
        previous_value = attrs.get("previous_value")

        if metric_value is not None and previous_value is not None and previous_value != 0:
            attrs["change_pct"] = round(
                ((metric_value - previous_value) / abs(previous_value)) * 100, 2
            )

        return attrs
