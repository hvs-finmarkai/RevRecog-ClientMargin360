"""
Invoices app views - InvoiceViewSet with actions: generate, approve, dispatch,
bulk_generate; InvoiceTemplateViewSet, CreditNoteViewSet.
"""

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CreditNote, DebitNote, Invoice, InvoiceApproval, InvoiceTemplate
from .serializers import (
    CreditNoteSerializer,
    DebitNoteSerializer,
    InvoiceApprovalSerializer,
    InvoiceCreateSerializer,
    InvoiceDetailSerializer,
    InvoiceGenerateSerializer,
    InvoiceListSerializer,
    InvoiceTemplateSerializer,
)


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing invoices with generation, approval, and dispatch workflows.
    """

    serializer_class = InvoiceListSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = [
        "status", "client", "contract", "currency",
        "tds_applicable", "template",
    ]
    search_fields = [
        "invoice_number", "client__name", "po_number", "notes",
    ]
    ordering_fields = [
        "invoice_date", "due_date", "total_amount", "created_at",
        "invoice_number",
    ]
    ordering = ["-invoice_date"]

    def get_queryset(self):
        return Invoice.objects.filter(
            organization=self.request.user.organization,
            is_deleted=False,
        ).select_related("client", "contract", "template")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return InvoiceDetailSerializer
        if self.action in ["create", "update", "partial_update"]:
            return InvoiceCreateSerializer
        if self.action in ["generate", "bulk_generate"]:
            return InvoiceGenerateSerializer
        if self.action == "approve":
            return InvoiceApprovalSerializer
        return InvoiceListSerializer

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=False, methods=["post"])
    def generate(self, request):
        """Generate an invoice from contract/billing period data."""
        serializer = InvoiceGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Invoice generation logic
        contract_id = serializer.validated_data.get("contract_id")
        billing_period_start = serializer.validated_data.get("billing_period_start")
        billing_period_end = serializer.validated_data.get("billing_period_end")

        return Response(
            {
                "detail": "Invoice generation initiated.",
                "contract_id": str(contract_id) if contract_id else None,
                "billing_period_start": str(billing_period_start),
                "billing_period_end": str(billing_period_end),
                "status": "processing",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve an invoice."""
        invoice = self.get_object()

        if invoice.status != Invoice.StatusChoices.PENDING_APPROVAL:
            return Response(
                {"detail": "Invoice is not in pending approval state."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comments = request.data.get("comments", "")

        InvoiceApproval.objects.create(
            invoice=invoice,
            approver=request.user,
            status=InvoiceApproval.StatusChoices.APPROVED,
            comments=comments,
            approved_at=timezone.now(),
            created_by=request.user,
        )

        invoice.status = Invoice.StatusChoices.APPROVED
        invoice.approved_by = request.user
        invoice.approved_at = timezone.now()
        invoice.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])

        return Response({"detail": "Invoice approved successfully."})

    @action(detail=True, methods=["post"])
    def dispatch(self, request, pk=None):
        """Dispatch/send an approved invoice to the client."""
        invoice = self.get_object()

        if invoice.status not in [
            Invoice.StatusChoices.APPROVED,
            Invoice.StatusChoices.SENT,
        ]:
            return Response(
                {"detail": "Invoice must be approved before dispatch."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invoice.status = Invoice.StatusChoices.SENT
        invoice.sent_at = timezone.now()
        invoice.save(update_fields=["status", "sent_at", "updated_at"])

        return Response({
            "detail": "Invoice dispatched successfully.",
            "sent_at": invoice.sent_at.isoformat(),
        })

    @action(detail=False, methods=["post"])
    def bulk_generate(self, request):
        """Bulk generate invoices for multiple contracts."""
        contract_ids = request.data.get("contract_ids", [])
        billing_period_start = request.data.get("billing_period_start")
        billing_period_end = request.data.get("billing_period_end")

        if not contract_ids:
            return Response(
                {"detail": "contract_ids list is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": f"Bulk generation initiated for {len(contract_ids)} contracts.",
                "contracts_count": len(contract_ids),
                "billing_period_start": billing_period_start,
                "billing_period_end": billing_period_end,
                "status": "processing",
            },
            status=status.HTTP_202_ACCEPTED,
        )


class InvoiceTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing invoice templates.
    """

    serializer_class = InvoiceTemplateSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["format", "is_default"]
    search_fields = ["name", "terms_text"]
    ordering_fields = ["name", "created_at"]
    ordering = ["-is_default", "name"]

    def get_queryset(self):
        return InvoiceTemplate.objects.filter(
            organization=self.request.user.organization,
            is_deleted=False,
        )

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()


class CreditNoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing credit notes.
    """

    serializer_class = CreditNoteSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "invoice"]
    search_fields = ["credit_note_number", "reason"]
    ordering_fields = ["date", "amount", "created_at"]
    ordering = ["-date"]

    def get_queryset(self):
        return CreditNote.objects.filter(
            invoice__organization=self.request.user.organization,
            is_deleted=False,
        ).select_related("invoice")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()
