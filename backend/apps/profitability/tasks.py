import logging
from decimal import Decimal

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, F

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def calculate_client_margins(self, organization_id, period):
    try:
        from apps.profitability.models import ClientMargin
        from apps.profitability.services.calculator import MarginCalculator
        from apps.contracts.models import Contract

        calculator = MarginCalculator()
        period_start, period_end = calculator.parse_period(period)

        active_clients = Contract.objects.filter(
            organization_id=organization_id,
            status="active",
        ).values_list("client_id", flat=True).distinct()

        results = []
        for client_id in active_clients:
            revenue = calculator.get_client_revenue(
                client_id=client_id,
                period_start=period_start,
                period_end=period_end,
            )

            direct_costs = calculator.get_direct_costs(
                client_id=client_id,
                period_start=period_start,
                period_end=period_end,
            )

            overhead_allocation = calculator.allocate_overhead(
                client_id=client_id,
                organization_id=organization_id,
                period_start=period_start,
                period_end=period_end,
            )

            gross_margin = revenue - direct_costs
            net_margin = gross_margin - overhead_allocation
            gross_margin_pct = (gross_margin / revenue * 100) if revenue > 0 else Decimal("0")
            net_margin_pct = (net_margin / revenue * 100) if revenue > 0 else Decimal("0")

            with transaction.atomic():
                margin, created = ClientMargin.objects.update_or_create(
                    organization_id=organization_id,
                    client_id=client_id,
                    period_start=period_start,
                    period_end=period_end,
                    defaults={
                        "revenue": revenue,
                        "direct_costs": direct_costs,
                        "overhead_allocation": overhead_allocation,
                        "gross_margin": gross_margin,
                        "gross_margin_percentage": gross_margin_pct,
                        "net_margin": net_margin,
                        "net_margin_percentage": net_margin_pct,
                        "calculated_at": timezone.now(),
                    },
                )

            results.append({
                "client_id": str(client_id),
                "revenue": str(revenue),
                "gross_margin_pct": str(gross_margin_pct),
                "net_margin_pct": str(net_margin_pct),
            })

        return {
            "status": "completed",
            "organization_id": str(organization_id),
            "period": period,
            "clients_calculated": len(results),
            "results": results,
        }

    except Exception as exc:
        logger.exception(f"Error calculating margins for org {organization_id}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {"status": "failed", "reason": str(exc)}


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def generate_profitability_snapshot(self, organization_id):
    try:
        from apps.profitability.models import ProfitabilitySnapshot, ClientMargin
        from apps.profitability.services.calculator import MarginCalculator

        calculator = MarginCalculator()
        now = timezone.now()
        period_start, period_end = calculator.get_current_period(now)

        margins = ClientMargin.objects.filter(
            organization_id=organization_id,
            period_start=period_start,
            period_end=period_end,
        )

        if not margins.exists():
            calculate_client_margins(organization_id, f"{period_start.isoformat()}/{period_end.isoformat()}")
            margins = ClientMargin.objects.filter(
                organization_id=organization_id,
                period_start=period_start,
                period_end=period_end,
            )

        aggregated = margins.aggregate(
            total_revenue=Sum("revenue"),
            total_direct_costs=Sum("direct_costs"),
            total_overhead=Sum("overhead_allocation"),
            total_gross_margin=Sum("gross_margin"),
            total_net_margin=Sum("net_margin"),
        )

        total_revenue = aggregated["total_revenue"] or Decimal("0")
        avg_gross_margin_pct = (
            (aggregated["total_gross_margin"] / total_revenue * 100)
            if total_revenue > 0
            else Decimal("0")
        )
        avg_net_margin_pct = (
            (aggregated["total_net_margin"] / total_revenue * 100)
            if total_revenue > 0
            else Decimal("0")
        )

        top_clients = margins.order_by("-net_margin_percentage")[:5]
        bottom_clients = margins.order_by("net_margin_percentage")[:5]
        at_risk_clients = margins.filter(net_margin_percentage__lt=Decimal("10"))

        snapshot = ProfitabilitySnapshot.objects.create(
            organization_id=organization_id,
            period_start=period_start,
            period_end=period_end,
            total_revenue=total_revenue,
            total_direct_costs=aggregated["total_direct_costs"] or Decimal("0"),
            total_overhead=aggregated["total_overhead"] or Decimal("0"),
            total_gross_margin=aggregated["total_gross_margin"] or Decimal("0"),
            total_net_margin=aggregated["total_net_margin"] or Decimal("0"),
            avg_gross_margin_percentage=avg_gross_margin_pct,
            avg_net_margin_percentage=avg_net_margin_pct,
            total_clients=margins.count(),
            at_risk_clients_count=at_risk_clients.count(),
            top_clients=[
                {"client_id": str(m.client_id), "margin_pct": str(m.net_margin_percentage)}
                for m in top_clients
            ],
            bottom_clients=[
                {"client_id": str(m.client_id), "margin_pct": str(m.net_margin_percentage)}
                for m in bottom_clients
            ],
            snapshot_date=now,
        )

        return {
            "status": "completed",
            "snapshot_id": str(snapshot.id),
            "total_revenue": str(total_revenue),
            "avg_net_margin_pct": str(avg_net_margin_pct),
            "clients_count": margins.count(),
            "at_risk_count": at_risk_clients.count(),
        }

    except Exception as exc:
        logger.exception(f"Error generating profitability snapshot for org {organization_id}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {"status": "failed", "reason": str(exc)}


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=300,
)
def run_benchmark_analysis(self, organization_id):
    try:
        from apps.profitability.models import BenchmarkResult, ProfitabilitySnapshot, ClientMargin
        from apps.profitability.services.benchmark import BenchmarkAnalyzer

        analyzer = BenchmarkAnalyzer()
        now = timezone.now()

        latest_snapshot = ProfitabilitySnapshot.objects.filter(
            organization_id=organization_id,
        ).order_by("-snapshot_date").first()

        if not latest_snapshot:
            generate_profitability_snapshot(organization_id)
            latest_snapshot = ProfitabilitySnapshot.objects.filter(
                organization_id=organization_id,
            ).order_by("-snapshot_date").first()

        margins = ClientMargin.objects.filter(
            organization_id=organization_id,
            period_start=latest_snapshot.period_start,
            period_end=latest_snapshot.period_end,
        )

        org_benchmarks = analyzer.calculate_org_benchmarks(margins)
        industry_benchmarks = analyzer.get_industry_benchmarks()

        client_benchmarks = []
        for margin in margins:
            client_benchmark = analyzer.benchmark_client(
                margin=margin,
                org_benchmarks=org_benchmarks,
                industry_benchmarks=industry_benchmarks,
            )
            client_benchmarks.append(client_benchmark)

        with transaction.atomic():
            BenchmarkResult.objects.filter(
                organization_id=organization_id,
            ).update(is_current=False)

            benchmark = BenchmarkResult.objects.create(
                organization_id=organization_id,
                snapshot=latest_snapshot,
                org_benchmarks=org_benchmarks,
                industry_benchmarks=industry_benchmarks,
                client_benchmarks=client_benchmarks,
                is_current=True,
                generated_at=now,
            )

        return {
            "status": "completed",
            "benchmark_id": str(benchmark.id),
            "clients_benchmarked": len(client_benchmarks),
            "org_avg_margin": str(org_benchmarks.get("avg_net_margin_pct", 0)),
        }

    except Exception as exc:
        logger.exception(f"Error running benchmark for org {organization_id}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {"status": "failed", "reason": str(exc)}
