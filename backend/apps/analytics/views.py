"""
Analytics app views - AnalyticsViewSet with actions: overview, revenue_trend, margin_summary.
"""

from django.db.models import Avg, Count, Sum
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import AnalyticsEvent, MetricSnapshot
from .serializers import AnalyticsEventSerializer, MetricSnapshotSerializer


class AnalyticsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for analytics with overview, revenue_trend, and margin_summary actions.
    """

    serializer_class = MetricSnapshotSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["metric_name", "metric_category", "period_type"]
    search_fields = ["metric_name"]
    ordering_fields = ["period_start", "metric_value", "metric_name"]
    ordering = ["-period_start"]

    def get_queryset(self):
        return MetricSnapshot.objects.filter(
            organization=self.request.user.organization,
            is_deleted=False,
        )

    def get_serializer_class(self):
        if self.action in ["overview", "revenue_trend", "margin_summary"]:
            return MetricSnapshotSerializer
        return MetricSnapshotSerializer

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=False, methods=["get"])
    def overview(self, request):
        """Get a high-level analytics overview for the organization."""
        org = request.user.organization

        # Get latest snapshots for key metrics
        key_metrics = [
            "total_revenue", "total_receivables", "avg_margin_pct",
            "active_contracts", "active_clients", "leakage_amount",
        ]

        metrics = {}
        for metric_name in key_metrics:
            latest = MetricSnapshot.objects.filter(
                organization=org,
                metric_name=metric_name,
                is_deleted=False,
            ).order_by("-period_start").first()

            if latest:
                metrics[metric_name] = {
                    "value": str(latest.metric_value),
                    "change_pct": str(latest.change_pct) if latest.change_pct else None,
                    "trend": latest.trend_direction,
                    "period": str(latest.period_start),
                }
            else:
                metrics[metric_name] = None

        # Recent events count
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        events_count = AnalyticsEvent.objects.filter(
            organization=org,
            created_at__gte=thirty_days_ago,
        ).count()

        return Response({
            "organization": str(org.name),
            "metrics": metrics,
            "events_last_30_days": events_count,
            "generated_at": timezone.now().isoformat(),
        })

    @action(detail=False, methods=["get"])
    def revenue_trend(self, request):
        """Get revenue trend data over time."""
        org = request.user.organization
        period_type = request.query_params.get("period_type", "monthly")
        months = int(request.query_params.get("months", 12))

        from datetime import timedelta
        start_date = timezone.now() - timedelta(days=months * 30)

        revenue_metrics = MetricSnapshot.objects.filter(
            organization=org,
            metric_name="total_revenue",
            period_type=period_type,
            period_start__gte=start_date,
            is_deleted=False,
        ).order_by("period_start")

        data_points = [
            {
                "period": str(m.period_start),
                "value": str(m.metric_value),
                "change_pct": str(m.change_pct) if m.change_pct else None,
            }
            for m in revenue_metrics
        ]

        # Calculate totals
        total = revenue_metrics.aggregate(total=Sum("metric_value"))["total"] or 0
        avg = revenue_metrics.aggregate(avg=Avg("metric_value"))["avg"] or 0

        return Response({
            "period_type": period_type,
            "months": months,
            "data_points": data_points,
            "total_revenue": str(total),
            "average_revenue": str(avg),
            "data_count": len(data_points),
        })

    @action(detail=False, methods=["get"])
    def margin_summary(self, request):
        """Get margin summary analytics."""
        org = request.user.organization
        period_type = request.query_params.get("period_type", "monthly")

        from datetime import timedelta
        six_months_ago = timezone.now() - timedelta(days=180)

        margin_metrics = MetricSnapshot.objects.filter(
            organization=org,
            metric_name="avg_margin_pct",
            period_type=period_type,
            period_start__gte=six_months_ago,
            is_deleted=False,
        ).order_by("period_start")

        data_points = [
            {
                "period": str(m.period_start),
                "value": str(m.metric_value),
                "change_pct": str(m.change_pct) if m.change_pct else None,
                "dimensions": m.dimensions,
            }
            for m in margin_metrics
        ]

        current_avg = margin_metrics.aggregate(
            avg=Avg("metric_value")
        )["avg"] or 0

        return Response({
            "period_type": period_type,
            "current_average_margin": str(current_avg),
            "data_points": data_points,
            "data_count": len(data_points),
        })

    @action(detail=False, methods=["get"])
    def events(self, request):
        """List recent analytics events."""
        org = request.user.organization
        event_type = request.query_params.get("event_type")
        category = request.query_params.get("category")
        limit = int(request.query_params.get("limit", 50))

        events = AnalyticsEvent.objects.filter(
            organization=org,
        ).order_by("-created_at")

        if event_type:
            events = events.filter(event_type=event_type)
        if category:
            events = events.filter(event_category=category)

        events = events[:limit]
        serializer = AnalyticsEventSerializer(events, many=True)
        return Response(serializer.data)
