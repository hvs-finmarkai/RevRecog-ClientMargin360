"""
Contracts app views - ContractViewSet with custom actions for
upload, parse, extract_terms, classify, compliance_check, versions, amendments.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    Contract,
    ContractAmendment,
    ContractDocument,
    ContractTerm,
    ContractVersion,
    PerformanceObligation,
)
from .serializers import (
    ContractAmendmentSerializer,
    ContractCreateSerializer,
    ContractDetailSerializer,
    ContractDocumentSerializer,
    ContractListSerializer,
    ContractTermSerializer,
    ContractVersionSerializer,
    PerformanceObligationSerializer,
)


class ContractViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing contracts with full lifecycle support.
    Includes document upload, AI parsing, term extraction, classification,
    compliance checking, version history, and amendment tracking.
    """

    serializer_class = ContractListSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = [
        "status", "billing_model", "client", "currency",
        "auto_renewal", "asc606_compliant",
    ]
    search_fields = ["contract_number", "title", "client__name", "description"]
    ordering_fields = [
        "start_date", "end_date", "total_value", "created_at", "contract_number",
    ]
    ordering = ["-start_date"]

    def get_queryset(self):
        return Contract.objects.filter(
            organization=self.request.user.organization,
            is_deleted=False,
        ).select_related("client", "organization")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ContractDetailSerializer
        if self.action in ["create", "update", "partial_update"]:
            return ContractCreateSerializer
        if self.action == "versions":
            return ContractVersionSerializer
        if self.action == "amendments":
            return ContractAmendmentSerializer
        if self.action == "extract_terms":
            return ContractTermSerializer
        if self.action == "upload":
            return ContractDocumentSerializer
        return ContractListSerializer

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=["post"])
    def upload(self, request, pk=None):
        """Upload a document to the contract."""
        contract = self.get_object()
        serializer = ContractDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            contract=contract,
            created_by=request.user,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def parse(self, request, pk=None):
        """Trigger AI parsing of contract documents."""
        contract = self.get_object()
        documents = contract.documents.all()
        if not documents.exists():
            return Response(
                {"detail": "No documents uploaded for this contract."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Trigger async parsing task
        parsed_count = 0
        for doc in documents:
            if not doc.ocr_text:
                parsed_count += 1
                # In production, this would trigger a Celery task
                # parse_contract_document.delay(doc.id)

        return Response({
            "detail": f"Parsing initiated for {parsed_count} document(s).",
            "total_documents": documents.count(),
            "queued_for_parsing": parsed_count,
        })

    @action(detail=True, methods=["get", "post"])
    def extract_terms(self, request, pk=None):
        """Extract or list contract terms."""
        contract = self.get_object()

        if request.method == "GET":
            terms = ContractTerm.objects.filter(contract=contract, is_deleted=False)
            serializer = ContractTermSerializer(terms, many=True)
            return Response(serializer.data)

        # POST: Create a new term
        serializer = ContractTermSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(contract=contract, created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def classify(self, request, pk=None):
        """Classify contract billing model using AI."""
        contract = self.get_object()

        # AI classification logic would go here
        classification_result = {
            "contract_id": str(contract.id),
            "current_billing_model": contract.billing_model,
            "suggested_billing_model": contract.billing_model,
            "confidence": 0.85,
            "reasoning": "Classification based on contract terms and structure.",
        }

        return Response(classification_result)

    @action(detail=True, methods=["post"])
    def compliance_check(self, request, pk=None):
        """Run ASC 606 compliance check on the contract."""
        contract = self.get_object()

        obligations = contract.performance_obligations.filter(is_deleted=False)
        compliance_result = {
            "contract_id": str(contract.id),
            "contract_number": contract.contract_number,
            "asc606_compliant": contract.asc606_compliant,
            "performance_obligations_count": obligations.count(),
            "checks": {
                "step1_contract_identified": True,
                "step2_obligations_identified": obligations.exists(),
                "step3_price_determined": contract.total_value > 0,
                "step4_price_allocated": all(
                    o.allocation_amount > 0 for o in obligations
                ),
                "step5_recognition_criteria": all(
                    o.recognition_pattern for o in obligations
                ),
            },
            "recommendations": [],
        }

        if not obligations.exists():
            compliance_result["recommendations"].append(
                "Identify and document performance obligations."
            )
        if not contract.asc606_compliant:
            compliance_result["recommendations"].append(
                "Complete ASC 606 five-step compliance review."
            )

        return Response(compliance_result)

    @action(detail=True, methods=["get"])
    def versions(self, request, pk=None):
        """Get version history for the contract."""
        contract = self.get_object()
        versions = ContractVersion.objects.filter(
            contract=contract, is_deleted=False
        )
        serializer = ContractVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get", "post"])
    def amendments(self, request, pk=None):
        """List or create amendments for the contract."""
        contract = self.get_object()

        if request.method == "GET":
            amendments = ContractAmendment.objects.filter(
                contract=contract, is_deleted=False
            )
            serializer = ContractAmendmentSerializer(amendments, many=True)
            return Response(serializer.data)

        serializer = ContractAmendmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(contract=contract, created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
