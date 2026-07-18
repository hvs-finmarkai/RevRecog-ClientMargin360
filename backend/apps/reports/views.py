"""
Reports app views - ReportViewSet with actions: generate, export; DashboardViewSet.
"""

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Dashboard, DashboardWidget, ReportExport, ReportSchedule, ReportTemplate
from .serializers import (
    DashboardSerializer,
    DashboardWidgetSerializer,
    ReportExportSerializer,
    ReportScheduleSerializer,
    ReportTemplateSerializer,
)


class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing report templates with generate and export actions.
    """

    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["report_type", "format", "is_active", "is_system"]
    search_fields = ["name", "description"]
    ordering_fields = ["report_type", "name", "created_at"]
    ordering = ["report_type", "name"]

    def get_queryset(self):
        return ReportTemplate.objects.filter(
            organization=self.request.user.organization,
            is_deleted=False,
        )

    def get_serializer_class(self):
        if self.action == "export":
            return ReportExportSerializer
        if self.action == "schedules":
            return ReportScheduleSerializer
        return ReportTemplateSerializer

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        if instance.is_system:
            return Response(
                {"detail": "System reports cannot be deleted."},
                status=status.HTTP_403_FORBIDDEN,
            )
        instance.soft_delete()

    @action(detail=True, methods=["post"])
    def generate(self, request, pk=None):
        """Generate a report from template with given parameters."""
        template = self.get_object()
        parameters = request.data.get("parameters", {})
        output_format = request.data.get("format", template.format)

        # Create export record
        export = ReportExport.objects.create(
            template=template,
            format=output_format,
            generated_by=request.user,
            parameters=parameters,
            status=ReportExport.StatusChoices.GENERATING,
            created_by=request.user,
        )

        # In production, this triggers async report generation
        return Response({
            "detail": "Report generation initiated.",
            "export_id": str(export.id),
            "template_name": template.name,
            "format": output_format,
            "status": "generating",
        }, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=["get"])
    def export(self, request, pk=None):
        """List all exports for this report template."""
        template = self.get_object()
        exports = ReportExport.objects.filter(
            template=template, is_deleted=False
        ).order_by("-generated_at")[:20]
        serializer = ReportExportSerializer(exports, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get", "post"])
    def schedules(self, request, pk=None):
        """List or create schedules for a report template."""
        template = self.get_object()

        if request.method == "GET":
            schedules = ReportSchedule.objects.filter(
                template=template, is_deleted=False
            )
            serializer = ReportScheduleSerializer(schedules, many=True)
            return Response(serializer.data)

        serializer = ReportScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(template=template, created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DashboardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing dashboards and their widgets.
    """

    serializer_class = DashboardSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["is_default", "is_shared", "owner"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at", "is_default"]
    ordering = ["-is_default", "name"]

    def get_queryset(self):
        user = self.request.user
        return Dashboard.objects.filter(
            organization=user.organization,
            is_deleted=False,
        ).filter(
            owner=user,
        ) | Dashboard.objects.filter(
            organization=user.organization,
            is_deleted=False,
            is_shared=True,
        )

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            owner=self.request.user,
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=["get"])
    def widgets(self, request, pk=None):
        """List all widgets for this dashboard."""
        dashboard = self.get_object()
        widgets = DashboardWidget.objects.filter(
            dashboard=dashboard, is_deleted=False
        ).order_by("position_y", "position_x")
        serializer = DashboardWidgetSerializer(widgets, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_widget(self, request, pk=None):
        """Add a widget to this dashboard."""
        dashboard = self.get_object()
        serializer = DashboardWidgetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(dashboard=dashboard, created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        """Set this dashboard as the default for the organization."""
        dashboard = self.get_object()

        # Unset all other defaults
        Dashboard.objects.filter(
            organization=request.user.organization,
            is_default=True,
        ).update(is_default=False)

        dashboard.is_default = True
        dashboard.save(update_fields=["is_default", "updated_at"])

        return Response({"detail": "Dashboard set as default."})
