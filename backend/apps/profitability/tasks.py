"""Profitability background tasks."""
from celery import shared_task


@shared_task
def recalculate_all_margins():
    """Recalculate profitability metrics for all active clients."""
    from apps.clients.models import Client
    from .services import calculate_client_profitability

    clients = Client.objects.filter(status="active")
    updated = 0
    for client in clients:
        calculate_client_profitability(client.id)
        updated += 1
    return f"Recalculated margins for {updated} clients"


@shared_task
def calculate_project_profitability(contract_id, period):
    """Calculate profitability for a specific project/contract."""
    from apps.contracts.models import Contract
    from .models import ProjectProfitability, CostEntry
    from django.db.models import Sum

    contract = Contract.objects.get(id=contract_id)
    costs = CostEntry.objects.filter(contract=contract, period=period).aggregate(
        total=Sum("amount")
    )["total"] or 0

    # Revenue calculation from recognition events
    from apps.recognition.models import RevenueRecognitionEvent
    revenue = RevenueRecognitionEvent.objects.filter(
        contract=contract, period=period, status="recognized"
    ).aggregate(total=Sum("amount"))["total"] or 0

    margin = revenue - costs
    margin_pct = (margin / revenue * 100) if revenue > 0 else 0

    ProjectProfitability.objects.update_or_create(
        contract=contract, period=period,
        defaults={
            "revenue": revenue,
            "total_costs": costs,
            "margin": margin,
            "margin_pct": margin_pct,
            "is_at_risk": margin_pct < 15,
        }
    )
    return f"Calculated profitability for {contract.contract_number} - {period}"
