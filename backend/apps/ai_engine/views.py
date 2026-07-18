"""
AI Engine app views - AIRecommendationViewSet with actions: generate, accept, reject;
ContractParsingViewSet with action: parse_document.
"""

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import AIModel, AIPrediction, AIRecommendation, ContractParsing, PromptLog
from .serializers import (
    AIModelSerializer,
    AIPredictionSerializer,
    AIRecommendationSerializer,
    ContractParsingSerializer,
    PromptLogSerializer,
)


class AIRecommendationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing AI-generated recommendations with generate, accept, reject actions.
    """

    serializer_class = AIRecommendationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = [
        "recommendation_type", "status", "priority", "client", "contract",
    ]
    search_fields = ["title", "description", "client__name", "contract__contract_number"]
    ordering_fields = [
        "generated_at", "confidence_score", "expected_impact_amount", "priority",
    ]
    ordering = ["-generated_at"]

    def get_queryset(self):
        return AIRecommendation.objects.filter(
            client__organization=self.request.user.organization,
            is_deleted=False,
        ).select_related("client", "contract")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=False, methods=["post"])
    def generate(self, request):
        """Trigger AI recommendation generation for a client or contract."""
        client_id = request.data.get("client_id")
        contract_id = request.data.get("contract_id")
        recommendation_type = request.data.get("recommendation_type")

        if not client_id and not contract_id:
            return Response(
                {"detail": "Either client_id or contract_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # In production, this would trigger the AI pipeline
        return Response({
            "detail": "AI recommendation generation initiated.",
            "client_id": client_id,
            "contract_id": contract_id,
            "recommendation_type": recommendation_type,
            "status": "processing",
            "initiated_at": timezone.now().isoformat(),
        })

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        """Accept an AI recommendation."""
        recommendation = self.get_object()

        if recommendation.status != AIRecommendation.StatusChoices.PENDING:
            return Response(
                {"detail": "Recommendation is not in pending status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        implementation_notes = request.data.get("implementation_notes", "")
        recommendation.status = AIRecommendation.StatusChoices.ACCEPTED
        recommendation.accepted_by = request.user
        recommendation.accepted_at = timezone.now()
        recommendation.implementation_notes = implementation_notes
        recommendation.save(update_fields=[
            "status", "accepted_by", "accepted_at",
            "implementation_notes", "updated_at",
        ])

        return Response({
            "detail": "Recommendation accepted.",
            "recommendation_id": str(recommendation.id),
            "status": recommendation.status,
        })

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject an AI recommendation."""
        recommendation = self.get_object()

        if recommendation.status != AIRecommendation.StatusChoices.PENDING:
            return Response(
                {"detail": "Recommendation is not in pending status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reason = request.data.get("reason", "")
        recommendation.status = AIRecommendation.StatusChoices.REJECTED
        recommendation.implementation_notes = reason
        recommendation.save(update_fields=[
            "status", "implementation_notes", "updated_at",
        ])

        return Response({
            "detail": "Recommendation rejected.",
            "recommendation_id": str(recommendation.id),
            "status": recommendation.status,
        })


class ContractParsingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing contract parsing results with parse_document action.
    """

    serializer_class = ContractParsingSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "model_version", "document"]
    search_fields = ["document__file_name", "raw_text"]
    ordering_fields = ["created_at", "processing_time_ms", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return ContractParsing.objects.filter(
            document__contract__organization=self.request.user.organization,
            is_deleted=False,
        ).select_related("document", "document__contract")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=False, methods=["post"])
    def parse_document(self, request):
        """Initiate AI parsing of a contract document."""
        document_id = request.data.get("document_id")

        if not document_id:
            return Response(
                {"detail": "document_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.contracts.models import ContractDocument

        try:
            document = ContractDocument.objects.get(
                id=document_id,
                contract__organization=request.user.organization,
            )
        except ContractDocument.DoesNotExist:
            return Response(
                {"detail": "Document not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Create parsing record
        parsing = ContractParsing.objects.create(
            document=document,
            status=ContractParsing.StatusChoices.PENDING,
            created_by=request.user,
        )

        # In production, this would trigger an async parsing task
        return Response({
            "detail": "Document parsing initiated.",
            "parsing_id": str(parsing.id),
            "document_id": str(document.id),
            "file_name": document.file_name,
            "status": "pending",
        }, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        """Mark a parsing result as reviewed with optional corrections."""
        parsing = self.get_object()
        corrections = request.data.get("corrections", {})

        parsing.reviewed_by = request.user
        parsing.reviewed_at = timezone.now()
        if corrections:
            parsing.corrections = corrections
        parsing.status = ContractParsing.StatusChoices.COMPLETED
        parsing.save(update_fields=[
            "reviewed_by", "reviewed_at", "corrections", "status", "updated_at",
        ])

        return Response({
            "detail": "Parsing reviewed successfully.",
            "parsing_id": str(parsing.id),
        })
