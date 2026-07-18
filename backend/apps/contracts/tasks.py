"""Contract background tasks."""
from celery import shared_task
from django.utils import timezone


@shared_task
def check_expiring_contracts(days_threshold=30):
    """Identify contracts expiring within the threshold and notify stakeholders."""
    from .models import Contract

    expiry_date = timezone.now().date() + timezone.timedelta(days=days_threshold)
    expiring = Contract.objects.filter(
        status=Contract.Status.ACTIVE,
        end_date__lte=expiry_date,
        end_date__gte=timezone.now().date(),
    )
    contract_ids = list(expiring.values_list("id", flat=True))
    return f"Found {len(contract_ids)} contracts expiring within {days_threshold} days"


@shared_task
def parse_contract_document(contract_id):
    """AI-powered contract document parsing to extract performance obligations."""
    from .models import Contract

    contract = Contract.objects.get(id=contract_id)
    if not contract.document:
        return "No document attached to contract"

    # AI parsing logic handled by ai_engine app
    from apps.ai_engine.tasks import process_contract_nlp
    process_contract_nlp.delay(contract_id)
    return f"Contract {contract.contract_number} queued for NLP processing"
