"""
Billing app models - BillingModel, RateCard, RateCardItem, BillingPeriod,
BillingSchedule, EscalationRule.
Manages billing configurations, rate cards, and billing cycles.
"""

import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.users.models import BaseModel


# =============================================================================
# Billing Model
# =============================================================================

class BillingModel(BaseModel):
    """Billing model configurations that define how clients are billed."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Short code for the billing model (e.g., TM, FP, RET)",
    )
    description = models.TextField(blank=True, default="")
    rules = models.JSONField(
        default=dict,
        blank=True,
        help_text="Billing rules engine configuration as JSON",
    )
    is_active = models.BooleanField(default=True)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="billing_models",
        null=True,
        blank=True,
        help_text="Null means system-wide billing model",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Billing Model"
        verbose_name_plural = "Billing Models"
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


# =============================================================================
# Rate Card Model
# =============================================================================

class RateCard(BaseModel):
    """Rate cards defining pricing for client engagements."""

    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        SUPERSEDED = "superseded", "Superseded"

    class CurrencyChoices(models.TextChoices):
        INR = "INR", "Indian Rupee"
        USD = "USD", "US Dollar"
        EUR = "EUR", "Euro"
        GBP = "GBP", "British Pound"
        AED = "AED", "UAE Dirham"
        SGD = "SGD", "Singapore Dollar"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        related_name="rate_cards",
    )
    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.CASCADE,
        related_name="rate_cards",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=200)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.INR,
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-effective_from"]
        verbose_name = "Rate Card"
        verbose_name_plural = "Rate Cards"
        indexes = [
            models.Index(fields=["client", "status"]),
            models.Index(fields=["effective_from", "effective_to"]),
            models.Index(fields=["contract"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.client.name}"

    @property
    def is_current(self):
        from django.utils import timezone
        today = timezone.now().date()
        if self.effective_to:
            return self.effective_from <= today <= self.effective_to
        return self.effective_from <= today


# =============================================================================
# Rate Card Item Model
# =============================================================================

class RateCardItem(BaseModel):
    """Individual line items within a rate card."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rate_card = models.ForeignKey(
        RateCard,
        on_delete=models.CASCADE,
        related_name="items",
    )
    role_name = models.CharField(
        max_length=200,
        help_text="Role/designation (e.g., Senior Developer, QA Lead)",
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    daily_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    monthly_rate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    overtime_multiplier = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.50,
        validators=[MinValueValidator(1)],
        help_text="Multiplier for overtime hours (e.g., 1.5x)",
    )
    minimum_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Minimum billable hours per period",
    )

    class Meta:
        ordering = ["role_name"]
        verbose_name = "Rate Card Item"
        verbose_name_plural = "Rate Card Items"
        unique_together = ["rate_card", "role_name"]
        indexes = [
            models.Index(fields=["rate_card", "role_name"]),
        ]

    def __str__(self):
        return f"{self.role_name} - {self.rate_card.name}"


# =============================================================================
# Billing Period Model
# =============================================================================

class BillingPeriod(BaseModel):
    """Defines billing periods for contracts."""

    class StatusChoices(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        CLOSED = "closed", "Closed"
        LOCKED = "locked", "Locked"
        INVOICED = "invoiced", "Invoiced"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.CASCADE,
        related_name="billing_periods",
    )
    period_start = models.DateField()
    period_end = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.OPEN,
    )
    locked_at = models.DateTimeField(null=True, blank=True)
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="locked_billing_periods",
    )
    total_billable_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-period_start"]
        verbose_name = "Billing Period"
        verbose_name_plural = "Billing Periods"
        unique_together = ["contract", "period_start", "period_end"]
        indexes = [
            models.Index(fields=["contract", "status"]),
            models.Index(fields=["period_start", "period_end"]),
        ]

    def __str__(self):
        return f"{self.contract.contract_number} ({self.period_start} to {self.period_end})"


# =============================================================================
# Billing Schedule Model
# =============================================================================

class BillingSchedule(BaseModel):
    """Scheduled billing events for contracts."""

    class FrequencyChoices(models.TextChoices):
        WEEKLY = "weekly", "Weekly"
        BI_WEEKLY = "bi_weekly", "Bi-Weekly"
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        SEMI_ANNUAL = "semi_annual", "Semi-Annual"
        ANNUAL = "annual", "Annual"
        MILESTONE = "milestone", "Milestone-Based"
        ON_DEMAND = "on_demand", "On Demand"

    class StatusChoices(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        GENERATED = "generated", "Generated"
        SKIPPED = "skipped", "Skipped"
        OVERDUE = "overdue", "Overdue"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.CASCADE,
        related_name="billing_schedules",
    )
    frequency = models.CharField(
        max_length=20,
        choices=FrequencyChoices.choices,
        default=FrequencyChoices.MONTHLY,
    )
    next_billing_date = models.DateField(db_index=True)
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.SCHEDULED,
    )
    milestone_description = models.TextField(
        blank=True,
        default="",
        help_text="Description if frequency is milestone-based",
    )
    last_generated_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["next_billing_date"]
        verbose_name = "Billing Schedule"
        verbose_name_plural = "Billing Schedules"
        indexes = [
            models.Index(fields=["contract", "status"]),
            models.Index(fields=["next_billing_date"]),
            models.Index(fields=["frequency"]),
        ]

    def __str__(self):
        return f"{self.contract.contract_number} - {self.get_frequency_display()} ({self.next_billing_date})"


# =============================================================================
# Escalation Rule Model
# =============================================================================

class EscalationRule(BaseModel):
    """Rate escalation rules for contracts."""

    class EscalationType(models.TextChoices):
        ANNUAL = "annual", "Annual Fixed"
        CPI = "cpi", "Consumer Price Index"
        CUSTOM = "custom", "Custom Formula"
        PERFORMANCE = "performance", "Performance-Based"

    class FrequencyChoices(models.TextChoices):
        ANNUAL = "annual", "Annual"
        SEMI_ANNUAL = "semi_annual", "Semi-Annual"
        QUARTERLY = "quarterly", "Quarterly"
        ON_RENEWAL = "on_renewal", "On Renewal"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.CASCADE,
        related_name="escalation_rules",
    )
    escalation_type = models.CharField(
        max_length=20,
        choices=EscalationType.choices,
        default=EscalationType.ANNUAL,
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Escalation percentage",
    )
    frequency = models.CharField(
        max_length=20,
        choices=FrequencyChoices.choices,
        default=FrequencyChoices.ANNUAL,
    )
    next_escalation_date = models.DateField(db_index=True)
    last_applied = models.DateField(null=True, blank=True)
    auto_apply = models.BooleanField(
        default=False,
        help_text="Automatically apply escalation when due",
    )
    cap_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Maximum cumulative escalation cap",
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["next_escalation_date"]
        verbose_name = "Escalation Rule"
        verbose_name_plural = "Escalation Rules"
        indexes = [
            models.Index(fields=["contract", "escalation_type"]),
            models.Index(fields=["next_escalation_date"]),
            models.Index(fields=["auto_apply"]),
        ]

    def __str__(self):
        return f"{self.contract.contract_number} - {self.get_escalation_type_display()} ({self.percentage}%)"
