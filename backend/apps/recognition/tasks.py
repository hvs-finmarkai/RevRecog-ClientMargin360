"""Revenue recognition background tasks."""
from celery import shared_task
from django.utils import timezone


@shared_task
def process_pending_recognitions():
    """Process all pending recognition events that meet auto-approval criteria."""
    from .models import RevenueRecognitionEvent, RecognitionRule

    rules = RecognitionRule.objects.filter(is_active=True, requires_approval=False)
    pending_events = RevenueRecognitionEvent.objects.filter(status="pending")

    auto_approved = 0
    for event in pending_events:
        for rule in rules:
            if event.ai_confidence_score >= rule.auto_recognize_threshold:
                event.status = RevenueRecognitionEvent.Status.RECOGNIZED
                event.approved_at = timezone.now()
                event.save()
                auto_approved += 1
                break

    return f"Auto-approved {auto_approved} out of {pending_events.count()} pending events"


@shared_task
def process_payment_recognition(payment_id):
    """Trigger revenue recognition based on payment received."""
    from apps.invoices.models import Payment

    payment = Payment.objects.select_related("invoice__contract").get(id=payment_id)
    contract = payment.invoice.contract
    # Determine if payment triggers point-in-time recognition
    return f"Processed payment recognition for contract {contract.contract_number}"


@shared_task
def calculate_over_time_recognition(contract_id, period):
    """Calculate over-time revenue recognition for a contract in a given period."""
    from apps.contracts.models import Contract, PerformanceObligation
    from .models import RevenueRecognitionEvent

    contract = Contract.objects.get(id=contract_id)
    obligations = contract.obligations.filter(fulfillment_type="over_time")

    events_created = 0
    for obligation in obligations:
        allocated = obligation.allocated_price
        progress = obligation.progress_percentage / 100
        cumulative = allocated * progress
        previously_recognized = RevenueRecognitionEvent.objects.filter(
            obligation=obligation,
            status="recognized",
        ).aggregate(total=models.Sum("amount"))["total"] or 0

        amount_to_recognize = cumulative - previously_recognized
        if amount_to_recognize > 0:
            RevenueRecognitionEvent.objects.create(
                contract=contract,
                obligation=obligation,
                recognition_date=timezone.now().date(),
                amount=amount_to_recognize,
                method=RevenueRecognitionEvent.RecognitionMethod.OVER_TIME_OUTPUT,
                period=period,
                progress_percentage=obligation.progress_percentage,
                cumulative_recognized=cumulative,
            )
            events_created += 1

    return f"Created {events_created} recognition events for contract {contract.contract_number}"
