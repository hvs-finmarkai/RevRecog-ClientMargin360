"""
Analytics app models - AnalyticsEvent, MetricSnapshot.
Manages event tracking, metric aggregation, and analytics data.
"""

import uuid

from django.conf import settings
from django.db import models

from apps.users.models import BaseModel


# =============================================================================
# Analytics Event Model
# =============================================================================

class AnalyticsEvent(models.Model):
    """Event tracking for analytics and behavioral analysis."""

    class EventCategory(models.TextChoices):
        USER_ACTION = "user_action", "User Action"
        SYSTEM_EVENT = "system_event", "System Event"
        BUSINESS_EVENT = "business_event", "Business Event"
        INTEGRATION = "integration", "Integration Event"
        ERROR = "error", "Error Event"
        PERFORMANCE = "performance", "Performance Event"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="analytics_events",
    )
    event_type = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Specific event type (e.g., invoice.created, contract.approved)",
    )
    event_category = models.CharField(
        max_length=20,
        choices=EventCategory.choices,
        default=EventCategory.BUSINESS_EVENT,
    )
    entity_type = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Type of entity involved (e.g., invoice, contract, client)",
    )
    entity_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="ID of the entity involved",
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Event payload data",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analytics_events",
    )
    session_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="User session identifier",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")
    source = models.CharField(
        max_length=50,
        default="web",
        help_text="Event source (web, api, system, integration)",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Analytics Event"
        verbose_name_plural = "Analytics Events"
        indexes = [
            models.Index(fields=["organization", "event_type"]),
            models.Index(fields=["event_type", "created_at"]),
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["event_category"]),
        ]

    def __str__(self):
        return f"{self.event_type} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


# =============================================================================
# Metric Snapshot Model
# =============================================================================

class MetricSnapshot(BaseModel):
    """Aggregated metric snapshots for time-series analysis."""

    class PeriodType(models.TextChoices):
        HOURLY = "hourly", "Hourly"
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        YEARLY = "yearly", "Yearly"

    class MetricCategory(models.TextChoices):
        REVENUE = "revenue", "Revenue"
        COLLECTIONS = "collections", "Collections"
        PROFITABILITY = "profitability", "Profitability"
        LEAKAGE = "leakage", "Leakage"
        CLIENTS = "clients", "Clients"
        CONTRACTS = "contracts", "Contracts"
        OPERATIONS = "operations", "Operations"
        AI = "ai", "AI Performance"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="metric_snapshots",
    )
    metric_name = models.CharField(
        max_length=200,
        db_index=True,
        help_text="Metric identifier (e.g., total_revenue, avg_margin_pct)",
    )
    metric_value = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        help_text="Numeric metric value",
    )
    metric_category = models.CharField(
        max_length=20,
        choices=MetricCategory.choices,
        default=MetricCategory.REVENUE,
    )
    period_type = models.CharField(
        max_length=10,
        choices=PeriodType.choices,
        default=PeriodType.DAILY,
    )
    period_start = models.DateTimeField(db_index=True)
    period_end = models.DateTimeField(null=True, blank=True)
    dimensions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Dimension slices (e.g., by client, by segment, by billing_model)",
    )
    previous_value = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Previous period value for trend calculation",
    )
    change_pct = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentage change from previous period",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata about the metric calculation",
    )

    class Meta:
        ordering = ["-period_start"]
        verbose_name = "Metric Snapshot"
        verbose_name_plural = "Metric Snapshots"
        unique_together = ["organization", "metric_name", "period_type", "period_start"]
        indexes = [
            models.Index(fields=["organization", "metric_name", "period_start"]),
            models.Index(fields=["metric_name", "period_type"]),
            models.Index(fields=["period_start"]),
            models.Index(fields=["metric_category"]),
        ]

    def __str__(self):
        return f"{self.metric_name} = {self.metric_value} ({self.period_start.strftime('%Y-%m-%d')})"

    @property
    def trend_direction(self):
        """Determine trend direction based on change percentage."""
        if self.change_pct is None:
            return "stable"
        if self.change_pct > 2:
            return "up"
        elif self.change_pct < -2:
            return "down"
        return "stable"
