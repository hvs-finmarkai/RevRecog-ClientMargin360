"""
Notifications app serializers - NotificationSerializer, NotificationTemplateSerializer,
NotificationPreferenceSerializer, AlertRuleSerializer.
"""

from rest_framework import serializers

from .models import AlertRule, Notification, NotificationPreference, NotificationTemplate


# =============================================================================
# Notification Template Serializer
# =============================================================================

class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for NotificationTemplate model."""

    channel_display = serializers.CharField(
        source="get_channel_display", read_only=True
    )
    usage_count = serializers.SerializerMethodField()

    class Meta:
        model = NotificationTemplate
        fields = [
            "id", "name", "code", "channel", "channel_display",
            "subject", "body_template", "variables",
            "is_active", "category", "description",
            "usage_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_usage_count(self, obj):
        return obj.alert_rules.count()

    def validate_code(self, value):
        qs = NotificationTemplate.objects.filter(code=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A template with this code already exists."
            )
        return value


# =============================================================================
# Notification Serializer
# =============================================================================

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""

    type_display = serializers.CharField(
        source="get_type_display", read_only=True
    )
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )
    is_read = serializers.BooleanField(read_only=True)
    user_email = serializers.CharField(
        source="user.email", read_only=True, default=None
    )
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id", "organization", "user", "user_email",
            "title", "message",
            "type", "type_display",
            "category", "category_display",
            "read_at", "is_read",
            "action_url", "metadata", "priority",
            "expires_at", "time_ago",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "read_at", "created_at", "updated_at",
        ]

    def get_time_ago(self, obj):
        """Return human-readable time since notification was created."""
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        diff = now - obj.created_at

        if diff < timedelta(minutes=1):
            return "just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes}m ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h ago"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days}d ago"
        else:
            return obj.created_at.strftime("%b %d, %Y")


# =============================================================================
# Notification Preference Serializer
# =============================================================================

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model."""

    channel_display = serializers.CharField(
        source="get_channel_display", read_only=True
    )
    user_email = serializers.CharField(
        source="user.email", read_only=True
    )

    class Meta:
        model = NotificationPreference
        fields = [
            "id", "user", "user_email",
            "channel", "channel_display",
            "categories", "is_enabled",
            "quiet_hours_start", "quiet_hours_end",
            "min_priority",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        quiet_start = attrs.get("quiet_hours_start")
        quiet_end = attrs.get("quiet_hours_end")

        if (quiet_start and not quiet_end) or (quiet_end and not quiet_start):
            raise serializers.ValidationError(
                "Both quiet hours start and end must be provided together."
            )

        categories = attrs.get("categories", [])
        if categories and not isinstance(categories, list):
            raise serializers.ValidationError(
                {"categories": "Categories must be a list."}
            )

        return attrs


# =============================================================================
# Alert Rule Serializer
# =============================================================================

class AlertRuleSerializer(serializers.ModelSerializer):
    """Serializer for AlertRule model."""

    severity_display = serializers.CharField(
        source="get_severity_display", read_only=True
    )
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    template_name = serializers.CharField(
        source="template.name", read_only=True, default=None
    )
    can_trigger = serializers.BooleanField(read_only=True)

    class Meta:
        model = AlertRule
        fields = [
            "id", "name", "organization", "organization_name",
            "description", "condition",
            "severity", "severity_display",
            "recipients", "channels",
            "cooldown_minutes", "is_active",
            "last_triggered", "trigger_count",
            "template", "template_name",
            "can_trigger",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "last_triggered", "trigger_count",
            "created_at", "updated_at",
        ]

    def validate_condition(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Condition must be a JSON object.")
        if not value:
            raise serializers.ValidationError(
                "Condition cannot be empty. Define at least one trigger condition."
            )
        return value

    def validate_recipients(self, value):
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError(
                "At least one recipient must be specified."
            )
        return value

    def validate_channels(self, value):
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError(
                "At least one notification channel must be specified."
            )
        valid_channels = ["email", "sms", "in_app", "slack", "teams", "push"]
        invalid = [c for c in value if c not in valid_channels]
        if invalid:
            raise serializers.ValidationError(
                f"Invalid channels: {', '.join(invalid)}. Valid options: {', '.join(valid_channels)}"
            )
        return value
