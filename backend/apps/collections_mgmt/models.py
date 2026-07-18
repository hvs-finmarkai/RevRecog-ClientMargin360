"""
Collections Management app models - Receivable, PaymentReceipt,
CollectionSchedule, AgingBucket, DunningRule, CashForecast.
Manages accounts receivable, payment tracking, aging analysis, and cash forecasting.
"""

import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.users.models import BaseModel


# =============================================================================
# Receivable Model
# =============================================================================

class Receivable(BaseModel):
    """Accounts receivable tracking per invoice."""

    class StatusChoices(models.TextChoices):
        CURRENT = "current", "Current"
        OVERDUE_30 = "overdue_30", "Overdue 1-30 Days"
        OVERDUE_60 = "overdue_60", "Overdue 31-60 Days"
        OVERDUE_90 = "overdue_90", "Overdue 61-90 Days"
        OVERDUE_90_PLUS = "overdue_90_plus", "Overdue 90+ Days"
        COLLECTED = "collected", "Collected"
        WRITTEN_OFF = "written_off", "Written Off"
        DISPUTED = "disputed", "Disputed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.OneToOneField(
        "invoices.Invoice",
        on_delete=models.CASCADE,
        related_name="receivable",
    )
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        related_name="receivables",
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Outstanding receivable amount",
    )
    amount_collected = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    due_date = models.DateField(db_index=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.CURRENT,
        db_index=True,
    )
    aging_days = models.IntegerField(
        default=0,
        help_text="Number of days past due date",
    )
    last_reminder_date = models.DateField(null=True, blank=True)
    next_action_date = models.DateField(null=True, blank=True)
    reminder_count = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, default="")
    dispute_reason = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-due_date"]
        verbose_name = "Receivable"
        verbose_name_plural = "Receivables"
        indexes = [
            models.Index(fields=["client", "status"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["status"]),
            models.Index(fields=["aging_days"]),
            models.Index(fields=["next_action_date"]),
        ]

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.client.name} ({self.amount})"

    @property
    def balance(self):
        return self.amount - self.amount_collected

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now().date() and self.status != self.StatusChoices.COLLECTED


# =============================================================================
# Payment Receipt Model
# =============================================================================

class PaymentReceipt(BaseModel):
    """Payment receipts recorded against receivables."""

    class PaymentMode(models.TextChoices):
        NEFT = "neft", "NEFT"
        RTGS = "rtgs", "RTGS"
        IMPS = "imps", "IMPS"
        UPI = "upi", "UPI"
        CHEQUE = "cheque", "Cheque"
        CASH = "cash", "Cash"
        WIRE = "wire", "Wire Transfer"
        CARD = "card", "Credit/Debit Card"
        DD = "dd", "Demand Draft"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    receivable = models.ForeignKey(
        Receivable,
        on_delete=models.CASCADE,
        related_name="payment_receipts",
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    payment_date = models.DateField(db_index=True)
    payment_mode = models.CharField(
        max_length=10,
        choices=PaymentMode.choices,
        default=PaymentMode.NEFT,
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Payment reference/transaction number",
    )
    bank_reference = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Bank statement reference",
    )
    reconciled = models.BooleanField(default=False)
    reconciled_at = models.DateTimeField(null=True, blank=True)
    reconciled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reconciled_payments",
    )
    tds_deducted = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-payment_date"]
        verbose_name = "Payment Receipt"
        verbose_name_plural = "Payment Receipts"
        indexes = [
            models.Index(fields=["receivable"]),
            models.Index(fields=["payment_date"]),
            models.Index(fields=["reconciled"]),
            models.Index(fields=["reference_number"]),
        ]

    def __str__(self):
        return f"Payment {self.reference_number} - {self.amount} ({self.payment_date})"


# =============================================================================
# Collection Schedule Model
# =============================================================================

class CollectionSchedule(BaseModel):
    """Follow-up schedules for collections activities."""

    class FrequencyChoices(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        BI_WEEKLY = "bi_weekly", "Bi-Weekly"
        MONTHLY = "monthly", "Monthly"
        AS_NEEDED = "as_needed", "As Needed"

    class EscalationLevel(models.IntegerChoices):
        LEVEL_1 = 1, "Level 1 - Standard"
        LEVEL_2 = 2, "Level 2 - Escalated"
        LEVEL_3 = 3, "Level 3 - Management"
        LEVEL_4 = 4, "Level 4 - Legal"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        related_name="collection_schedules",
    )
    frequency = models.CharField(
        max_length=20,
        choices=FrequencyChoices.choices,
        default=FrequencyChoices.WEEKLY,
    )
    next_followup_date = models.DateField(db_index=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_collections",
    )
    escalation_level = models.IntegerField(
        choices=EscalationLevel.choices,
        default=EscalationLevel.LEVEL_1,
    )
    notes = models.TextField(blank=True, default="")
    total_outstanding = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    last_contact_date = models.DateField(null=True, blank=True)
    last_contact_outcome = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["next_followup_date"]
        verbose_name = "Collection Schedule"
        verbose_name_plural = "Collection Schedules"
        indexes = [
            models.Index(fields=["client"]),
            models.Index(fields=["next_followup_date"]),
            models.Index(fields=["assigned_to"]),
            models.Index(fields=["escalation_level"]),
        ]

    def __str__(self):
        return f"{self.client.name} - Next: {self.next_followup_date}"


