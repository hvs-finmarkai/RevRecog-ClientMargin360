"""
Invoices app models - Invoice, InvoiceLineItem, InvoiceTemplate,
CreditNote, DebitNote, InvoiceApproval.
Manages invoice generation, approval workflow, and credit/debit notes.
"""

import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.users.models import BaseModel


# =============================================================================
# Invoice Template Model
# =============================================================================

class InvoiceTemplate(BaseModel):
    """Templates for invoice generation and formatting."""

    class FormatChoices(models.TextChoices):
        PDF = "pdf", "PDF"
        EXCEL = "excel", "Excel"
        HTML = "html", "HTML"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="invoice_templates",
    )
    format = models.CharField(
        max_length=10,
        choices=FormatChoices.choices,
        default=FormatChoices.PDF,
    )
    header_html = models.TextField(blank=True, default="")
    footer_html = models.TextField(blank=True, default="")
    logo_url = models.URLField(max_length=500, blank=True, default="")
    terms_text = models.TextField(
        blank=True,
        default="",
        help_text="Default terms and conditions text",
    )
    is_default = models.BooleanField(default=False)
    css_styles = models.TextField(blank=True, default="")
    page_size = models.CharField(max_length=10, default="A4")

    class Meta:
        ordering = ["-is_default", "name"]
        verbose_name = "Invoice Template"
        verbose_name_plural = "Invoice Templates"
        indexes = [
            models.Index(fields=["organization", "is_default"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_format_display()})"


# =============================================================================
# Invoice Model
# =============================================================================

class Invoice(BaseModel):
    """Primary invoice model with full GST compliance."""

    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_APPROVAL = "pending_approval", "Pending Approval"
        APPROVED = "approved", "Approved"
        SENT = "sent", "Sent"
        PAID = "paid", "Paid"
        PARTIALLY_PAID = "partially_paid", "Partially Paid"
        OVERDUE = "overdue", "Overdue"
        CANCELLED = "cancelled", "Cancelled"
        DISPUTED = "disputed", "Disputed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "users.Organization",
        on_delete=models.CASCADE,
        related_name="invoices",
    )
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        related_name="invoices",
    )
    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices",
    )
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique invoice number (e.g., INV-2024-001)",
    )
    invoice_date = models.DateField(db_index=True)
    due_date = models.DateField(db_index=True)
    subtotal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    tax_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    cgst = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Central GST amount",
    )
    sgst = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="State GST amount",
    )
    igst = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Integrated GST amount",
    )
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    tds_applicable = models.BooleanField(
        default=False,
        help_text="Whether TDS is applicable on this invoice",
    )
    tds_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    tds_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    net_receivable = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Amount receivable after TDS deduction",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        db_index=True,
    )
    po_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Client's Purchase Order number",
    )
    po_date = models.DateField(null=True, blank=True)
    billing_period_start = models.DateField(null=True, blank=True)
    billing_period_end = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    internal_notes = models.TextField(blank=True, default="")
    template = models.ForeignKey(
        InvoiceTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_invoices",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=255, blank=True, default="")
    currency = models.CharField(max_length=3, default="INR")
    exchange_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=1.0000,
    )

    class Meta:
        ordering = ["-invoice_date"]
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["client", "status"]),
            models.Index(fields=["invoice_number"]),
            models.Index(fields=["invoice_date"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["contract"]),
        ]

    def __str__(self):
        return f"{self.invoice_number} - {self.client.name} ({self.total_amount})"

    @property
    def is_overdue(self):
        from django.utils import timezone
        return (
            self.status not in [self.StatusChoices.PAID, self.StatusChoices.CANCELLED]
            and self.due_date < timezone.now().date()
        )

    @property
    def amount_paid(self):
        return self.payment_receipts.filter(
            reconciled=True
        ).aggregate(total=models.Sum("amount"))["total"] or 0

    @property
    def balance_due(self):
        return self.net_receivable - self.amount_paid


# =============================================================================
# Invoice Line Item Model
# =============================================================================

class InvoiceLineItem(BaseModel):
    """Individual line items within an invoice with GenericFK for billable reference."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="line_items",
    )
    description = models.TextField()
    hsn_code = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="HSN/SAC code for GST classification",
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1,
        validators=[MinValueValidator(0)],
    )
    unit = models.CharField(
        max_length=50,
        default="units",
        help_text="Unit of measurement (hours, days, units, etc.)",
    )
    rate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=18.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Tax rate percentage",
    )
    tax_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    # Generic FK for linking to any billable entity
    billable_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    billable_object_id = models.CharField(max_length=255, blank=True, default="")
    billable_reference = GenericForeignKey("billable_content_type", "billable_object_id")
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Invoice Line Item"
        verbose_name_plural = "Invoice Line Items"
        indexes = [
            models.Index(fields=["invoice"]),
            models.Index(fields=["hsn_code"]),
            models.Index(
                fields=["billable_content_type", "billable_object_id"],
                name="idx_billable_ref",
            ),
        ]

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.description[:50]}"

    def save(self, *args, **kwargs):
        if not self.amount:
            self.amount = self.quantity * self.rate
        if not self.tax_amount:
            self.tax_amount = self.amount * (self.tax_rate / 100)
        super().save(*args, **kwargs)


# =============================================================================
# Credit Note Model
# =============================================================================

class CreditNote(BaseModel):
    """Credit notes issued against invoices."""

    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        APPLIED = "applied", "Applied"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="credit_notes",
    )
    credit_note_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
    )
    date = models.DateField()
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
    )
    tax_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        ordering = ["-date"]
        verbose_name = "Credit Note"
        verbose_name_plural = "Credit Notes"
        indexes = [
            models.Index(fields=["invoice"]),
            models.Index(fields=["credit_note_number"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.credit_note_number} - {self.amount}"


# =============================================================================
# Debit Note Model
# =============================================================================

class DebitNote(BaseModel):
    """Debit notes issued against invoices."""

    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        APPLIED = "applied", "Applied"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="debit_notes",
    )
    debit_note_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
    )
    date = models.DateField()
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
    )
    tax_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        ordering = ["-date"]
        verbose_name = "Debit Note"
        verbose_name_plural = "Debit Notes"
        indexes = [
            models.Index(fields=["invoice"]),
            models.Index(fields=["debit_note_number"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.debit_note_number} - {self.amount}"


# =============================================================================
# Invoice Approval Model
# =============================================================================

class InvoiceApproval(BaseModel):
    """Approval workflow records for invoices."""

    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        RETURNED = "returned", "Returned for Revision"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="approvals",
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invoice_approvals",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    comments = models.TextField(blank=True, default="")
    approved_at = models.DateTimeField(null=True, blank=True)
    step_order = models.PositiveIntegerField(
        default=1,
        help_text="Order in multi-step approval workflow",
    )

    class Meta:
        ordering = ["step_order", "-created_at"]
        verbose_name = "Invoice Approval"
        verbose_name_plural = "Invoice Approvals"
        indexes = [
            models.Index(fields=["invoice", "status"]),
            models.Index(fields=["approver", "status"]),
        ]

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.approver.get_full_name()} ({self.get_status_display()})"
