"""Revenue leakage detection tasks."""
from celery import shared_task
from django.utils import timezone
import time


@shared_task
def run_leakage_detection(triggered_by_id=None):
    """Run full leakage detection analysis across all active contracts."""
    from apps.contracts.models import Contract
    from .models import LeakageAlert, LeakageDetectionRun

    start_time = time.time()
    contracts = Contract.objects.filter(status="active")
    alerts_generated = 0
    total_leakage = 0

    for contract in contracts:
        # Run detection algorithms
        alerts = detect_leakage_for_contract(contract)
        alerts_generated += len(alerts)
        total_leakage += sum(a.estimated_leakage_amount for a in alerts)

    duration = time.time() - start_time
    user_id = triggered_by_id

    LeakageDetectionRun.objects.create(
        contracts_analyzed=contracts.count(),
        alerts_generated=alerts_generated,
        total_leakage_detected=total_leakage,
        duration_seconds=duration,
        triggered_by_id=user_id,
    )

    return f"Detection complete: {alerts_generated} alerts, ${total_leakage} leakage detected"


def detect_leakage_for_contract(contract):
    """Run leakage detection algorithms for a single contract."""
    from .models import LeakageAlert

    alerts = []
    # Check for unbilled work, scope creep, rate erosion, etc.
    # AI-powered analysis via apps.ai_engine
    return alerts
