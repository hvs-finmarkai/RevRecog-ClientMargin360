"""
Reports app models - ReportTemplate, ReportSchedule, ReportExport,
Dashboard, DashboardWidget.
Manages report generation, scheduling, and dashboard configuration.
"""

import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.users.models import BaseModel


# =============================================================================
# Report Template Model
# =============================================================================

class ReportTemplate(BaseModel):
    """Templates defining report structure and data queries."""

    class ReportType(models.TextChoices):
        REVENUE = "revenue", "Revenue Report"
        PROFITABILITY = "profitability", "Profitability Report"
        AGING = "aging", "Aging Report"
        LEAKAGE = "leakage", "Leakage Report"
        CLIENT_HEALTH = "client_health", "Client Health Report"
        COLLECTION = "collection", "Collection Report"
        CONTRACT = "contract", "Contract Report"
        BILLING = "billing", "Billing Report"
        COMPLIANCE = "compliance", "Compliance Report"
        CUSTOM = "custom", "Custom Report"

    class FormatChoices(models.TextChoices):
        PDF = "pdf", "PDF"
        EXCEL = "excel", "Excel"
        CSV = "csv", "CSV"
        HTML = "html", "HTML"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="report_templates",
    )
    report_type = models.CharField(
        max_length=20,
        choices=ReportType.choices,
        db_index=True,
    )
    description = models.TextField(blank=True, default="")
    query_config = models.JSONField(
        default=dict,
        help_text="Data query configuration (models, filters, aggregations)",
    )
    columns = models.JSONField(
        default=list,
        help_text="Column definitions (name, field, width, format)",
    )
    filters = models.JSONField(
        default=list,
        blank=True,
        help_text="Available filter parameters",
    )
    format = models.CharField(
        max_length=10,
        choices=FormatChoices.choices,
        default=FormatChoices.PDF,
    )
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(
        default=False,
        help_text="System templates cannot be deleted",
    )
    sort_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Default sort configuration",
    )
    grouping = models.JSONField(
        default=list,
        blank=True,
        help_text="Grouping/subtotal configuration",
    )
    chart_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Chart/visualization configuration if applicable",
    )

    class Meta:
        ordering = ["report_type", "name"]
        verbose_name = "Report Template"
        verbose_name_plural = "Report Templates"
        indexes = [
            models.Index(fields=["organization", "report_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"


# =============================================================================
# Report Schedule Model
# =============================================================================

class ReportSchedule(BaseModel):
    """Scheduled report generation and distribution."""

    class FrequencyChoices(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        BI_WEEKLY = "bi_weekly", "Bi-Weekly"
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        ANNUAL = "annual", "Annual"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    frequency = models.CharField(
        max_length=15,
        choices=FrequencyChoices.choices,
        default=FrequencyChoices.MONTHLY,
    )
    next_run = models.DateTimeField(db_index=True)
    last_run = models.DateTimeField(null=True, blank=True)
    recipients = models.JSONField(
        default=list,
        help_text="List of email addresses or user IDs to send report to",
    )
    is_active = models.BooleanField(default=True)
    parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Report parameters/filters for scheduled run",
    )
    run_count = models.PositiveIntegerField(default=0)
    last_status = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "Pending"),
            ("success", "Success"),
            ("failed", "Failed"),
        ],
    )
    failure_message = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["next_run"]
        verbose_name = "Report Schedule"
        verbose_name_plural = "Report Schedules"
        indexes = [
            models.Index(fields=["template", "is_active"]),
            models.Index(fields=["next_run"]),
            models.Index(fields=["frequency"]),
        ]

    def __str__(self):
        return f"{self.template.name} - {self.get_frequency_display()} (Next: {self.next_run})"


# =============================================================================
# Report Export Model
# =============================================================================

