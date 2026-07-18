"""
Reports app serializers - ReportTemplateSerializer, ReportScheduleSerializer,
ReportExportSerializer, DashboardSerializer, DashboardWidgetSerializer.
"""

from rest_framework import serializers

from .models import Dashboard, DashboardWidget, ReportExport, ReportSchedule, ReportTemplate


# =============================================================================
# Dashboard Widget Serializer
# =============================================================================

class DashboardWidgetSerializer(serializers.ModelSerializer):
    """Serializer for DashboardWidget model."""

    widget_type_display = serializers.CharField(
        source="get_widget_type_display", read_only=True
    )

    class Meta:
        model = DashboardWidget
        fields = [
            "id", "dashboard", "widget_type", "widget_type_display",
            "title", "config",
            "position_x", "position_y", "width", "height",
            "refresh_interval", "is_visible",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        width = attrs.get("width", 4)
        height = attrs.get("height", 3)

        if width < 1 or width > 12:
            raise serializers.ValidationError(
                {"width": "Width must be between 1 and 12 grid units."}
            )
        if height < 1 or height > 12:
            raise serializers.ValidationError(
                {"height": "Height must be between 1 and 12 grid units."}
            )
        return attrs


# =============================================================================
# Dashboard Serializer
# =============================================================================

class DashboardSerializer(serializers.ModelSerializer):
    """Serializer for Dashboard model with nested widgets."""

    widgets = DashboardWidgetSerializer(many=True, required=False)
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    owner_name = serializers.SerializerMethodField()
    widget_count = serializers.SerializerMethodField()

    class Meta:
        model = Dashboard
        fields = [
            "id", "name", "organization", "organization_name",
            "description", "layout",
            "is_default", "is_shared",
            "owner", "owner_name",
            "refresh_interval", "widget_count",
            "widgets",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_owner_name(self, obj):
        if obj.owner:
            return obj.owner.get_full_name()
        return None

    def get_widget_count(self, obj):
        return obj.widgets.filter(is_visible=True).count()

    def create(self, validated_data):
        widgets_data = validated_data.pop("widgets", [])
        dashboard = Dashboard.objects.create(**validated_data)

        for widget_data in widgets_data:
            widget_data.pop("dashboard", None)
            DashboardWidget.objects.create(dashboard=dashboard, **widget_data)

        return dashboard

    def update(self, instance, validated_data):
        widgets_data = validated_data.pop("widgets", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if widgets_data is not None:
            instance.widgets.all().delete()
            for widget_data in widgets_data:
                widget_data.pop("dashboard", None)
                DashboardWidget.objects.create(dashboard=instance, **widget_data)

        return instance


# =============================================================================
# Report Template Serializer
# =============================================================================

class ReportTemplateSerializer(serializers.ModelSerializer):
    """Serializer for ReportTemplate model."""

    report_type_display = serializers.CharField(
        source="get_report_type_display", read_only=True
    )
    format_display = serializers.CharField(
        source="get_format_display", read_only=True
    )
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    schedule_count = serializers.SerializerMethodField()

    class Meta:
        model = ReportTemplate
        fields = [
            "id", "name", "organization", "organization_name",
            "report_type", "report_type_display",
            "description", "query_config", "columns",
            "filters", "format", "format_display",
            "is_active", "is_system",
            "sort_config", "grouping", "chart_config",
            "schedule_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "is_system", "created_at", "updated_at"]

    def get_schedule_count(self, obj):
        return obj.schedules.filter(is_active=True).count()

    def validate_columns(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Columns must be a list.")
        return value


# =============================================================================
# Report Schedule Serializer
# =============================================================================

class ReportScheduleSerializer(serializers.ModelSerializer):
    """Serializer for ReportSchedule model."""

    template_name = serializers.CharField(
        source="template.name", read_only=True
    )
    frequency_display = serializers.CharField(
        source="get_frequency_display", read_only=True
    )

    class Meta:
        model = ReportSchedule
        fields = [
            "id", "template", "template_name",
            "frequency", "frequency_display",
            "next_run", "last_run", "recipients",
            "is_active", "parameters",
            "run_count", "last_status", "failure_message",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "last_run", "run_count", "last_status",
            "failure_message", "created_at", "updated_at",
        ]

    def validate_recipients(self, value):
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError(
                "At least one recipient must be specified."
            )
        return value


# =============================================================================
# Report Export Serializer
# =============================================================================

class ReportExportSerializer(serializers.ModelSerializer):
    """Serializer for ReportExport model."""

    template_name = serializers.CharField(
        source="template.name", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    generated_by_name = serializers.SerializerMethodField()
    size_display = serializers.CharField(read_only=True)

    class Meta:
        model = ReportExport
        fields = [
            "id", "template", "template_name",
            "generated_at", "file_url", "format",
            "size_bytes", "size_display",
            "generated_by", "generated_by_name",
            "parameters", "row_count", "generation_time_ms",
            "status", "status_display",
            "error_message", "expires_at",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "generated_at", "file_url", "size_bytes",
            "row_count", "generation_time_ms",
            "status", "error_message",
            "created_at", "updated_at",
        ]

    def get_generated_by_name(self, obj):
        if obj.generated_by:
            return obj.generated_by.get_full_name()
        return None
