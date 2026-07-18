"""
Contracts app models - Contract, ContractVersion, ContractTerm,
PerformanceObligation, ContractDocument, ContractAmendment.
Manages contract lifecycle and ASC 606 compliance.
"""

import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.users.models import BaseModel


# =============================================================================
# Contract Model
# =============================================================================

class Contract(BaseModel):
    """Primary contract model representing client agreements."""

    class BillingModelChoices(models.TextChoices):
        FIXED_PRICE = "fixed_price", "Fixed Price"
        TIME_AND_MATERIAL = "time_and_material", "Time & Material"
        RETAINER = "retainer", "Retainer"
        MILESTONE = "milestone", "Milestone-Based"
        HYBRID = "hybrid", "Hybrid"
        OUTCOME_BASED = "outcome_based", "Outcome-Based"
        SUBSCRIPTION = "subscription", "Subscription"

    class CurrencyChoices(models.TextChoices):
        INR = "INR", "Indian Rupee"
        USD = "USD", "US Dollar"
        EUR = "EUR", "Euro"
        GBP = "GBP", "British Pound"
        AED = "AED", "UAE Dirham"
        SGD = "SGD", "Singapore Dollar"

    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_APPROVAL = "pending_approval", "Pending Approval"
        ACTIVE = "active", "Active"
        ON_HOLD = "on_hold", "On Hold"
        EXPIRING = "expiring", "Expiring Soon"
        EXPIRED = "expired", "Expired"
        TERMINATED = "terminated", "Terminated"
        RENEWED = "renewed", "Renewed"

    class PaymentTermChoices(models.TextChoices):
        NET_15 = "net_15", "Net 15"
        NET_30 = "net_30", "Net 30"
        NET_45 = "net_45", "Net 45"
        NET_60 = "net_60", "Net 60"
        NET_90 = "net_90", "Net 90"
        IMMEDIATE = "immediate", "Immediate"
        ADVANCE = "advance", "Advance"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="contracts",
    )
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        related_name="contracts",
    )
    contract_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique contract identifier (e.g., CTR-2024-001)",
    )
    title = models.CharField(max_length=500)
    billing_model = models.CharField(
        max_length=20,
        choices=BillingModelChoices.choices,
        default=BillingModelChoices.TIME_AND_MATERIAL,
    )
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.INR,
    )
    total_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Total contract value",
    )
    monthly_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Monthly recurring value",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    auto_renewal = models.BooleanField(default=False)
    renewal_term_months = models.PositiveIntegerField(
        default=12,
        help_text="Auto-renewal term in months",
    )
    payment_terms = models.CharField(
        max_length=20,
        choices=PaymentTermChoices.choices,
        default=PaymentTermChoices.NET_30,
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        db_index=True,
    )
    asc606_compliant = models.BooleanField(
        default=False,
        help_text="Whether contract has been evaluated for ASC 606 compliance",
    )
    signed_date = models.DateField(null=True, blank=True)
    document_url = models.URLField(max_length=500, blank=True, default="")
    description = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "Contract"
        verbose_name_plural = "Contracts"
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["client", "status"]),
            models.Index(fields=["start_date", "end_date"]),
            models.Index(fields=["billing_model"]),
            models.Index(fields=["contract_number"]),
        ]

    def __str__(self):
        return f"{self.contract_number} - {self.title}"

    @property
    def is_active(self):
        from django.utils import timezone
        today = timezone.now().date()
        return self.status == self.StatusChoices.ACTIVE and self.start_date <= today <= self.end_date

    @property
    def remaining_value(self):
        recognized = self.revenue_schedules.aggregate(
            total=models.Sum("recognized_amount")
        )["total"] or 0
        return self.total_value - recognized


# =============================================================================
# Contract Version Model
# =============================================================================

