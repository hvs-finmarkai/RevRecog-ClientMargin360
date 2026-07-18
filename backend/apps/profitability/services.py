"""Profitability business logic services."""
from decimal import Decimal
from django.db.models import Sum


def get_client_profitability(client_id):
    """Get profitability summary for a specific client."""
    from .models import ClientProfitability

    latest = ClientProfitability.objects.filter(client_id=client_id).first()
    if not latest:
        return {
            "client_id": client_id,
            "revenue": 0,
            "gross_margin": 0,
            "gross_margin_pct": 0,
            "health_score": 0,
            "trend": "stable",
        }

    return {
        "client_id": client_id,
        "period": latest.period,
        "revenue": float(latest.revenue),
        "direct_costs": float(latest.direct_costs),
        "indirect_costs": float(latest.indirect_costs),
        "gross_margin": float(latest.gross_margin),
        "gross_margin_pct": float(latest.gross_margin_pct),
        "net_margin": float(latest.net_margin),
        "net_margin_pct": float(latest.net_margin_pct),
        "health_score": latest.health_score,
        "trend": latest.trend,
    }


def calculate_client_profitability(client_id):
    """Calculate and store client profitability for the current period."""
    from django.utils import timezone
    from apps.recognition.models import RevenueRecognitionEvent
    from .models import ClientProfitability, CostEntry

    period = timezone.now().strftime("%Y-%m")

    # Get recognized revenue for the period
    revenue = RevenueRecognitionEvent.objects.filter(
        contract__client_id=client_id,
        status="recognized",
        period=period,
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

    # Get costs for the period
    costs = CostEntry.objects.filter(
        client_id=client_id,
        period=period,
    )
    direct_costs = costs.filter(cost_type__in=["labor", "technology"]).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")
    indirect_costs = costs.filter(cost_type__in=["overhead", "infrastructure"]).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")

    gross_margin = revenue - direct_costs
    gross_margin_pct = (gross_margin / revenue * 100) if revenue > 0 else Decimal("0")
    net_margin = revenue - direct_costs - indirect_costs
    net_margin_pct = (net_margin / revenue * 100) if revenue > 0 else Decimal("0")

    # Determine trend
    previous_period_record = ClientProfitability.objects.filter(
        client_id=client_id
    ).exclude(period=period).first()

    if previous_period_record:
        if gross_margin_pct > previous_period_record.gross_margin_pct + 2:
            trend = "improving"
        elif gross_margin_pct < previous_period_record.gross_margin_pct - 2:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"

    # Health score (0-100)
    health_score = min(100, max(0, int(gross_margin_pct * 2)))

    ClientProfitability.objects.update_or_create(
        client_id=client_id, period=period,
        defaults={
            "revenue": revenue,
            "direct_costs": direct_costs,
            "indirect_costs": indirect_costs,
            "gross_margin": gross_margin,
            "gross_margin_pct": gross_margin_pct,
            "net_margin": net_margin,
            "net_margin_pct": net_margin_pct,
            "health_score": health_score,
            "trend": trend,
        }
    )
