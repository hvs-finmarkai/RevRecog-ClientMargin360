"""
Clients app views - ClientViewSet with custom actions for
profitability_summary, health_score, contacts, segments.
"""

from django.db.models import Avg, Count, Q, Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Client, ClientAddress, ClientContact, ClientSegment
from .serializers import (
    ClientAddressSerializer,
    ClientContactSerializer,
    ClientCreateSerializer,
    ClientDetailSerializer,
    ClientHealthSerializer,
    ClientListSerializer,
    ClientSegmentSerializer,
)


class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing clients with profitability, health scoring,
    contacts, and segmentation capabilities.
    """

    serializer_class = ClientListSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = [
        "status", "industry", "segment", "payment_terms", "country",
    ]
    search_fields = [
        "name", "legal_name", "email", "contact_person", "gstin", "pan",
    ]
    ordering_fields = [
        "name", "created_at", "health_score", "risk_score", "credit_limit",
    ]
    ordering = ["name"]

    def get_queryset(self):
        return Client.objects.filter(
            organization=self.request.user.organization,
            is_deleted=False,
        ).select_related("segment")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ClientDetailSerializer
        if self.action in ["create", "update", "partial_update"]:
            return ClientCreateSerializer
        if self.action == "contacts":
            return ClientContactSerializer
        if self.action == "health_score":
            return ClientHealthSerializer
        if self.action == "segments":
            return ClientSegmentSerializer
        return ClientListSerializer

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=["get"])
    def profitability_summary(self, request, pk=None):
        """Get profitability summary for a specific client."""
        client = self.get_object()

        from apps.profitability.models import MarginCalculation, ProfitabilitySnapshot

        latest_snapshot = ProfitabilitySnapshot.objects.filter(
            client=client
        ).order_by("-snapshot_date").first()

        recent_margins = MarginCalculation.objects.filter(
            client=client
        ).order_by("-period_start")[:6]

        summary = {
            "client_id": str(client.id),
            "client_name": client.name,
            "trailing_12m_revenue": None,
            "trailing_12m_cost": None,
            "trailing_12m_margin_pct": None,
            "trend_direction": None,
            "active_contracts": client.contracts.filter(status="active").count(),
            "recent_margins": [
                {
                    "period": f"{m.period_start} - {m.period_end}",
                    "revenue": str(m.revenue),
                    "gross_margin_pct": str(m.gross_margin_pct),
                    "net_margin_pct": str(m.net_margin_pct),
                    "status": m.status,
                }
                for m in recent_margins
            ],
        }

        if latest_snapshot:
            summary.update({
                "trailing_12m_revenue": str(latest_snapshot.trailing_12m_revenue),
                "trailing_12m_cost": str(latest_snapshot.trailing_12m_cost),
                "trailing_12m_margin_pct": str(latest_snapshot.trailing_12m_margin_pct),
                "trend_direction": latest_snapshot.trend_direction,
            })

        return Response(summary)

    @action(detail=True, methods=["get"])
    def health_score(self, request, pk=None):
        """Get detailed health score breakdown for a client."""
        client = self.get_object()

        health_data = {
            "client_id": str(client.id),
            "client_name": client.name,
            "overall_health_score": str(client.health_score),
            "risk_score": str(client.risk_score),
            "factors": {
                "payment_timeliness": 0,
                "contract_utilization": 0,
                "relationship_tenure_months": 0,
                "revenue_growth": 0,
                "margin_stability": 0,
            },
            "status": client.status,
            "recommendations": [],
        }

        if client.health_score < 50:
            health_data["recommendations"].append(
                "Client health is deteriorating. Schedule a review meeting."
            )
        if client.risk_score > 70:
            health_data["recommendations"].append(
                "High risk score. Review payment patterns and contract terms."
            )

        return Response(health_data)

    @action(detail=True, methods=["get", "post"])
    def contacts(self, request, pk=None):
        """List or create contacts for a client."""
        client = self.get_object()

        if request.method == "GET":
            contacts = ClientContact.objects.filter(
                client=client, is_deleted=False
            )
            serializer = ClientContactSerializer(contacts, many=True)
            return Response(serializer.data)

        serializer = ClientContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(client=client, created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def segments(self, request):
        """List all client segments with client counts."""
        segments = ClientSegment.objects.filter(is_deleted=False).annotate(
            client_count=Count("clients", filter=Q(clients__is_deleted=False))
        )
        serializer = ClientSegmentSerializer(segments, many=True)
        return Response(serializer.data)
