"""
Leakage app models - LeakageDetection, LeakageRule, LeakageAlert,
LeakageResolution.
Manages revenue leakage detection, alerting, and resolution tracking.
"""

import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.users.models import BaseModel


# =============================================================================
# Leakage Detection Model
# =============================================================================

class LeakageDetection(BaseModel):
    """Detected instances of revenue leakage."""

    class DetectionType(models.TextChoices):
        UNBILLED_HOURS = "unbilled_hours", "Unbilled Hours"
        MISSED_MILESTONE = "missed_milestone", "Missed Milestone"
        RATE_ESCALATION_MISSED = "rate_escalation_missed", "Rate Escalation Missed"
        EXPENSES_NOT_BILLED = "expenses_not_billed", "Expenses Not Billed"
        SCOPE_CREEP = "scope_creep", "Scope Creep"
        UNDERCHARGING = "undercharging", "Undercharging"
        DISCOUNT_OVERUSE = "discount_overuse", "Discount Overuse"
        CONTRACT_EXPIRY_MISSED = "contract_expiry_missed", "Contract Expiry Missed"
        BILLING_DELAY = "billing_delay", "Billing Delay"

    class StatusChoices(models.TextChoices):
        OPEN = "open", "Open"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"
        FALSE_POSITIVE = "false_positive", "False Positive"
        ESCALATED = "escalated", "Escalated"

    class SeverityChoices(models.TextChoices):
        CRITICAL = "critical", "Critical"
        HIGH = "high", "High"
        MEDIUM = "medium", "Medium"
        LOW = "low", "Low"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="leakage_detections",
    )
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        related_name="leakage_detections",
    )
    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.CASCADE,
        related_name="leakage_detections",
        null=True,
        blank=True,
    )
    detection_type = models.CharField(
        max_length=30,
        choices=DetectionType.choices,
        db_index=True,
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Estimated leakage amount",
    )
    description = models.TextField()
    severity = models.CharField(
        max_length=10,
        choices=SeverityChoices.choices,
        default=SeverityChoices.MEDIUM,
    )
    detected_at = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.OPEN,
        db_index=True,
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_leakages",
    )
    resolution_notes = models.TextField(blank=True, default="")
    rule = models.ForeignKey(
        "LeakageRule",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="detections",
        help_text="Rule that triggered this detection",
    )
    evidence_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Supporting data/evidence for the detection",
    )

    class Meta:
        ordering = ["-detected_at"]
        verbose_name = "Leakage Detection"
        verbose_name_plural = "Leakage Detections"
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["client", "detection_type"]),
            models.Index(fields=["contract", "status"]),
            models.Index(fields=["severity", "status"]),
            models.Index(fields=["detected_at"]),
        ]

    def __str__(self):
        return f"{self.get_detection_type_display()} - {self.client.name} ({self.amount})"


# =============================================================================
# Leakage Rule Model
# =============================================================================

