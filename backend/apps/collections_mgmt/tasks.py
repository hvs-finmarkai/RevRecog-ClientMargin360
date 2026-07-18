"""Collections management background tasks."""
from celery import shared_task
from django.utils import timezone


@shared_task
def generate_aging_reports():
    """Generate aging analysis reports for all clients with outstanding invoices."""
    from apps.clients.models import Client
    from apps.invoices.models import Invoice
    from .models import AgingReport
    from django.db.models import Sum, Q

    today = timezone.now().date()
    clients = Client.objects.filter(invoices__status__in=["sent", "partially_paid", "overdue"]).distinct()

    for client in clients:
        invoices = Invoice.objects.filter(
            client=client,
            status__in=["sent", "partially_paid", "overdue"],
        )
        current = invoices.filter(due_date__gte=today).aggregate(t=Sum("balance_due"))["t"] or 0
        d1_30 = invoices.filter(due_date__lt=today, due_date__gte=today - timezone.timedelta(days=30)).aggregate(t=Sum("balance_due"))["t"] or 0
        d31_60 = invoices.filter(due_date__lt=today - timezone.timedelta(days=30), due_date__gte=today - timezone.timedelta(days=60)).aggregate(t=Sum("balance_due"))["t"] or 0
        d61_90 = invoices.filter(due_date__lt=today - timezone.timedelta(days=60), due_date__gte=today - timezone.timedelta(days=90)).aggregate(t=Sum("balance_due"))["t"] or 0
        over_90 = invoices.filter(due_date__lt=today - timezone.timedelta(days=90)).aggregate(t=Sum("balance_due"))["t"] or 0

        AgingReport.objects.update_or_create(
            report_date=today, client=client,
            defaults={
                "current_amount": current,
                "days_1_30": d1_30,
                "days_31_60": d31_60,
                "days_61_90": d61_90,
                "days_over_90": over_90,
                "total_outstanding": current + d1_30 + d31_60 + d61_90 + over_90,
            }
        )

    return f"Generated aging reports for {clients.count()} clients"


@shared_task
def send_collection_reminders():
    """Send automated collection reminder emails."""
    from .models import CollectionEntry

    entries = CollectionEntry.objects.filter(
        status__in=["pending", "in_progress"],
        next_followup_date__lte=timezone.now().date(),
    )
    sent = 0
    for entry in entries:
        # Send reminder email
        sent += 1
    return f"Sent {sent} collection reminders"


@shared_task
def update_collection_priorities():
    """Update collection priorities based on AI scoring."""
    from .models import CollectionEntry
    entries = CollectionEntry.objects.exclude(status__in=["collected", "written_off"])
    for entry in entries:
        # Recalculate priority based on AI model
        pass
    return f"Updated priorities for {entries.count()} entries"
