"""
Invoices app serializers - InvoiceListSerializer, InvoiceDetailSerializer,
InvoiceCreateSerializer, InvoiceLineItemSerializer, InvoiceTemplateSerializer,
CreditNoteSerializer, DebitNoteSerializer, InvoiceApprovalSerializer,
InvoiceGenerateSerializer.
"""

from django.utils import timezone
from rest_framework import serializers

from .models import (
    CreditNote,
    DebitNote,
    Invoice,
    InvoiceApproval,
    InvoiceLineItem,
    InvoiceTemplate,
)


# =============================================================================
# Invoice Template Serializer
# =============================================================================

class InvoiceTemplateSerializer(serializers.ModelSerializer):
    """Serializer for InvoiceTemplate model."""

    format_display = serializers.CharField(
        source="get_format_display", read_only=True
    )

    class Meta:
        model = InvoiceTemplate
        fields = [
            "id", "name", "organization", "format", "format_display",
            "header_html", "footer_html", "logo_url",
            "terms_text", "is_default", "css_styles", "page_size",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# =============================================================================
# Invoice Line Item Serializer
# =============================================================================

class InvoiceLineItemSerializer(serializers.ModelSerializer):
    """Serializer for InvoiceLineItem model."""

    net_amount = serializers.SerializerMethodField()

    class Meta:
        model = InvoiceLineItem
        fields = [
            "id", "invoice", "description", "hsn_code",
            "quantity", "unit", "rate", "amount",
            "discount_percentage", "tax_rate", "tax_amount",
            "sort_order", "net_amount",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "amount", "tax_amount", "created_at", "updated_at"]

    def get_net_amount(self, obj):
        return obj.amount + obj.tax_amount if obj.amount else 0

    def validate(self, attrs):
        quantity = attrs.get("quantity", 1)
        rate = attrs.get("rate", 0)

        if quantity <= 0:
            raise serializers.ValidationError(
                {"quantity": "Quantity must be greater than zero."}
            )
        if rate < 0:
            raise serializers.ValidationError(
                {"rate": "Rate cannot be negative."}
            )
        return attrs


# =============================================================================
# Credit Note Serializer
# =============================================================================

class CreditNoteSerializer(serializers.ModelSerializer):
    """Serializer for CreditNote model."""

    invoice_number = serializers.CharField(
        source="invoice.invoice_number", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = CreditNote
        fields = [
            "id", "invoice", "invoice_number",
            "credit_note_number", "date", "amount",
            "reason", "status", "status_display", "tax_amount",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Credit note amount must be positive.")
        return value

    def validate(self, attrs):
        invoice = attrs.get("invoice") or (self.instance.invoice if self.instance else None)
        amount = attrs.get("amount", 0)

        if invoice and amount > invoice.total_amount:
            raise serializers.ValidationError(
                {"amount": "Credit note amount cannot exceed the invoice total amount."}
            )
        return attrs


# =============================================================================
# Debit Note Serializer
# =============================================================================

class DebitNoteSerializer(serializers.ModelSerializer):
    """Serializer for DebitNote model."""

    invoice_number = serializers.CharField(
        source="invoice.invoice_number", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = DebitNote
        fields = [
            "id", "invoice", "invoice_number",
            "debit_note_number", "date", "amount",
            "reason", "status", "status_display", "tax_amount",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Debit note amount must be positive.")
        return value


# =============================================================================
# Invoice Approval Serializer
# =============================================================================

class InvoiceApprovalSerializer(serializers.ModelSerializer):
    """Serializer for InvoiceApproval model."""

    invoice_number = serializers.CharField(
        source="invoice.invoice_number", read_only=True
    )
    approver_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = InvoiceApproval
        fields = [
            "id", "invoice", "invoice_number",
            "approver", "approver_name",
            "status", "status_display",
            "comments", "approved_at", "step_order",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "approved_at", "created_at", "updated_at"]

    def get_approver_name(self, obj):
        return obj.approver.get_full_name()


# =============================================================================
# Invoice List Serializer (Read - Lightweight)
# =============================================================================

class InvoiceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for invoice list views."""

    client_name = serializers.CharField(source="client.name", read_only=True)
    contract_number = serializers.CharField(
        source="contract.contract_number", read_only=True, default=None
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    is_overdue = serializers.BooleanField(read_only=True)
    balance_due = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    days_outstanding = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            "id", "invoice_number", "client", "client_name",
            "contract", "contract_number",
            "invoice_date", "due_date",
            "total_amount", "net_receivable",
            "status", "status_display",
            "currency", "is_overdue", "balance_due",
            "days_outstanding", "created_at",
        ]
        read_only_fields = ["id", "invoice_number", "created_at"]

    def get_days_outstanding(self, obj):
        if obj.status in ["paid", "cancelled"]:
            return 0
        today = timezone.now().date()
        return max(0, (today - obj.due_date).days)


# =============================================================================
# Invoice Detail Serializer (Read - Full)
# =============================================================================

class InvoiceDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer for invoice with nested objects."""

    client_name = serializers.CharField(source="client.name", read_only=True)
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    contract_number = serializers.CharField(
        source="contract.contract_number", read_only=True, default=None
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    is_overdue = serializers.BooleanField(read_only=True)
    amount_paid = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    balance_due = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    approved_by_name = serializers.SerializerMethodField()
    line_items = InvoiceLineItemSerializer(many=True, read_only=True)
    credit_notes = CreditNoteSerializer(many=True, read_only=True)
    debit_notes = DebitNoteSerializer(many=True, read_only=True)
    approvals = InvoiceApprovalSerializer(many=True, read_only=True)
    template_name = serializers.CharField(
        source="template.name", read_only=True, default=None
    )

    class Meta:
        model = Invoice
        fields = [
            "id", "organization", "organization_name",
            "client", "client_name",
            "contract", "contract_number",
            "invoice_number", "invoice_date", "due_date",
            "subtotal", "tax_amount", "cgst", "sgst", "igst",
            "total_amount", "tds_applicable", "tds_rate",
            "tds_amount", "net_receivable",
            "status", "status_display",
            "po_number", "po_date",
            "billing_period_start", "billing_period_end",
            "notes", "internal_notes",
            "template", "template_name",
            "approved_by", "approved_by_name",
            "approved_at", "sent_at", "paid_at",
            "payment_reference", "currency", "exchange_rate",
            "is_overdue", "amount_paid", "balance_due",
            "line_items", "credit_notes", "debit_notes", "approvals",
            "created_at", "updated_at", "created_by", "updated_by",
        ]
        read_only_fields = [
            "id", "invoice_number", "approved_by", "approved_at",
            "sent_at", "paid_at", "created_at", "updated_at",
            "created_by", "updated_by",
        ]

    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return obj.approved_by.get_full_name()
        return None


# =============================================================================
# Invoice Create Serializer (Write)
# =============================================================================

class InvoiceCreateSerializer(serializers.ModelSerializer):
    """Write serializer for creating/updating invoices with nested line items."""

    line_items = InvoiceLineItemSerializer(many=True, required=False)

    class Meta:
        model = Invoice
        fields = [
            "id", "organization", "client", "contract",
            "invoice_date", "due_date",
            "po_number", "po_date",
            "billing_period_start", "billing_period_end",
            "notes", "internal_notes",
            "template", "currency", "exchange_rate",
            "tds_applicable", "tds_rate",
            "line_items",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        invoice_date = attrs.get("invoice_date")
        due_date = attrs.get("due_date")

        if invoice_date and due_date and due_date < invoice_date:
            raise serializers.ValidationError(
                {"due_date": "Due date cannot be before invoice date."}
            )

        billing_start = attrs.get("billing_period_start")
        billing_end = attrs.get("billing_period_end")
        if billing_start and billing_end and billing_end <= billing_start:
            raise serializers.ValidationError(
                {"billing_period_end": "Billing period end must be after start."}
            )

        return attrs

    def _calculate_totals(self, invoice, line_items):
        """Calculate invoice totals from line items."""
        subtotal = sum(item.amount for item in line_items)
        tax_amount = sum(item.tax_amount for item in line_items)
        total_amount = subtotal + tax_amount

        invoice.subtotal = subtotal
        invoice.tax_amount = tax_amount
        invoice.total_amount = total_amount

        if invoice.tds_applicable and invoice.tds_rate:
            invoice.tds_amount = subtotal * (invoice.tds_rate / 100)
        else:
            invoice.tds_amount = 0

        invoice.net_receivable = total_amount - invoice.tds_amount
        invoice.save()

    def create(self, validated_data):
        line_items_data = validated_data.pop("line_items", [])
        invoice = Invoice.objects.create(**validated_data)

        created_items = []
        for item_data in line_items_data:
            item_data.pop("invoice", None)
            item = InvoiceLineItem(invoice=invoice, **item_data)
            item.amount = item.quantity * item.rate
            item.tax_amount = item.amount * (item.tax_rate / 100)
            item.save()
            created_items.append(item)

        if created_items:
            self._calculate_totals(invoice, created_items)

        return invoice

    def update(self, instance, validated_data):
        line_items_data = validated_data.pop("line_items", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if line_items_data is not None:
            instance.line_items.all().delete()
            created_items = []
            for item_data in line_items_data:
                item_data.pop("invoice", None)
                item = InvoiceLineItem(invoice=instance, **item_data)
                item.amount = item.quantity * item.rate
                item.tax_amount = item.amount * (item.tax_rate / 100)
                item.save()
                created_items.append(item)

            if created_items:
                self._calculate_totals(instance, created_items)

        return instance


# =============================================================================
# Invoice Generate Serializer (Action)
# =============================================================================

class InvoiceGenerateSerializer(serializers.Serializer):
    """Serializer for bulk invoice generation action."""

    contract_id = serializers.UUIDField(required=True)
    billing_period_start = serializers.DateField(required=True)
    billing_period_end = serializers.DateField(required=True)
    template_id = serializers.UUIDField(required=False, allow_null=True)
    auto_send = serializers.BooleanField(default=False)
    include_expenses = serializers.BooleanField(default=True)

    def validate(self, attrs):
        billing_start = attrs.get("billing_period_start")
        billing_end = attrs.get("billing_period_end")

        if billing_end <= billing_start:
            raise serializers.ValidationError(
                {"billing_period_end": "Billing period end must be after start."}
            )

        from apps.contracts.models import Contract
        try:
            contract = Contract.objects.get(
                id=attrs["contract_id"], is_deleted=False
            )
        except Contract.DoesNotExist:
            raise serializers.ValidationError(
                {"contract_id": "Contract not found."}
            )

        if contract.status != "active":
            raise serializers.ValidationError(
                {"contract_id": "Contract must be active to generate invoices."}
            )

        attrs["contract"] = contract
        return attrs
