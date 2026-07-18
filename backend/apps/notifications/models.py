"""
Notifications app models - Notification, NotificationTemplate,
NotificationPreference, AlertRule.
Manages notifications, templates, user preferences, and alert rules.
"""

import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.users.models import BaseModel


# =============================================================================
# Notification Template Model
# =============================================================================

class NotificationTemplate(BaseModel):
    """Templates for generating notifications across channels."""

    class ChannelChoices(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        IN_APP = "in_app", "In-App"
        SLACK = "slack", "Slack"
        TEAMS = "teams", "Microsoft Teams"
        WEBHOOK = "webhook", "Webhook"
        PUSH = "push", "Push Notification"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique code for programmatic reference",
    )
    channel = models.CharField(
        max_length=10,
        choices=ChannelChoices.choices,
    )
    subject = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="Subject line (for email) or title",
    )
    body_template = models.TextField(
        help_text="Template body with Jinja2/Django template syntax",
    )
    variables = models.JSONField(
        default=list,
        blank=True,
        help_text="List of available template variables",
    )
    is_active = models.BooleanField(default=True)
    category = models.CharField(
        max_length=50,
        blank=True,
        default="general",
        help_text="Notification category for preference matching",
    )
    description = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["name"]
        verbose_name = "Notification Template"
        verbose_name_plural = "Notification Templates"
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["channel", "is_active"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_channel_display()})"


# =============================================================================
# Notification Model
# =============================================================================

class Notification(BaseModel):
    """Individual notification instances sent to users."""

    class TypeChoices(models.TextChoices):
        ALERT = "alert", "Alert"
        INFO = "info", "Information"
        WARNING = "warning", "Warning"
        SUCCESS = "success", "Success"
        ERROR = "error", "Error"

    class CategoryChoices(models.TextChoices):
        INVOICE = "invoice", "Invoice"
        PAYMENT = "payment", "Payment"
        CONTRACT = "contract", "Contract"
        LEAKAGE = "leakage", "Revenue Leakage"
        COLLECTION = "collection", "Collections"
        AI_INSIGHT = "ai_insight", "AI Insight"
        SYSTEM = "system", "System"
        APPROVAL = "approval", "Approval Required"
        ESCALATION = "escalation", "Escalation"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        help_text="Null means broadcast to all org users",
    )
    title = models.CharField(max_length=300)
    message = models.TextField()
    type = models.CharField(
        max_length=10,
        choices=TypeChoices.choices,
        default=TypeChoices.INFO,
    )
    category = models.CharField(
        max_length=15,
        choices=CategoryChoices.choices,
        default=CategoryChoices.SYSTEM,
        db_index=True,
    )
    read_at = models.DateTimeField(null=True, blank=True)
    action_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        help_text="URL to navigate to when notification is clicked",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional contextual data",
    )
    priority = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="1 = highest priority, 10 = lowest",
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Notification expires after this datetime",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        indexes = [
            models.Index(fields=["user", "read_at"]),
            models.Index(fields=["organization", "category"]),
            models.Index(fields=["type"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["priority"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"

    @property
    def is_read(self):
        return self.read_at is not None

    def mark_as_read(self):
        from django.utils import timezone
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=["read_at", "updated_at"])


# =============================================================================
# Notification Preference Model
# =============================================================================

class NotificationPreference(BaseModel):
    """User-specific notification preferences."""

    class ChannelChoices(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        IN_APP = "in_app", "In-App"
        SLACK = "slack", "Slack"
        TEAMS = "teams", "Microsoft Teams"
        PUSH = "push", "Push Notification"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )
    channel = models.CharField(
        max_length=10,
        choices=ChannelChoices.choices,
    )
    categories = models.JSONField(
        default=list,
        blank=True,
        help_text="List of categories enabled for this channel",
    )
    is_enabled = models.BooleanField(default=True)
    quiet_hours_start = models.TimeField(
        null=True,
        blank=True,
        help_text="Start of quiet hours (no notifications sent)",
    )
    quiet_hours_end = models.TimeField(
        null=True,
        blank=True,
        help_text="End of quiet hours",
    )
    min_priority = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Only deliver notifications with priority <= this value",
    )

    class Meta:
        ordering = ["user", "channel"]
        verbose_name = "Notification Preference"
        verbose_name_plural = "Notification Preferences"
        unique_together = ["user", "channel"]
        indexes = [
            models.Index(fields=["user", "channel"]),
            models.Index(fields=["is_enabled"]),
        ]

    def __str__(self):
        status = "enabled" if self.is_enabled else "disabled"
        return f"{self.user.email} - {self.get_channel_display()} ({status})"


# =============================================================================
# Alert Rule Model
# =============================================================================

class AlertRule(BaseModel):
    """Configurable alert rules that trigger notifications based on conditions."""

    class SeverityChoices(models.TextChoices):
        CRITICAL = "critical", "Critical"
        HIGH = "high", "High"
        MEDIUM = "medium", "Medium"
        LOW = "low", "Low"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="alert_rules",
    )
    description = models.TextField(blank=True, default="")
    condition = models.JSONField(
        default=dict,
        help_text="Rule conditions as structured JSON (event_type, thresholds, etc.)",
    )
    severity = models.CharField(
        max_length=10,
        choices=SeverityChoices.choices,
        default=SeverityChoices.MEDIUM,
    )
    recipients = models.JSONField(
        default=list,
        help_text="List of user IDs or roles to notify",
    )
    channels = models.JSONField(
        default=list,
        help_text="List of notification channels to use",
    )
    cooldown_minutes = models.PositiveIntegerField(
        default=60,
        help_text="Minimum minutes between repeated alerts",
    )
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    trigger_count = models.PositiveIntegerField(default=0)
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alert_rules",
    )

    class Meta:
        ordering = ["severity", "name"]
        verbose_name = "Alert Rule"
        verbose_name_plural = "Alert Rules"
        indexes = [
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["severity"]),
            models.Index(fields=["last_triggered"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_severity_display()})"

    @property
    def can_trigger(self):
        """Check if cooldown period has passed since last trigger."""
        if not self.last_triggered:
            return True
        from django.utils import timezone
        from datetime import timedelta
        elapsed = timezone.now() - self.last_triggered
        return elapsed >= timedelta(minutes=self.cooldown_minutes)