class ContractVersion(BaseModel):
    """Tracks version history of contract changes."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    version_number = models.PositiveIntegerField()
    changes_summary = models.TextField()
    effective_date = models.DateField()
    snapshot_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON snapshot of contract state at this version",
    )

    class Meta:
        ordering = ["-version_number"]
        verbose_name = "Contract Version"
        verbose_name_plural = "Contract Versions"
        unique_together = ["contract", "version_number"]
        indexes = [
            models.Index(fields=["contract", "version_number"]),
        ]

    def __str__(self):
        return f"{self.contract.contract_number} v{self.version_number}"


# =============================================================================
# Contract Term Model
# =============================================================================

class ContractTerm(BaseModel):
    """Individual terms and conditions within a contract."""

    class TermType(models.TextChoices):
        PAYMENT = "payment", "Payment Term"
        SLA = "sla", "Service Level Agreement"
        PENALTY = "penalty", "Penalty Clause"
        TERMINATION = "termination", "Termination Clause"
        RENEWAL = "renewal", "Renewal Term"
        ESCALATION = "escalation", "Escalation Clause"
        WARRANTY = "warranty", "Warranty"
        INDEMNITY = "indemnity", "Indemnity"
        CONFIDENTIALITY = "confidentiality", "Confidentiality"

    class EscalationFrequency(models.TextChoices):
        ANNUAL = "annual", "Annual"
        SEMI_ANNUAL = "semi_annual", "Semi-Annual"
        QUARTERLY = "quarterly", "Quarterly"
        ON_RENEWAL = "on_renewal", "On Renewal"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="terms",
    )
    term_type = models.CharField(
        max_length=20,
        choices=TermType.choices,
    )
    description = models.TextField()
    value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
    )
    unit = models.CharField(max_length=50, blank=True, default="")
    escalation_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Escalation rate as percentage",
    )
    escalation_frequency = models.CharField(
        max_length=20,
        choices=EscalationFrequency.choices,
        blank=True,
        default="",
    )

    class Meta:
        ordering = ["term_type"]
        verbose_name = "Contract Term"
        verbose_name_plural = "Contract Terms"
        indexes = [
            models.Index(fields=["contract", "term_type"]),
        ]

    def __str__(self):
        return f"{self.contract.contract_number} - {self.get_term_type_display()}"


# =============================================================================
# Performance Obligation Model
# =============================================================================

class PerformanceObligation(BaseModel):
    """ASC 606 performance obligations within a contract."""

    class RecognitionPattern(models.TextChoices):
        OVER_TIME = "over_time", "Over Time"
        POINT_IN_TIME = "point_in_time", "Point in Time"

    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        SATISFIED = "satisfied", "Satisfied"
        PARTIALLY_SATISFIED = "partially_satisfied", "Partially Satisfied"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="performance_obligations",
    )
    description = models.TextField()
    standalone_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Standalone selling price for allocation",
    )
    allocation_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Allocated transaction price",
    )
    recognition_pattern = models.CharField(
        max_length=20,
        choices=RecognitionPattern.choices,
        default=RecognitionPattern.OVER_TIME,
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    satisfaction_criteria = models.TextField(
        blank=True,
        default="",
        help_text="Criteria for determining when obligation is satisfied",
    )
    expected_completion_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["contract", "description"]
        verbose_name = "Performance Obligation"
        verbose_name_plural = "Performance Obligations"
        indexes = [
            models.Index(fields=["contract", "status"]),
            models.Index(fields=["recognition_pattern"]),
        ]

    def __str__(self):
        return f"{self.contract.contract_number} - {self.description[:50]}"


# =============================================================================
# Contract Document Model
# =============================================================================

class ContractDocument(BaseModel):
    """Documents attached to contracts with OCR and AI extraction."""

    class DocumentType(models.TextChoices):
        CONTRACT = "contract", "Contract"
        SOW = "sow", "Statement of Work"
        AMENDMENT = "amendment", "Amendment"
        PO = "po", "Purchase Order"
        NDA = "nda", "Non-Disclosure Agreement"
        MSA = "msa", "Master Service Agreement"
        INVOICE = "invoice", "Invoice"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
    )
    file_url = models.URLField(max_length=500)
    file_name = models.CharField(max_length=255, blank=True, default="")
    file_size = models.PositiveIntegerField(default=0, help_text="File size in bytes")
    ocr_text = models.TextField(blank=True, default="")
    extracted_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="AI-extracted structured data from document",
    )
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="AI extraction confidence (0-1)",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_documents",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contract Document"
        verbose_name_plural = "Contract Documents"
        indexes = [
            models.Index(fields=["contract", "document_type"]),
        ]

    def __str__(self):
        return f"{self.contract.contract_number} - {self.get_document_type_display()}"


# =============================================================================
# Contract Amendment Model
# =============================================================================

class ContractAmendment(BaseModel):
    """Amendments/modifications to existing contracts."""

    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING = "pending", "Pending Approval"
        APPROVED = "approved", "Approved"
        EXECUTED = "executed", "Executed"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="amendments",
    )
    amendment_number = models.CharField(max_length=50)
    description = models.TextField()
    effective_date = models.DateField()
    value_change = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Positive for increase, negative for decrease",
    )
    new_terms = models.JSONField(
        default=dict,
        blank=True,
        help_text="Modified terms as structured JSON",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_amendments",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-effective_date"]
        verbose_name = "Contract Amendment"
        verbose_name_plural = "Contract Amendments"
        unique_together = ["contract", "amendment_number"]
        indexes = [
            models.Index(fields=["contract", "status"]),
            models.Index(fields=["effective_date"]),
        ]

    def __str__(self):
        return f"{self.contract.contract_number} - Amendment {self.amendment_number}"
