"""Invoice business logic services."""
from django.utils import timezone


def create_invoice_from_schedule(schedule):
    """Create an invoice based on a billing schedule."""
    from .models import Invoice, InvoiceLineItem

    contract = schedule.contract
    client = contract.client
    today = timezone.now().date()

    # Generate invoice number
    count = Invoice.objects.filter(issue_date__year=today.year).count() + 1
    invoice_number = f"INV-{today.year}-{count:05d}"

    invoice = Invoice.objects.create(
        invoice_number=invoice_number,
        contract=contract,
        client=client,
        issue_date=today,
        due_date=today + timezone.timedelta(days=client.payment_terms_days),
        subtotal=schedule.amount,
        tax_amount=0,
        total_amount=schedule.amount,
        currency=contract.currency,
        payment_terms=f"Net {client.payment_terms_days}",
    )

    InvoiceLineItem.objects.create(
        invoice=invoice,
        description=f"{contract.title} - {schedule.frequency} billing",
        quantity=1,
        unit_price=schedule.amount,
        amount=schedule.amount,
    )

    return invoice