# =============================================================================
# Aging Bucket Model
# =============================================================================

class AgingBucket(BaseModel):
    """Aging analysis snapshots for the organization."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="aging_buckets",
    )
    as_of_date = models.DateField(db_index=True)
    current_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Amount not yet due",
    )
    days_30 = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Amount overdue 1-30 days",
    )
    days_60 = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Amount overdue 31-60 days",
    )
    days_90 = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Amount overdue 61-90 days",
    )
    days_90_plus = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Amount overdue 90+ days",
    )
    total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total outstanding",
    )
    client_count = models.PositiveIntegerField(default=0)
    invoice_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-as_of_date"]
        verbose_name = "Aging Bucket"
        verbose_name_plural = "Aging Buckets"
        unique_together = ["organization", "as_of_date"]
        indexes = [
            models.Index(fields=["organization", "as_of_date"]),
        ]

    def __str__(self):
        return f"Aging as of {self.as_of_date} (Total: {self.total})"

    def save(self, *args, **kwargs):
        self.total = (
            self.current_amount
            + self.days_30
            + self.days_60
            + self.days_90
            + self.days_90_plus
        )
        super().save(*args, **kwargs)


# =============================================================================
# Dunning Rule Model
# =============================================================================

class DunningRule(BaseModel):
    """Rules for automated dunning/collection actions."""

    class ActionChoices(models.TextChoices):
        EMAIL = "email", "Send Email"
        SMS = "sms", "Send SMS"
        CALL = "call", "Schedule Call"
        ESCALATE = "escalate", "Escalate"
        LETTER = "letter", "Send Letter"
        SUSPEND = "suspend", "Suspend Services"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="dunning_rules",
        null=True,
        blank=True,
    )
    days_overdue = models.PositiveIntegerField(
        help_text="Number of days overdue to trigger this rule",
    )
    action = models.CharField(
        max_length=20,
        choices=ActionChoices.choices,
    )
    template = models.ForeignKey(
        "notifications.NotificationTemplate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dunning_rules",
    )
    auto_execute = models.BooleanField(
        default=False,
        help_text="Automatically execute action without manual approval",
    )
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(
        default=100,
        help_text="Lower = higher priority",
    )
    description = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["days_overdue", "priority"]
        verbose_name = "Dunning Rule"
        verbose_name_plural = "Dunning Rules"
        indexes = [
            models.Index(fields=["days_overdue", "is_active"]),
            models.Index(fields=["action"]),
            models.Index(fields=["organization"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.days_overdue} days ({self.get_action_display()})"


# =============================================================================
# Cash Forecast Model
# =============================================================================

class CashForecast(BaseModel):
    """Cash flow forecasts based on receivables and collection patterns."""

    class MethodologyChoices(models.TextChoices):
        HISTORICAL = "historical", "Historical Pattern"
        AI_PREDICTED = "ai_predicted", "AI Predicted"
        WEIGHTED_AVERAGE = "weighted_average", "Weighted Average"
        MANUAL = "manual", "Manual Estimate"
        CONTRACTUAL = "contractual", "Contractual Schedule"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="cash_forecasts",
    )
    forecast_date = models.DateField(
        db_index=True,
        help_text="Date when forecast was generated",
    )
    period_start = models.DateField()
    period_end = models.DateField()
    expected_collections = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    actual_collections = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Actual collections (populated after period ends)",
    )
    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Confidence level as percentage",
    )
    methodology = models.CharField(
        max_length=20,
        choices=MethodologyChoices.choices,
        default=MethodologyChoices.HISTORICAL,
    )
    breakdown = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detailed breakdown by client/invoice",
    )
    variance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Difference between expected and actual (post-period)",
    )

    class Meta:
        ordering = ["-forecast_date", "period_start"]
        verbose_name = "Cash Forecast"
        verbose_name_plural = "Cash Forecasts"
        indexes = [
            models.Index(fields=["organization", "forecast_date"]),
            models.Index(fields=["period_start", "period_end"]),
            models.Index(fields=["methodology"]),
        ]

    def __str__(self):
        return f"Forecast {self.period_start} to {self.period_end} ({self.expected_collections})"

    @property
    def accuracy(self):
        """Calculate forecast accuracy after actual data is available."""
        if self.actual_collections and self.expected_collections:
            return (1 - abs(self.actual_collections - self.expected_collections) / self.expected_collections) * 100
        return None
