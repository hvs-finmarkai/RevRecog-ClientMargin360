"""
Recognition app models - RevenueSchedule, RevenueEntry, RecognitionRule,
ASC606Compliance.
Manages revenue recognition per ASC 606 / Ind AS 115 standards.
"""

import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.users.models import BaseModel


# =============================================================================
# Revenue Schedule Model
# =============================================================================

class RevenueSchedule(BaseModel):
    """Revenue recognition schedule for a contract or performance obligation."""

    class PatternChoices(models.TextChoices):
        STRAIGHT_LINE = "straight_line", "Straight Line"
        PERCENTAGE_COMPLETION = "percentage_completion", "Percentage of Completion"
        MILESTONE = "milestone", "Milestone-Based"
        USAGE = "usage", "Usage-Based"
        OUTPUT = "output", "Output Method"
        INPUT = "input", "Input Method"

    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        SUSPENDED = "suspended", "Suspended"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.CASCADE,
        related_name="revenue_schedules",
    )
    performance_obligation = models.ForeignKey(
        "contracts.PerformanceObligation",
        on_delete=models.CASCADE,
        related_name="revenue_schedules",
        null=True,
        blank=True,
    )
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Total amount to be recognized",
    )
    recognized_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Amount recognized to date",
    )
    deferred_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Deferred revenue balance",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    pattern = models.CharField(
        max_length=25,
        choices=PatternChoices.choices,
        default=PatternChoices.STRAIGHT_LINE,
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
    )
    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "Revenue Schedule"
        verbose_name_plural = "Revenue Schedules"
        indexes = [
            models.Index(fields=["contract", "status"]),
            models.Index(fields=["performance_obligation"]),
            models.Index(fields=["pattern"]),
            models.Index(fields=["start_date", "end_date"]),
        ]

    def __str__(self):
        return f"{self.contract.contract_number} - {self.get_pattern_display()} ({self.total_amount})"

    @property
    def remaining_amount(self):
        return self.total_amount - self.recognized_amount

    @property
    def recognition_percentage(self):
        if self.total_amount > 0:
            return (self.recognized_amount / self.total_amount) * 100
        return 0


# =============================================================================
# Revenue Entry Model
# =============================================================================

class RevenueEntry(BaseModel):
    """Individual revenue recognition entries (journal entries)."""

    class EntryType(models.TextChoices):
        RECOGNIZED = "recognized", "Revenue Recognized"
        DEFERRED = "deferred", "Deferred Revenue"
        ADJUSTMENT = "adjustment", "Adjustment"
        REVERSAL = "reversal", "Reversal"
        CATCH_UP = "catch_up", "Catch-Up Adjustment"

    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Draft"
        POSTED = "posted", "Posted"
        REVERSED = "reversed", "Reversed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schedule = models.ForeignKey(
        RevenueSchedule,
        on_delete=models.CASCADE,
        related_name="entries",
    )
    period_start = models.DateField()
    period_end = models.DateField()
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Amount for this entry (can be negative for reversals)",
    )
    entry_type = models.CharField(
        max_length=20,
        choices=EntryType.choices,
        default=EntryType.RECOGNIZED,
    )
    journal_entry_ref = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Reference to accounting journal entry",
    )
    posted_date = models.DateField(null=True, blank=True)
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posted_revenue_entries",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-period_start"]
        verbose_name = "Revenue Entry"
        verbose_name_plural = "Revenue Entries"
        indexes = [
            models.Index(fields=["schedule", "entry_type"]),
            models.Index(fields=["period_start", "period_end"]),
            models.Index(fields=["status"]),
            models.Index(fields=["posted_date"]),
        ]

    def __str__(self):
        return f"{self.schedule.contract.contract_number} - {self.get_entry_type_display()} ({self.amount})"


# =============================================================================
# Recognition Rule Model
# =============================================================================