class LeakageRule(BaseModel):
    """Rules for automated leakage detection."""

    class DetectionType(models.TextChoices):
        UNBILLED_HOURS = "unbilled_hours", "Unbilled Hours"
        MISSED_MILESTONE = "missed_milestone", "Missed Milestone"
        RATE_ESCALATION_MISSED = "rate_escalation_missed", "Rate Escalation Missed"
        EXPENSES_NOT_BILLED = "expenses_not_billed", "Expenses Not Billed"
        SCOPE_CREEP = "scope_creep", "Scope Creep"
        UNDERCHARGING = "undercharging", "Undercharging"
        DISCOUNT_OVERUSE = "discount_overuse", "Discount Overuse"
        CONTRACT_EXPIRY_MISSED = "contract_expiry_missed", "Contract Expiry Missed"
        BILLING_DELAY = "billing_delay", "Billing Delay"

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
        related_name="leakage_rules",
        null=True,
        blank=True,
    )
    detection_type = models.CharField(
        max_length=30,
        choices=DetectionType.choices,
    )
    condition = models.JSONField(
        default=dict,
        help_text="Rule conditions as structured JSON",
    )
    threshold = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Minimum amount threshold for triggering",
    )
    severity = models.CharField(
        max_length=10,
        choices=SeverityChoices.choices,
        default=SeverityChoices.MEDIUM,
    )
    is_active = models.BooleanField(default=True)
    auto_alert = models.BooleanField(
        default=True,
        help_text="Automatically send alerts when triggered",
    )
    cooldown_hours = models.PositiveIntegerField(
        default=24,
        help_text="Hours to wait before re-triggering for same entity",
    )
    description = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["severity", "name"]
        verbose_name = "Leakage Rule"
        verbose_name_plural = "Leakage Rules"
        indexes = [
            models.Index(fields=["detection_type", "is_active"]),
            models.Index(fields=["severity"]),
            models.Index(fields=["organization"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_detection_type_display()})"


# =============================================================================
# Leakage Alert Model
# =============================================================================

class LeakageAlert(BaseModel):
    """Alerts generated from leakage detections."""

    class AlertType(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        IN_APP = "in_app", "In-App Notification"
        SLACK = "slack", "Slack"
        TEAMS = "teams", "Microsoft Teams"
        WEBHOOK = "webhook", "Webhook"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    detection = models.ForeignKey(
        LeakageDetection,
        on_delete=models.CASCADE,
        related_name="alerts",
    )
    alert_type = models.CharField(
        max_length=20,
        choices=AlertType.choices,
    )
    recipients = models.JSONField(
        default=list,
        help_text="List of recipient identifiers (emails, user IDs, etc.)",
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acknowledged_leakage_alerts",
    )
    message = models.TextField(blank=True, default="")
    delivery_status = models.CharField(
        max_length=20,
        default="pending",
        help_text="Delivery status from notification provider",
    )

    class Meta:
        ordering = ["-sent_at"]
        verbose_name = "Leakage Alert"
        verbose_name_plural = "Leakage Alerts"
        indexes = [
            models.Index(fields=["detection"]),
            models.Index(fields=["alert_type"]),
            models.Index(fields=["sent_at"]),
        ]

    def __str__(self):
        return f"Alert for {self.detection} via {self.get_alert_type_display()}"


# =============================================================================
# Leakage Resolution Model
# =============================================================================

class LeakageResolution(BaseModel):
    """Resolution tracking for detected leakages."""

    class ActionChoices(models.TextChoices):
        INVOICE_GENERATED = "invoice_generated", "Invoice Generated"
        RATE_CORRECTED = "rate_corrected", "Rate Corrected"
        CONTRACT_AMENDED = "contract_amended", "Contract Amended"
        CREDIT_NOTE = "credit_note", "Credit Note Issued"
        WRITE_OFF = "write_off", "Written Off"
        NO_ACTION = "no_action", "No Action Required"
        PROCESS_IMPROVEMENT = "process_improvement", "Process Improvement"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    detection = models.OneToOneField(
        LeakageDetection,
        on_delete=models.CASCADE,
        related_name="resolution",
    )
    action_taken = models.CharField(
        max_length=30,
        choices=ActionChoices.choices,
    )
    description = models.TextField(blank=True, default="")
    amount_recovered = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    recovery_date = models.DateField(null=True, blank=True)
    invoice_generated = models.ForeignKey(
        "invoices.Invoice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leakage_resolutions",
        help_text="Invoice generated to recover leaked amount",
    )
    preventive_measures = models.TextField(
        blank=True,
        default="",
        help_text="Steps taken to prevent recurrence",
    )

    class Meta:
        ordering = ["-recovery_date"]
        verbose_name = "Leakage Resolution"
        verbose_name_plural = "Leakage Resolutions"
        indexes = [
            models.Index(fields=["action_taken"]),
            models.Index(fields=["recovery_date"]),
        ]

    def __str__(self):
        return f"Resolution for {self.detection} - {self.get_action_taken_display()}"

    @property
    def recovery_percentage(self):
        if self.detection.amount > 0:
            return (self.amount_recovered / self.detection.amount) * 100
        return 0