class ReportExport(BaseModel):
    """Generated report files and their metadata."""

    class StatusChoices(models.TextChoices):
        GENERATING = "generating", "Generating"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name="exports",
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    file_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
    )
    format = models.CharField(max_length=10, default="pdf")
    size_bytes = models.PositiveIntegerField(default=0)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_reports",
    )
    parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Parameters used to generate this report",
    )
    row_count = models.PositiveIntegerField(default=0)
    generation_time_ms = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.GENERATING,
    )
    error_message = models.TextField(blank=True, default="")
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the file will be automatically deleted",
    )

    class Meta:
        ordering = ["-generated_at"]
        verbose_name = "Report Export"
        verbose_name_plural = "Report Exports"
        indexes = [
            models.Index(fields=["template", "generated_at"]),
            models.Index(fields=["generated_by"]),
            models.Index(fields=["status"]),
            models.Index(fields=["generated_at"]),
        ]

    def __str__(self):
        return f"{self.template.name} - {self.generated_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def size_display(self):
        """Human-readable file size."""
        if self.size_bytes < 1024:
            return f"{self.size_bytes} B"
        elif self.size_bytes < 1024 * 1024:
            return f"{self.size_bytes / 1024:.1f} KB"
        else:
            return f"{self.size_bytes / (1024 * 1024):.1f} MB"


# =============================================================================
# Dashboard Model
# =============================================================================

class Dashboard(BaseModel):
    """Custom dashboards with configurable widget layouts."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="dashboards",
    )
    description = models.TextField(blank=True, default="")
    layout = models.JSONField(
        default=dict,
        blank=True,
        help_text="Dashboard layout configuration",
    )
    is_default = models.BooleanField(default=False)
    is_shared = models.BooleanField(
        default=False,
        help_text="Whether this dashboard is visible to all org users",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_dashboards",
    )
    refresh_interval = models.PositiveIntegerField(
        default=300,
        help_text="Auto-refresh interval in seconds (0 = no auto-refresh)",
    )

    class Meta:
        ordering = ["-is_default", "name"]
        verbose_name = "Dashboard"
        verbose_name_plural = "Dashboards"
        indexes = [
            models.Index(fields=["organization", "is_default"]),
            models.Index(fields=["owner"]),
        ]

    def __str__(self):
        return f"{self.name} ({'Default' if self.is_default else 'Custom'})"


# =============================================================================
# Dashboard Widget Model
# =============================================================================

class DashboardWidget(BaseModel):
    """Individual widgets within a dashboard."""

    class WidgetType(models.TextChoices):
        KPI_CARD = "kpi_card", "KPI Card"
        LINE_CHART = "line_chart", "Line Chart"
        BAR_CHART = "bar_chart", "Bar Chart"
        PIE_CHART = "pie_chart", "Pie Chart"
        TABLE = "table", "Table"
        HEATMAP = "heatmap", "Heatmap"
        GAUGE = "gauge", "Gauge"
        TREND = "trend", "Trend Indicator"
        LIST = "list", "List"
        MAP = "map", "Map"
        CUSTOM = "custom", "Custom Component"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name="widgets",
    )
    widget_type = models.CharField(
        max_length=15,
        choices=WidgetType.choices,
    )
    title = models.CharField(max_length=200)
    config = models.JSONField(
        default=dict,
        help_text="Widget-specific configuration (data source, formatting, etc.)",
    )
    position_x = models.PositiveIntegerField(
        default=0,
        help_text="Grid X position",
    )
    position_y = models.PositiveIntegerField(
        default=0,
        help_text="Grid Y position",
    )
    width = models.PositiveIntegerField(
        default=4,
        validators=[MinValueValidator(1)],
        help_text="Widget width in grid units",
    )
    height = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1)],
        help_text="Widget height in grid units",
    )
    refresh_interval = models.PositiveIntegerField(
        default=0,
        help_text="Widget-specific refresh interval (0 = use dashboard default)",
    )
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["position_y", "position_x"]
        verbose_name = "Dashboard Widget"
        verbose_name_plural = "Dashboard Widgets"
        indexes = [
            models.Index(fields=["dashboard", "widget_type"]),
            models.Index(fields=["position_x", "position_y"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_widget_type_display()}) on {self.dashboard.name}"
