"""
Profitability app views - MarginCalculationViewSet, CostAllocationViewSet,
ProfitabilitySnapshotViewSet with actions: calculate, benchmark, forecast.
"""

from django.db.models import Avg, Count, Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    BenchmarkData,
    CostAllocation,
    MarginCalculation,
    OverheadAllocation,
    ProfitabilitySnapshot,
)
from .serializers import (
    BenchmarkDataSerializer,
    CostAllocationSerializer,
    MarginCalculationSerializer,
    OverheadAllocationSerializer,
    ProfitabilitySnapshotSerializer,
)


class MarginCalculationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing margin calculations with calculate action.
    """

    serializer_class = MarginCalculationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["client", "contract", "status"]
    search_fields = ["client__name", "contract__contract_number", "notes"]
    ordering_fields = [
        "period_start", "period_end", "gross_margin_pct",
        "net_margin_pct", "revenue",
    ]
    ordering = ["-period_start"]

    def get_queryset(self):
        return MarginCalculation.objects.filter(
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
    def calculate(self, request):
        """Trigger margin calculation for a client/contract and period."""
        client_id = request.data.get("client_id")
        contract_id = request.data.get("contract_id")
        period_start = request.data.get("period_start")
        period_end = request.data.get("period_end")

        if not client_id or not period_start or not period_end:
            return Response(
                {"detail": "client_id, period_start, and period_end are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # In production, this would trigger actual calculation from cost allocations
        return Response({
            "detail": "Margin calculation initiated.",
            "client_id": client_id,
            "contract_id": contract_id,
            "period_start": period_start,
            "period_end": period_end,
            "status": "processing",
        })

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get margin summary across all clients."""
        org = request.user.organization
        margins = MarginCalculation.objects.filter(
            client__organization=org,
            is_deleted=False,
        )

        by_status = margins.values("status").annotate(
            count=Count("id"),
            avg_margin=Avg("net_margin_pct"),
        )

        overall = margins.aggregate(
            avg_gross_margin=Avg("gross_margin_pct"),
            avg_net_margin=Avg("net_margin_pct"),
            total_revenue=Sum("revenue"),
            total_cost=Sum("direct_costs"),
        )

        return Response({
            "overall": overall,
            "by_status": list(by_status),
        })


class CostAllocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing cost allocations.
    """

    serializer_class = CostAllocationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["client", "contract"]
    search_fields = ["client__name", "contract__contract_number", "notes"]
    ordering_fields = ["period_start", "total_cost", "headcount"]
    ordering = ["-period_start"]

    def get_queryset(self):
        return CostAllocation.objects.filter(
            client__organization=self.request.user.organization,
            is_deleted=False,
        ).select_related("client", "contract")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()


class ProfitabilitySnapshotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for profitability snapshots with benchmark and forecast actions.
    """

    serializer_class = ProfitabilitySnapshotSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["client", "trend_direction"]
    search_fields = ["client__name"]
    ordering_fields = [
        "snapshot_date", "trailing_12m_revenue",
        "trailing_12m_margin_pct", "rank",
    ]
    ordering = ["-snapshot_date", "rank"]

    def get_queryset(self):
        return ProfitabilitySnapshot.objects.filter(
            client__organization=self.request.user.organization,
            is_deleted=False,
        ).select_related("client")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=False, methods=["post"])
    def calculate(self, request):
        """Trigger profitability snapshot calculation for all clients."""
        return Response({
            "detail": "Profitability snapshot calculation initiated for all active clients.",
            "status": "processing",
            "initiated_at": timezone.now().isoformat(),
        })

    @action(detail=False, methods=["get"])
    def benchmark(self, request):
        """Get benchmark comparison data for the organization."""
        org = request.user.organization
        billing_model = request.query_params.get("billing_model")
        industry = request.query_params.get("industry")

        benchmarks = BenchmarkData.objects.filter(
            is_deleted=False,
        ).filter(
            organization=org,
        ) | BenchmarkData.objects.filter(
            is_deleted=False,
            organization__isnull=True,
        )

        if billing_model:
            benchmarks = benchmarks.filter(billing_model=billing_model)
        if industry:
            benchmarks = benchmarks.filter(industry=industry)

        benchmarks = benchmarks.order_by("-period")[:12]
        serializer = BenchmarkDataSerializer(benchmarks, many=True)

        # Include org averages for comparison
        org_avg = MarginCalculation.objects.filter(
            client__organization=org,
            is_deleted=False,
        ).aggregate(
            avg_gross_margin=Avg("gross_margin_pct"),
            avg_net_margin=Avg("net_margin_pct"),
        )

        return Response({
            "benchmarks": serializer.data,
            "organization_averages": org_avg,
        })

    @action(detail=False, methods=["get"])
    def forecast(self, request):
        """Get profitability forecast based on trends."""
        org = request.user.organization
        months_ahead = int(request.query_params.get("months", 6))

        # Get latest snapshots for trending
        latest_snapshots = ProfitabilitySnapshot.objects.filter(
            client__organization=org,
            is_deleted=False,
        ).order_by("-snapshot_date")[:20]

        avg_margin = latest_snapshots.aggregate(
            avg=Avg("trailing_12m_margin_pct")
        )["avg"] or 0

        return Response({
            "forecast_months": months_ahead,
            "current_avg_margin": str(avg_margin),
            "trend_clients_improving": latest_snapshots.filter(
                trend_direction="improving"
            ).count(),
            "trend_clients_declining": latest_snapshots.filter(
                trend_direction="declining"
            ).count(),
            "trend_clients_stable": latest_snapshots.filter(
                trend_direction="stable"
            ).count(),
        })