class RecognitionRule(BaseModel):
    """Rules engine for automatic revenue recognition pattern selection."""

    class RecognitionPattern(models.TextChoices):
        STRAIGHT_LINE = "straight_line", "Straight Line"
        PERCENTAGE_COMPLETION = "percentage_completion", "Percentage of Completion"
        MILESTONE = "milestone", "Milestone-Based"
        USAGE = "usage", "Usage-Based"
        OUTPUT = "output", "Output Method"
        INPUT = "input", "Input Method"

    class TimingChoices(models.TextChoices):
        OVER_TIME = "over_time", "Over Time"
        POINT_IN_TIME = "point_in_time", "Point in Time"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    billing_model = models.CharField(
        max_length=50,
        help_text="Billing model code this rule applies to",
    )
    condition = models.JSONField(
        default=dict,
        blank=True,
        help_text="Conditions under which this rule applies (JSON)",
    )
    recognition_pattern = models.CharField(
        max_length=25,
        choices=RecognitionPattern.choices,
    )
    timing = models.CharField(
        max_length=20,
        choices=TimingChoices.choices,
        default=TimingChoices.OVER_TIME,
    )
    description = models.TextField(blank=True, default="")
    priority = models.PositiveIntegerField(
        default=100,
        help_text="Lower number = higher priority",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["priority", "name"]
        verbose_name = "Recognition Rule"
        verbose_name_plural = "Recognition Rules"
        indexes = [
            models.Index(fields=["billing_model"]),
            models.Index(fields=["recognition_pattern"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_recognition_pattern_display()})"


# =============================================================================
# ASC 606 Compliance Model
# =============================================================================

class ASC606Compliance(BaseModel):
    """Tracks ASC 606 (Ind AS 115) five-step compliance for contracts."""

    class ComplianceStatus(models.TextChoices):
        NOT_STARTED = "not_started", "Not Started"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLIANT = "compliant", "Compliant"
        NON_COMPLIANT = "non_compliant", "Non-Compliant"
        NEEDS_REVIEW = "needs_review", "Needs Review"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.OneToOneField(
        "contracts.Contract",
        on_delete=models.CASCADE,
        related_name="asc606_compliance",
    )
    # Step 1: Identify the contract
    step1_identified = models.BooleanField(
        default=False,
        help_text="Step 1: Contract with customer identified",
    )
    step1_notes = models.TextField(blank=True, default="")
    step1_date = models.DateField(null=True, blank=True)

    # Step 2: Identify performance obligations
    step2_obligations_identified = models.BooleanField(
        default=False,
        help_text="Step 2: Performance obligations identified",
    )
    step2_notes = models.TextField(blank=True, default="")
    step2_date = models.DateField(null=True, blank=True)

    # Step 3: Determine transaction price
    step3_price_determined = models.BooleanField(
        default=False,
        help_text="Step 3: Transaction price determined",
    )
    step3_notes = models.TextField(blank=True, default="")
    step3_date = models.DateField(null=True, blank=True)

    # Step 4: Allocate transaction price
    step4_allocated = models.BooleanField(
        default=False,
        help_text="Step 4: Transaction price allocated to obligations",
    )
    step4_notes = models.TextField(blank=True, default="")
    step4_date = models.DateField(null=True, blank=True)

    # Step 5: Recognize revenue
    step5_recognized = models.BooleanField(
        default=False,
        help_text="Step 5: Revenue recognized when/as obligations satisfied",
    )
    step5_notes = models.TextField(blank=True, default="")
    step5_date = models.DateField(null=True, blank=True)

    compliance_status = models.CharField(
        max_length=20,
        choices=ComplianceStatus.choices,
        default=ComplianceStatus.NOT_STARTED,
    )
    last_review_date = models.DateField(null=True, blank=True)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asc606_reviews",
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-last_review_date"]
        verbose_name = "ASC 606 Compliance"
        verbose_name_plural = "ASC 606 Compliances"
        indexes = [
            models.Index(fields=["compliance_status"]),
            models.Index(fields=["last_review_date"]),
        ]

    def __str__(self):
        return f"{self.contract.contract_number} - {self.get_compliance_status_display()}"

    @property
    def completion_percentage(self):
        steps = [
            self.step1_identified,
            self.step2_obligations_identified,
            self.step3_price_determined,
            self.step4_allocated,
            self.step5_recognized,
        ]
        return (sum(steps) / len(steps)) * 100

    @property
    def is_fully_compliant(self):
        return all([
            self.step1_identified,
            self.step2_obligations_identified,
            self.step3_price_determined,
            self.step4_allocated,
            self.step5_recognized,
        ])
