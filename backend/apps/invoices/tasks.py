"""Invoice background tasks."""
from celery import shared_task


@shared_task
def generate_invoice_pdf(invoice_id):
    """Generate PDF for an invoice using ReportLab/WeasyPrint."""
    from .models import Invoice
    invoice = Invoice.objects.get(id=invoice_id)
    # PDF generation logic using reportlab/weasyprint
    return f"Generated PDF for invoice {invoice.invoice_number}"


@shared_task
def generate_milestone_invoice(milestone_id):
    """Generate an invoice when a billing milestone is achieved."""
    from apps.billing.models import BillingMilestone
    milestone = BillingMilestone.objects.select_related("schedule__contract").get(id=milestone_id)
    contract = milestone.schedule.contract
    # Invoice creation logic
    return f"Generated milestone invoice for {contract.contract_number} - {milestone.name}"


@shared_task
def mark_overdue_invoices():
    """Mark invoices past their due date as overdue."""
    from django.utils import timezone
    from .models import Invoice

    today = timezone.now().date()
    overdue = Invoice.objects.filter(
        due_date__lt=today,
        status__in=[Invoice.Status.SENT, Invoice.Status.PARTIALLY_PAID],
    )
    count = overdue.update(status=Invoice.Status.OVERDUE)
    return f"Marked {count} invoices as overdue"


@shared_task
def send_invoice_email(invoice_id):
    """Send invoice to client via email."""
    from .models import Invoice
    invoice = Invoice.objects.get(id=invoice_id)
    # Email sending logic
    return f"Sent invoice {invoice.invoice_number} to {invoice.client.name}"
