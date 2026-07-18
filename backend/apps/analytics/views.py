from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Count, Sum, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.collections_mgmt.models import Receivable
from apps.contracts.models import Contract
from apps.clients.models import Client
from apps.invoices.models import Invoice
from apps.leakage.models import LeakageDetection
from apps.profitability.models import MarginCalculation
from apps.recognition.models import RevenueEntry

from .models import AnalyticsEvent, MetricSnapshot
from .serializers import AnalyticsEventSerializer, MetricSnapshotSerializer


class AnalyticsViewSet(viewsets.ModelViewSet):
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
        org = request.user.organization
        today = timezone.now().date()
        month_start = today.replace(day=1)

        total_contract_value = Contract.objects.filter(
            organization=org,
            status="active",
            is_deleted=False,
        ).aggregate(total=Sum("total_value"))["total"] or Decimal("0.00")

        monthly_revenue = RevenueEntry.objects.filter(
            schedule__contract__organization=org,
            period_start__gte=month_start,
            period_end__lte=today,
            status="posted",
            is_deleted=False,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        revenue_leakage = LeakageDetection.objects.filter(
            organization=org,
            status__in=["open", "acknowledged", "in_progress"],
            is_deleted=False,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        overdue_receivables = Receivable.objects.filter(
            invoice__organization=org,
            status__in=["overdue_30", "overdue_60", "overdue_90", "overdue_90_plus"],
            is_deleted=False,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        active_clients = Client.objects.filter(
            organization=org,
            status="active",
            is_deleted=False,
        ).count()

        active_contracts = Contract.objects.filter(
            organization=org,
            status="active",
            is_deleted=False,
        ).count()

        return Response({
            "total_contract_value": str(total_contract_value),
            "monthly_revenue": str(monthly_revenue),
            "revenue_leakage": str(revenue_leakage),
            "overdue_receivables": str(overdue_receivables),
            "active_clients": active_clients,
            "active_contracts": active_contracts,
            "generated_at": timezone.now().isoformat(),
        })

    @action(detail=False, methods=["get"])
    def revenue_trend(self, request):
        org = request.user.organization
        six_months_ago = timezone.now().date() - timedelta(days=180)

        entries = (
            RevenueEntry.objects.filter(
                schedule__contract__organization=org,
                status="posted",
                period_start__gte=six_months_ago,
                is_deleted=False,
            )
            .annotate(month=TruncMonth("period_start"))
            .values("month")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("month")
        )

        data_points = [
            {
                "month": entry["month"].strftime("%Y-%m"),
                "revenue": str(entry["total"]),
                "entry_count": entry["count"],
            }
            for entry in entries
        ]

        total_revenue = sum(entry["total"] for entry in entries) if entries else Decimal("0.00")

        return Response({
            "period": "last_6_months",
            "data_points": data_points,
            "total_revenue": str(total_revenue),
            "months_count": len(data_points),
        })

    @action(detail=False, methods=["get"])
    def margin_summary(self, request):
        org = request.user.organization

        margins = (
            MarginCalculation.objects.filter(
                client__organization=org,
                is_deleted=False,
            )
            .values("client__id", "client__name")
            .annotate(
                avg_gross_margin_pct=Avg("gross_margin_pct"),
                avg_net_margin_pct=Avg("net_margin_pct"),
                total_revenue=Sum("revenue"),
                total_direct_costs=Sum("direct_costs"),
            )
            .order_by("-avg_net_margin_pct")
        )

        client_margins = [
            {
                "client_id": str(m["client__id"]),
                "client_name": m["client__name"],
                "avg_gross_margin_pct": str(round(m["avg_gross_margin_pct"], 2)),
                "avg_net_margin_pct": str(round(m["avg_net_margin_pct"], 2)),
                "total_revenue": str(m["total_revenue"]),
                "total_direct_costs": str(m["total_direct_costs"]),
            }
            for m in margins
        ]

        overall_avg = MarginCalculation.objects.filter(
            client__organization=org,
            is_deleted=False,
        ).aggregate(
            avg_gross=Avg("gross_margin_pct"),
            avg_net=Avg("net_margin_pct"),
        )

        return Response({
            "client_margins": client_margins,
            "overall_avg_gross_margin_pct": str(round(overall_avg["avg_gross"] or 0, 2)),
            "overall_avg_net_margin_pct": str(round(overall_avg["avg_net"] or 0, 2)),
            "client_count": len(client_margins),
        })

    @action(detail=False, methods=["get"])
    def leakage_summary(self, request):
        org = request.user.organization

        total_leakage = LeakageDetection.objects.filter(
            organization=org,
            is_deleted=False,
        ).aggregate(
            total_amount=Sum("amount"),
            open_count=Count("id", filter=Q(status="open")),
            resolved_count=Count("id", filter=Q(status="resolved")),
            total_count=Count("id"),
        )

        by_type = (
            LeakageDetection.objects.filter(
                organization=org,
                is_deleted=False,
            )
            .values("detection_type")
            .annotate(count=Count("id"), total=Sum("amount"))
            .order_by("-total")
        )

        by_severity = (
            LeakageDetection.objects.filter(
                organization=org,
                status__in=["open", "acknowledged", "in_progress"],
                is_deleted=False,
            )
            .values("severity")
            .annotate(count=Count("id"), total=Sum("amount"))
            .order_by("-total")
        )

        return Response({
            "total_leakage_amount": str(total_leakage["total_amount"] or 0),
            "open_count": total_leakage["open_count"],
            "resolved_count": total_leakage["resolved_count"],
            "total_count": total_leakage["total_count"],
            "by_type": [
                {
                    "detection_type": item["detection_type"],
                    "count": item["count"],
                    "total_amount": str(item["total"]),
                }
                for item in by_type
            ],
            "by_severity": [
                {
                    "severity": item["severity"],
                    "count": item["count"],
                    "total_amount": str(item["total"]),
                }
                for item in by_severity
            ],
        })

    @action(detail=False, methods=["get"])
    def events(self, request):
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
