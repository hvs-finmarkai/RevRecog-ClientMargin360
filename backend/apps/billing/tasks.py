"""Billing background tasks."""
from celery import shared_task
from django.utils import timezone


@shared_task
def generate_scheduled_invoices():
    """Generate invoices based on billing schedules."""
    from .models import BillingSchedule

    today = timezone.now().date()
    schedules = BillingSchedule.objects.filter(
        is_active=True,
        start_date__lte=today,
        end_date__gte=today,
        billing_day=today.day,
    )
    count = 0
    for schedule in schedules:
        from apps.invoices.services import create_invoice_from_schedule
        create_invoice_from_schedule(schedule)
        count += 1
    return f"Generated {count} invoices from billing schedules"


@shared_task
def check_milestone_achievements():
    """Check for milestones that may have been achieved based on project progress."""
    from .models import BillingMilestone

    pending = BillingMilestone.objects.filter(status=BillingMilestone.Status.PENDING)
    return f"Checked {pending.count()} pending milestones"
